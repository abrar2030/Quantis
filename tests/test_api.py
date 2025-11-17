import asyncio

import pytest
# from api.endpoints.predict import predict_endpoint # F401: Unused import
from api.middleware.auth import validate_api_key
from fastapi import HTTPException

# import json # F401: Unused import


def test_predict_endpoint_success(test_client, sample_data):
    response = test_client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_predict_endpoint_invalid_data(test_client):
    response = test_client.post(
        "/predict", json={"features": [0.1], "api_key": "test_key"}
    )
    assert response.status_code == 422


def test_predict_endpoint_invalid_api_key(test_client, sample_data):
    invalid_data = sample_data.copy()
    invalid_data["api_key"] = "invalid_key"
    response = test_client.post("/predict", json=invalid_data)
    assert response.status_code == 401


def test_validate_api_key():
    with pytest.raises(HTTPException):
        validate_api_key("invalid_key")


def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_rate_limiting(test_client, sample_data):
    # Make multiple requests in quick succession
    responses = []
    for _ in range(11):  # Assuming rate limit is 10 requests per minute
        response = test_client.post("/predict", json=sample_data)
        responses.append(response)

    # The last request should be rate limited
    assert responses[-1].status_code == 429
    assert "Too many requests" in responses[-1].json()["detail"]


def test_request_timeout(test_client, sample_data):
    # Test with a very large payload that should timeout
    large_data = sample_data.copy()
    large_data["features"] = [0.1] * 1000000  # Very large feature vector

    response = test_client.post("/predict", json=large_data)
    assert response.status_code == 408
    assert "Request timeout" in response.json()["detail"]


def test_malformed_json(test_client):
    # Send malformed JSON
    response = test_client.post(
        "/predict", data="invalid json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["detail"]


@pytest.mark.asyncio
async def test_concurrent_requests(test_client, sample_data):
    # Test multiple concurrent requests
    async def make_request():
        return test_client.post("/predict", json=sample_data)

    # Make 5 concurrent requests
    tasks = [make_request() for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    assert all("prediction" in r.json() for r in responses)


def test_cors_headers(test_client):
    response = test_client.options("/predict")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "Access-Control-Allow-Headers" in response.headers
