from unittest.mock import MagicMock, patch

import pytest
from api.app import app
from api.middleware.auth import validate_api_key
from fastapi import HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def sample_data():
    return {"features": [0.1] * 128, "api_key": "test_key"}


@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("API_SECRET", "test_key")


# Test different input data formats
def test_predict_with_different_feature_lengths(test_client, mock_env_api_key):
    # Test with minimum features
    min_data = {"features": [0.1] * 10, "api_key": "test_key"}
    response = test_client.post("/predict", json=min_data)
    assert response.status_code == 422  # Should fail validation

    # Test with maximum features
    max_data = {"features": [0.1] * 256, "api_key": "test_key"}
    response = test_client.post("/predict", json=max_data)
    assert response.status_code == 422  # Should fail validation

    # Test with correct features
    correct_data = {"features": [0.1] * 128, "api_key": "test_key"}
    response = test_client.post("/predict", json=correct_data)
    assert response.status_code == 200
    assert "prediction" in response.json()


# Test with extreme values
def test_predict_with_extreme_values(test_client, mock_env_api_key):
    # Test with very large values
    large_values = {"features": [1e10] * 128, "api_key": "test_key"}
    response = test_client.post("/predict", json=large_values)
    assert response.status_code == 200

    # Test with very small values
    small_values = {"features": [1e-10] * 128, "api_key": "test_key"}
    response = test_client.post("/predict", json=small_values)
    assert response.status_code == 200

    # Test with mixed positive and negative values
    mixed_values = {
        "features": [-0.5 if i % 2 == 0 else 0.5 for i in range(128)],
        "api_key": "test_key",
    }
    response = test_client.post("/predict", json=mixed_values)
    assert response.status_code == 200


# Test with missing API key in different ways
def test_predict_missing_api_key_variations(test_client):
    # Test with missing API key in JSON
    data_without_key = {"features": [0.1] * 128}
    response = test_client.post("/predict", json=data_without_key)
    assert response.status_code == 422  # Validation error

    # Test with empty API key
    data_empty_key = {"features": [0.1] * 128, "api_key": ""}
    response = test_client.post("/predict", json=data_empty_key)
    assert response.status_code == 403  # Forbidden

    # Test with API key in header but not in JSON
    data_without_key = {"features": [0.1] * 128}
    response = test_client.post(
        "/predict", json=data_without_key, headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code in [401, 403, 422]  # One of these error codes


# Test model loading behavior
@patch("api.endpoints.prediction.joblib.load")
def test_model_loading_behavior(mock_load, test_client, mock_env_api_key, sample_data):
    # Test successful model loading
    mock_model = MagicMock()
    mock_model.predict.return_value = [[0.1, 0.2, 0.3]]
    mock_model.predict_proba.return_value = [[0.2, 0.5, 0.3]]
    mock_load.return_value = mock_model

    response = test_client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "prediction" in response.json()

    # Test model loading failure
    mock_load.side_effect = FileNotFoundError("Model file not found")
    response = test_client.post("/predict", json=sample_data)
    assert response.status_code == 200  # Should still work with dummy model
    assert "prediction" in response.json()


# Test model health endpoint with different scenarios
def test_model_health_detailed(test_client):
    # Basic health check
    response = test_client.get("/model_health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()

    # Test with accept header for different formats
    response = test_client.get("/model_health", headers={"Accept": "application/xml"})
    assert response.status_code == 406  # Not Acceptable

    # Test with different HTTP methods
    response = test_client.post("/model_health")
    assert response.status_code == 405  # Method Not Allowed


# Test API key validation with mocked environment variables
@pytest.mark.asyncio
async def test_api_key_validation_with_env_vars(monkeypatch):
    # Set environment variable
    monkeypatch.setenv("API_SECRET", "correct_key")

    # Test with correct key
    result = await validate_api_key("correct_key")
    assert result == "correct_key"

    # Test with incorrect key
    with pytest.raises(HTTPException) as excinfo:
        await validate_api_key("wrong_key")
    assert excinfo.value.status_code == 403

    # Test with missing environment variable
    monkeypatch.delenv("API_SECRET")
    with pytest.raises(HTTPException) as excinfo:
        await validate_api_key("any_key")
    assert excinfo.value.status_code == 403


# Test prediction response format
def test_prediction_response_format(test_client, mock_env_api_key, sample_data):
    response = test_client.post("/predict", json=sample_data)
    assert response.status_code == 200

    # Check response structure
    response_data = response.json()
    assert "prediction" in response_data
    assert "confidence" in response_data

    # Check data types
    assert isinstance(response_data["prediction"], list)
    assert isinstance(response_data["confidence"], (int, float))
    assert 0 <= response_data["confidence"] <= 1  # Confidence should be between 0 and 1


# Test with malformed features
def test_predict_with_malformed_features(test_client, mock_env_api_key):
    # Test with non-numeric features
    non_numeric = {"features": ["a", "b", "c"] + [0.1] * 125, "api_key": "test_key"}
    response = test_client.post("/predict", json=non_numeric)
    assert response.status_code == 422  # Validation error

    # Test with None values
    none_values = {"features": [None] * 128, "api_key": "test_key"}
    response = test_client.post("/predict", json=none_values)
    assert response.status_code == 422  # Validation error

    # Test with mixed types
    mixed_types = {
        "features": [0.1, "string", 1, True] + [0.1] * 124,
        "api_key": "test_key",
    }
    response = test_client.post("/predict", json=mixed_types)
    assert response.status_code == 422  # Validation error


# Test with different HTTP methods
def test_predict_with_different_http_methods(
    test_client, mock_env_api_key, sample_data
):
    # Test with GET (should fail)
    response = test_client.get("/predict", params=sample_data)
    assert response.status_code == 405  # Method Not Allowed

    # Test with PUT (should fail)
    response = test_client.put("/predict", json=sample_data)
    assert response.status_code == 405  # Method Not Allowed

    # Test with DELETE (should fail)
    response = test_client.delete("/predict")
    assert response.status_code == 405  # Method Not Allowed
