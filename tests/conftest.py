import pytest
from api.app import app
# import torch # F401: Unused import
from fastapi.testclient import TestClient
from models.train_model import TemporalFusionTransformer


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def sample_model():
    model = TemporalFusionTransformer(input_size=128)
    return model


@pytest.fixture
def sample_data():
    return {"features": [0.1] * 128, "api_key": "test_key"}


@pytest.fixture
def mock_mlflow():
    # Mock MLflow tracking
    class MockMLflow:
        def __init__(self):
            self.metrics = {}
            self.params = {}

        def log_metric(self, key, value):
            self.metrics[key] = value

        def log_param(self, key, value):
            self.params[key] = value

    return MockMLflow()
