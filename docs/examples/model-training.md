# Example: Model Training Workflow

Complete guide for training machine learning models using the Quantis platform.

## Overview

This example demonstrates:

1. Dataset upload and validation
2. Model creation and configuration
3. Training execution and monitoring
4. Model evaluation and comparison

## Step-by-Step Guide

### Step 1: Authenticate

```bash
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "DemoPassword123!"}' \
  | jq -r '.access_token')
```

### Step 2: Upload Training Dataset

```bash
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@stock_prices.csv" \
  -F "name=Stock Prices 2024" \
  -F "description=Daily stock prices for training"
```

**Response:**

```json
{
  "id": 1,
  "name": "Stock Prices 2024",
  "description": "Daily stock prices for training",
  "status": "uploaded",
  "total_rows": 10000,
  "total_columns": 15,
  "created_at": "2025-12-30T10:00:00Z"
}
```

### Step 3: View Dataset Statistics

```bash
curl -X GET http://localhost:8000/datasets/1/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "total_rows": 10000,
  "total_columns": 15,
  "numeric_columns": 12,
  "categorical_columns": 3,
  "missing_values": 25,
  "memory_usage_mb": 1.5,
  "column_stats": {
    "price": { "mean": 150.5, "std": 25.3, "min": 100, "max": 200 },
    "volume": { "mean": 1000000, "std": 500000, "min": 0, "max": 5000000 }
  }
}
```

### Step 4: Create Model

```bash
curl -X POST http://localhost:8000/models \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LSTM Stock Forecaster v1",
    "model_type": "lstm",
    "description": "LSTM model for predicting next-day stock prices",
    "hyperparameters": {
      "input_size": 10,
      "hidden_size": 64,
      "output_size": 3,
      "num_layers": 2,
      "dropout": 0.2,
      "learning_rate": 0.001
    }
  }'
```

**Response:**

```json
{
  "id": 1,
  "name": "LSTM Stock Forecaster v1",
  "model_type": "lstm",
  "status": "created",
  "hyperparameters": {...},
  "created_at": "2025-12-30T11:00:00Z"
}
```

### Step 5: Start Training

```bash
curl -X POST http://localhost:8000/models/1/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "epochs": 100,
    "batch_size": 32,
    "validation_split": 0.2,
    "early_stopping": true,
    "patience": 10
  }'
```

**Response:**

```json
{
  "status": "training_started",
  "training_id": "train_abc123",
  "estimated_duration_minutes": 15,
  "message": "Model training has started in the background"
}
```

### Step 6: Monitor Training Progress

```bash
# Poll training status
while true; do
  STATUS=$(curl -X GET http://localhost:8000/models/1/training-status \
    -H "Authorization: Bearer $TOKEN" \
    | jq -r '.status')

  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 5
done
```

**Training Status Response:**

```json
{
  "status": "training",
  "progress": 65,
  "current_epoch": 65,
  "total_epochs": 100,
  "current_metrics": {
    "loss": 0.0325,
    "val_loss": 0.0412,
    "mae": 0.0156
  },
  "elapsed_time_seconds": 540
}
```

**Completed Status:**

```json
{
  "status": "completed",
  "progress": 100,
  "final_metrics": {
    "loss": 0.0289,
    "val_loss": 0.0395,
    "mae": 0.0142,
    "mse": 0.0251,
    "r2_score": 0.92
  },
  "total_time_seconds": 780,
  "completed_at": "2025-12-30T11:13:00Z"
}
```

### Step 7: Get Model Metrics

```bash
curl -X GET http://localhost:8000/models/1/metrics \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "accuracy": 0.95,
  "precision": 0.94,
  "recall": 0.93,
  "f1_score": 0.935,
  "mse": 0.025,
  "mae": 0.015,
  "r2_score": 0.92,
  "training_history": {
    "epochs": [1, 2, 3, ..., 100],
    "loss": [0.5, 0.45, 0.42, ..., 0.029],
    "val_loss": [0.52, 0.48, 0.44, ..., 0.040]
  }
}
```

## Python Training Script

