import pytest
from models.aws_deploy import deploy_to_aws
from monitoring.metrics_collector import MetricsCollector
import boto3
from unittest.mock import Mock, patch

@pytest.fixture
def mock_s3():
    with patch('boto3.client') as mock:
        mock_s3 = Mock()
        mock.return_value = mock_s3
        yield mock_s3

@pytest.fixture
def mock_cloudwatch():
    with patch('boto3.client') as mock:
        mock_cloudwatch = Mock()
        mock.return_value = mock_cloudwatch
        yield mock_cloudwatch

def test_aws_deployment(mock_s3):
    model_path = "test_model.pt"
    bucket_name = "test-bucket"
    
    deploy_to_aws(model_path, bucket_name)
    
    mock_s3.upload_file.assert_called_once_with(
        model_path,
        bucket_name,
        f"models/{model_path}"
    )

def test_metrics_collector(mock_cloudwatch):
    collector = MetricsCollector()
    
    # Test metric collection
    collector.record_metric("PredictionLatency", 0.5)
    collector.record_metric("ModelAccuracy", 0.95)
    
    # Verify metrics were sent to CloudWatch
    assert mock_cloudwatch.put_metric_data.call_count == 2

def test_error_handling(mock_s3):
    # Test deployment with invalid credentials
    mock_s3.upload_file.side_effect = Exception("Invalid credentials")
    
    with pytest.raises(Exception) as exc_info:
        deploy_to_aws("test_model.pt", "test-bucket")
    
    assert "Invalid credentials" in str(exc_info.value)

def test_metrics_validation(mock_cloudwatch):
    collector = MetricsCollector()
    
    # Test invalid metric value
    with pytest.raises(ValueError):
        collector.record_metric("InvalidMetric", -1)
    
    # Test invalid metric name
    with pytest.raises(ValueError):
        collector.record_metric("", 0.5) 