import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock

from models.train_model import TemporalFusionTransformer, train_model


# Test model with different input sizes
def test_model_with_different_input_sizes():
    # Test with minimum input size
    min_model = TemporalFusionTransformer(input_size=64)
    min_input = torch.randn(1, 64)
    min_output = min_model(min_input)
    assert min_output.shape == (1, 1)
    
    # Test with maximum input size
    max_model = TemporalFusionTransformer(input_size=256)
    max_input = torch.randn(1, 256)
    max_output = max_model(max_input)
    assert max_output.shape == (1, 1)


# Test model with different batch sizes
def test_model_with_different_batch_sizes(sample_model):
    # Test with small batch
    small_batch = torch.randn(5, 128)
    small_output = sample_model(small_batch)
    assert small_output.shape == (5, 1)
    
    # Test with large batch
    large_batch = torch.randn(100, 128)
    large_output = sample_model(large_batch)
    assert large_output.shape == (100, 1)
    
    # Test with single sample
    single_sample = torch.randn(1, 128)
    single_output = sample_model(single_sample)
    assert single_output.shape == (1, 1)


# Test model with different data types
def test_model_with_different_data_types(sample_model):
    # Test with float32
    float32_input = torch.randn(1, 128, dtype=torch.float32)
    float32_output = sample_model(float32_input)
    assert float32_output.dtype == torch.float32
    
    # Test with float64
    float64_input = torch.randn(1, 128, dtype=torch.float64)
    with pytest.raises(Exception):  # Should raise exception for incompatible dtype
        sample_model(float64_input)


# Test model with extreme values
def test_model_with_extreme_values(sample_model):
    # Test with very large values
    large_values = torch.ones(1, 128) * 1e10
    large_output = sample_model(large_values)
    assert not torch.isnan(large_output).any()
    
    # Test with very small values
    small_values = torch.ones(1, 128) * 1e-10
    small_output = sample_model(small_values)
    assert not torch.isnan(small_output).any()
    
    # Test with mixed positive and negative values
    mixed_values = torch.ones(1, 128)
    mixed_values[0, ::2] = -1  # Set every other value to -1
    mixed_output = sample_model(mixed_values)
    assert not torch.isnan(mixed_output).any()


# Test model training with different optimizers
@patch('torch.optim.Adam')
def test_model_training_with_different_optimizers(mock_adam, sample_model, mock_mlflow):
    # Setup mock optimizer
    mock_optimizer = MagicMock()
    mock_adam.return_value = mock_optimizer
    
    # Create dummy training data
    X_train = torch.randn(100, 128)
    y_train = torch.randn(100, 1)
    
    # Train model
    trained_model = train_model(sample_model, X_train, y_train, mock_mlflow)
    
    # Verify optimizer was used
    mock_adam.assert_called_once()
    assert isinstance(trained_model, TemporalFusionTransformer)


# Test model with noisy inputs
def test_model_robustness_to_noise(sample_model):
    # Generate base input
    base_input = torch.randn(1, 128)
    base_output = sample_model(base_input)
    
    # Add different levels of noise
    noise_levels = [0.01, 0.1, 0.5]
    for noise_level in noise_levels:
        noisy_input = base_input + torch.randn(1, 128) * noise_level
        noisy_output = sample_model(noisy_input)
        
        # Check that output changes gradually with noise
        output_diff = torch.norm(base_output - noisy_output).item()
        assert output_diff < noise_level * 10  # Output difference should be proportional to noise


# Test model with adversarial inputs
def test_model_with_adversarial_inputs(sample_model):
    # Generate base input
    base_input = torch.randn(1, 128, requires_grad=True)
    
    # Forward pass
    output = sample_model(base_input)
    loss = output.mean()
    
    # Backward pass to get gradients
    loss.backward()
    
    # Create adversarial example by moving in direction of gradient
    epsilon = 0.1
    adversarial_input = base_input + epsilon * base_input.grad.sign()
    
    # Check model output on adversarial input
    adversarial_output = sample_model(adversarial_input.detach())
    
    # Model should be somewhat robust to small adversarial perturbations
    assert not torch.isnan(adversarial_output).any()


# Test model serialization with different formats
def test_model_serialization_formats(sample_model, tmp_path):
    # Test PyTorch native serialization
    torch_path = tmp_path / "model.pt"
    torch.save(sample_model, torch_path)
    loaded_model = torch.load(torch_path)
    assert isinstance(loaded_model, TemporalFusionTransformer)
    
    # Test state_dict serialization
    state_dict_path = tmp_path / "model_state_dict.pt"
    torch.save(sample_model.state_dict(), state_dict_path)
    new_model = TemporalFusionTransformer(input_size=128)
    new_model.load_state_dict(torch.load(state_dict_path))
    
    # Compare outputs
    test_input = torch.randn(1, 128)
    original_output = sample_model(test_input)
    loaded_output = new_model(test_input)
    assert torch.allclose(original_output, loaded_output)


# Test model performance metrics
def test_model_performance_metrics(sample_model):
    # Generate synthetic test data
    num_samples = 100
    X_test = torch.randn(num_samples, 128)
    y_test = torch.randn(num_samples, 1)
    
    # Get model predictions
    y_pred = sample_model(X_test)
    
    # Calculate MSE
    mse = torch.mean((y_pred - y_test) ** 2).item()
    
    # Calculate MAE
    mae = torch.mean(torch.abs(y_pred - y_test)).item()
    
    # Calculate R^2
    y_mean = torch.mean(y_test)
    ss_tot = torch.sum((y_test - y_mean) ** 2)
    ss_res = torch.sum((y_test - y_pred) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    
    # Metrics should be valid
    assert 0 <= mse
    assert 0 <= mae
    assert r2 <= 1.0


# Test model with time-based features
def test_model_with_time_features(sample_model):
    # Create synthetic time series data with seasonal patterns
    batch_size = 10
    seq_len = 128
    
    # Generate time features (e.g., hour of day, day of week)
    time_features = torch.zeros(batch_size, seq_len)
    for i in range(seq_len):
        time_features[:, i] = i % 24  # Hour of day
    
    # Normalize time features
    time_features = time_features / 24.0
    
    # Model should handle time-based features
    output = sample_model(time_features)
    assert output.shape == (batch_size, 1)
    assert not torch.isnan(output).any()


# Test model with missing values
def test_model_with_missing_values(sample_model):
    # Create input with some missing values (represented as NaNs)
    input_with_nans = torch.randn(1, 128)
    input_with_nans[0, 10:20] = float('nan')  # Set some values to NaN
    
    # Replace NaNs with zeros or mean
    input_fixed = torch.nan_to_num(input_with_nans, nan=0.0)
    
    # Model should handle the fixed input
    output = sample_model(input_fixed)
    assert not torch.isnan(output).any()


# Test model with different learning rates
def test_model_with_different_learning_rates(sample_model, mock_mlflow):
    # Create dummy training data
    X_train = torch.randn(100, 128)
    y_train = torch.randn(100, 1)
    
    # Test with different learning rates
    learning_rates = [0.001, 0.01, 0.1]
    for lr in learning_rates:
        # Set learning rate
        sample_model.learning_rate = lr
        
        # Train model
        trained_model = train_model(sample_model, X_train, y_train, mock_mlflow)
        
        # Verify model was trained
        assert isinstance(trained_model, TemporalFusionTransformer)
        assert trained_model.learning_rate == lr