```python
import requests
import time
from typing import Dict, Any

class ModelTrainer:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token

    def upload_dataset(self, file_path: str, name: str) -> int:
        """Upload training dataset."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name}
            headers = {'Authorization': f'Bearer {self.token}'}

            response = requests.post(
                f"{self.base_url}/datasets/upload",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()['id']

    def create_model(self, config: Dict[str, Any]) -> int:
        """Create a new model."""
        response = requests.post(
            f"{self.base_url}/models",
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            json=config
        )
        response.raise_for_status()
        return response.json()['id']

    def train_model(self, model_id: int, training_config: Dict[str, Any]):
        """Start model training."""
        response = requests.post(
            f"{self.base_url}/models/{model_id}/train",
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            json=training_config
        )
        response.raise_for_status()
        return response.json()

    def wait_for_training(self, model_id: int, poll_interval=5):
        """Wait for training to complete."""
        print(f"Training model {model_id}...")

        while True:
            response = requests.get(
                f"{self.base_url}/models/{model_id}/training-status",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            status_data = response.json()
            status = status_data['status']

            if status == 'completed':
                print("\n✓ Training completed successfully!")
                return status_data
            elif status == 'failed':
                print("\n✗ Training failed!")
                raise Exception(f"Training failed: {status_data.get('error')}")
            else:
                progress = status_data.get('progress', 0)
                epoch = status_data.get('current_epoch', 0)
                total_epochs = status_data.get('total_epochs', 0)
                loss = status_data.get('current_metrics', {}).get('loss', 0)

                print(f"\rProgress: {progress}% | Epoch: {epoch}/{total_epochs} | Loss: {loss:.4f}", end='')
                time.sleep(poll_interval)

    def get_metrics(self, model_id: int) -> Dict[str, Any]:
        """Get model metrics."""
        response = requests.get(
            f"{self.base_url}/models/{model_id}/metrics",
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    # Login
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "demo_user", "password": "DemoPassword123!"}
    )
    token = login_response.json()['access_token']

    # Initialize trainer
    trainer = ModelTrainer(token=token)

    # Upload dataset
    print("Uploading dataset...")
    dataset_id = trainer.upload_dataset(
        file_path="data/stock_prices.csv",
        name="Stock Prices 2024"
    )
    print(f"✓ Dataset uploaded (ID: {dataset_id})")

    # Create model
    print("\nCreating model...")
    model_config = {
        "name": "LSTM Stock Forecaster",
        "model_type": "lstm",
        "hyperparameters": {
            "hidden_size": 64,
            "num_layers": 2,
            "dropout": 0.2,
            "learning_rate": 0.001
        }
    }
    model_id = trainer.create_model(model_config)
    print(f"✓ Model created (ID: {model_id})")

    # Train model
    print("\nStarting training...")
    training_config = {
        "dataset_id": dataset_id,
        "epochs": 100,
        "batch_size": 32,
        "validation_split": 0.2
    }
    trainer.train_model(model_id, training_config)

    # Wait for completion
    final_status = trainer.wait_for_training(model_id)

    # Get metrics
    print("\nFinal metrics:")
    metrics = trainer.get_metrics(model_id)
    print(f"  MAE: {metrics['mae']:.4f}")
    print(f"  MSE: {metrics['mse']:.4f}")
    print(f"  R²:  {metrics['r2_score']:.4f}")
```

## Advanced Configuration

### Custom Hyperparameters

```json
{
  "name": "Advanced LSTM Model",
  "model_type": "lstm",
  "hyperparameters": {
    "input_size": 20,
    "hidden_size": 128,
    "output_size": 5,
    "num_layers": 3,
    "dropout": 0.3,
    "learning_rate": 0.0005,
    "weight_decay": 0.0001,
    "gradient_clip": 1.0
  }
}
```

### Training with Early Stopping

```json
{
  "dataset_id": 1,
  "epochs": 200,
  "batch_size": 64,
  "validation_split": 0.2,
  "early_stopping": true,
  "patience": 15,
  "min_delta": 0.001
}
```

## Monitoring with MLflow

Access MLflow UI at: http://localhost:5000

View:

- Training curves
- Hyperparameter comparisons
- Model artifacts
- Experiment metrics

## Best Practices

1. **Data Validation**: Always check dataset stats before training
2. **Start Small**: Test with fewer epochs initially
3. **Monitor Progress**: Poll training status regularly
4. **Use Validation**: Always set validation_split
5. **Early Stopping**: Enable to prevent overfitting
6. **Save Checkpoints**: Models are automatically checkpointed
7. **Compare Models**: Use comparison endpoint to evaluate different configs

## Troubleshooting

### Issue: Training fails immediately

- Check dataset format and completeness
- Verify hyperparameters are valid
- Check system resources (memory, disk)

### Issue: Loss not decreasing

- Reduce learning rate
- Increase model capacity (hidden_size, num_layers)
- Check data preprocessing

### Issue: Overfitting

- Increase dropout
- Use early stopping
- Add more training data
- Reduce model complexity

## Next Steps

- [Basic Prediction Example](basic-prediction.md)
- [Advanced Analytics Example](advanced-analytics.md)
- [Model Comparison Guide](../API.md#get-modelscompare)

---
