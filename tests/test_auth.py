import pytest
from api.app import app
from api.middleware.auth import ApiKeyManager, RateLimiter, Roles
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("API_SECRET", "test_key")
    monkeypatch.setenv("JWT_SECRET", "test_jwt_secret")


@pytest.fixture
def admin_api_key():
    # Create an admin API key for testing
    return ApiKeyManager.create_api_key(
        user_id="test_admin", role=Roles.ADMIN, expiry_days=1
    )


@pytest.fixture
def user_api_key():
    # Create a regular user API key for testing
    return ApiKeyManager.create_api_key(
        user_id="test_user", role=Roles.USER, expiry_days=1
    )


@pytest.fixture
def readonly_api_key():
    # Create a readonly API key for testing
    return ApiKeyManager.create_api_key(
        user_id="test_readonly", role=Roles.READONLY, expiry_days=1
    )


def test_api_key_creation():
    # Test creating an API key
    api_key = ApiKeyManager.create_api_key(
        user_id="test_user", role=Roles.USER, expiry_days=30
    )

    assert api_key is not None
    assert len(api_key) > 0

    # Validate the key
    key_info = ApiKeyManager.validate_api_key(api_key)
    assert key_info["user_id"] == "test_user"
    assert key_info["role"] == Roles.USER


def test_api_key_validation():
    # Create a key
    api_key = ApiKeyManager.create_api_key(user_id="test_validation", role=Roles.ADMIN)

    # Validate it
    key_info = ApiKeyManager.validate_api_key(api_key)
    assert key_info["user_id"] == "test_validation"
    assert key_info["role"] == Roles.ADMIN

    # Test invalid key
    with pytest.raises(Exception):
        ApiKeyManager.validate_api_key("invalid_key")


def test_api_key_revocation():
    # Create a key
    api_key = ApiKeyManager.create_api_key(user_id="test_revocation", role=Roles.USER)

    # Validate it works
    key_info = ApiKeyManager.validate_api_key(api_key)
    assert key_info["user_id"] == "test_revocation"

    # Revoke it
    success = ApiKeyManager.revoke_api_key(api_key)
    assert success is True

    # Validate it no longer works
    with pytest.raises(Exception):
        ApiKeyManager.validate_api_key(api_key)


def test_rate_limiter():
    # Create a rate limiter with a low limit for testing
    limiter = RateLimiter(requests_per_minute=3)

    # Mock user for testing
    user = {"user_id": "test_rate_limit"}

    # First 3 requests should succeed
    for _ in range(3):
        result = limiter(user)
        assert result == user

    # 4th request should fail
    with pytest.raises(Exception):
        limiter(user)


def test_predict_endpoint_with_roles(test_client, user_api_key, readonly_api_key):
    # Test with user role (should succeed)
    response = test_client.post(
        "/predict", json={"features": [0.1] * 128}, headers={"X-API-Key": user_api_key}
    )
    assert response.status_code == 200

    # Test with readonly role (should fail)
    response = test_client.post(
        "/predict",
        json={"features": [0.1] * 128},
        headers={"X-API-Key": readonly_api_key},
    )
    assert response.status_code == 403


def test_model_health_with_roles(test_client, user_api_key, readonly_api_key):
    # Test with user role (should succeed)
    response = test_client.get("/model_health", headers={"X-API-Key": user_api_key})
    assert response.status_code == 200

    # Test with readonly role (should succeed)
    response = test_client.get("/model_health", headers={"X-API-Key": readonly_api_key})
    assert response.status_code == 200


def test_user_management_endpoints(test_client, admin_api_key, user_api_key):
    # Test creating a user with admin role (should succeed)
    response = test_client.post(
        "/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "role": "user",
            "password": "password123",
        },
        headers={"X-API-Key": admin_api_key},
    )
    assert response.status_code == 200

    # Test creating a user with user role (should fail)
    response = test_client.post(
        "/users",
        json={
            "username": "newuser2",
            "email": "newuser2@example.com",
            "role": "user",
            "password": "password123",
        },
        headers={"X-API-Key": user_api_key},
    )
    assert response.status_code == 403


def test_api_key_management_endpoints(test_client, admin_api_key, user_api_key):
    # Test creating an API key with admin role (should succeed)
    response = test_client.post(
        "/api-keys",
        json={"user_id": "newuser", "role": "user", "expiry_days": 30},
        headers={"X-API-Key": admin_api_key},
    )
    assert response.status_code == 200
    assert "api_key" in response.json()

    # Test creating an API key with user role (should fail)
    response = test_client.post(
        "/api-keys",
        json={"user_id": "newuser", "role": "user", "expiry_days": 30},
        headers={"X-API-Key": user_api_key},
    )
    assert response.status_code == 403


def test_current_user_endpoint(test_client, user_api_key):
    # Test getting current user info
    response = test_client.get("/users/me", headers={"X-API-Key": user_api_key})
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user"
    assert response.json()["role"] == Roles.USER
