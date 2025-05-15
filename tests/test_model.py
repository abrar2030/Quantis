# import numpy as np # F401: Unused import
import pytest
import torch

from models.mlflow_tracking import log_metrics
from models.train_model import TemporalFusionTransformer, train_model


def test_model_loading():
    model = TemporalFusionTransformer(input_size=128)
    model.load_state_dict(torch.load("tft_model.pt"))
    assert model(torch.randn(1, 128)).shape == (1, 1)


def test_api_endpoint(test_client):
    response = test_client.post(
        "/predict", json={"features": [0.1, 0.5, ...], "api_key": "valid_key"}
    )
    assert response.status_code == 200


def test_model_initialization(sample_model):
    assert isinstance(sample_model, TemporalFusionTransformer)
    assert sample_model.input_size == 128


def test_model_forward_pass(sample_model):
    input_tensor = torch.randn(1, 128)
    output = sample_model(input_tensor)
    assert output.shape == (1, 1)
    assert not torch.isnan(output).any()


def test_model_training(sample_model, mock_mlflow):
    # Create dummy training data
    X_train = torch.randn(100, 128)
    y_train = torch.randn(100, 1)

    # Train model
    trained_model = train_model(sample_model, X_train, y_train, mock_mlflow)

    # Verify model was trained
    assert isinstance(trained_model, TemporalFusionTransformer)
    assert len(mock_mlflow.metrics) > 0
    assert "loss" in mock_mlflow.metrics


def test_model_save_load(sample_model, tmp_path):
    # Save model
    save_path = tmp_path / "test_model.pt"
    torch.save(sample_model.state_dict(), save_path)

    # Load model
    loaded_model = TemporalFusionTransformer(input_size=128)
    loaded_model.load_state_dict(torch.load(save_path))

    # Verify loaded model
    assert isinstance(loaded_model, TemporalFusionTransformer)
    input_tensor = torch.randn(1, 128)
    assert torch.allclose(sample_model(input_tensor), loaded_model(input_tensor))


def test_mlflow_tracking(mock_mlflow):
    metrics = {"accuracy": 0.95, "loss": 0.1}
    log_metrics(metrics, mock_mlflow)

    assert mock_mlflow.metrics["accuracy"] == 0.95
    assert mock_mlflow.metrics["loss"] == 0.1


def test_model_inference(sample_model):
    input_tensor = torch.randn(1, 128)
    prediction = sample_model(input_tensor)

    assert isinstance(prediction, torch.Tensor)
    assert prediction.shape == (1, 1)
    assert not torch.isnan(prediction).any()
    assert not torch.isinf(prediction).any()


def test_model_batch_processing(sample_model):
    # Test batch processing
    batch_size = 32
    input_batch = torch.randn(batch_size, 128)
    output_batch = sample_model(input_batch)

    assert output_batch.shape == (batch_size, 1)
    assert not torch.isnan(output_batch).any()
    assert not torch.isinf(output_batch).any()


def test_model_gradient_flow(sample_model):
    # Test gradient flow during training
    input_tensor = torch.randn(1, 128, requires_grad=True)
    output = sample_model(input_tensor)
    loss = output.mean()
    loss.backward()

    # Check if gradients are flowing
    assert input_tensor.grad is not None
    assert not torch.isnan(input_tensor.grad).any()


def test_model_hyperparameters(sample_model):
    # Test model hyperparameters
    assert hasattr(sample_model, "learning_rate")
    assert hasattr(sample_model, "batch_size")
    assert hasattr(sample_model, "num_epochs")
    assert sample_model.learning_rate > 0
    assert sample_model.batch_size > 0
    assert sample_model.num_epochs > 0


def test_model_regularization(sample_model):
    # Test regularization effects
    input_tensor = torch.randn(1, 128)
    output1 = sample_model(input_tensor)

    # Add noise to input
    noisy_input = input_tensor + torch.randn_like(input_tensor) * 0.1
    output2 = sample_model(noisy_input)

    # Outputs should be similar but not identical
    assert not torch.allclose(output1, output2)
    assert torch.norm(output1 - output2) < 1.0


def test_model_memory_efficiency(sample_model):
    # Test memory efficiency
    torch.cuda.reset_peak_memory_stats()
    initial_memory = torch.cuda.memory_allocated()

    # Process large batch
    batch_size = 1024
    input_batch = torch.randn(batch_size, 128)
    _ = sample_model(input_batch)

    final_memory = torch.cuda.memory_allocated()
    memory_used = final_memory - initial_memory

    # Memory usage should be reasonable
    assert memory_used < 1e9  # Less than 1GB


def test_model_error_handling(sample_model):
    # Test error handling for invalid inputs
    with pytest.raises(ValueError):
        sample_model(torch.randn(1, 64))  # Wrong input size

    with pytest.raises(ValueError):
        sample_model(torch.randn(1, 128, 1))  # Wrong input dimensions
