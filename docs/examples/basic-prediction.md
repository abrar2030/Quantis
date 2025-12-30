# Example: Basic Prediction Workflow

This example demonstrates the complete workflow for making predictions with a trained model using the Quantis API.

## Prerequisites

- Quantis services running (`./scripts/run_quantis.sh dev`)
- Valid user account and authentication token
- Trained model available

## Complete Workflow

### Step 1: Authentication

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "DemoPassword123!"
  }'
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the access token:

```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Step 2: List Available Models

```bash
curl -X GET http://localhost:8000/models \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "LSTM Stock Forecaster",
    "model_type": "lstm",
    "status": "trained",
    "created_at": "2025-12-30T10:00:00Z"
  },
  {
    "id": 2,
    "name": "TFT Market Predictor",
    "model_type": "tft",
    "status": "trained",
    "created_at": "2025-12-29T15:30:00Z"
  }
]
```

### Step 3: Get Model Details

```bash
curl -X GET http://localhost:8000/models/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "id": 1,
  "name": "LSTM Stock Forecaster",
  "model_type": "lstm",
  "status": "trained",
  "hyperparameters": {
    "hidden_size": 64,
    "num_layers": 2,
    "dropout": 0.2
  },
  "training_metrics": {
    "mse": 0.025,
    "mae": 0.015,
    "r2_score": 0.92
  },
  "created_at": "2025-12-30T10:00:00Z",
  "updated_at": "2025-12-30T12:00:00Z"
}
```

### Step 4: Make Single Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "input_data": [0.15, 0.25, 0.35, 0.45, 0.55]
  }'
```

**Response:**

```json
{
  "prediction_id": 12345,
  "model_id": 1,
  "prediction_result": [0.72, 0.28],
  "confidence_score": 0.85,
  "execution_time_ms": 45,
  "timestamp": "2025-12-30T14:30:00Z"
}
```

### Step 5: Make Batch Predictions

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "input_data_list": [
      [0.1, 0.2, 0.3, 0.4, 0.5],
      [0.2, 0.3, 0.4, 0.5, 0.6],
      [0.3, 0.4, 0.5, 0.6, 0.7]
    ]
  }'
```

**Response:**

```json
{
  "predictions": [
    {
      "prediction_id": 12346,
      "prediction_result": [0.65, 0.35],
      "confidence_score": 0.82
    },
    {
      "prediction_id": 12347,
      "prediction_result": [0.7, 0.3],
      "confidence_score": 0.88
    },
    {
      "prediction_id": 12348,
      "prediction_result": [0.75, 0.25],
      "confidence_score": 0.9
    }
  ],
  "total_predictions": 3,
  "successful_predictions": 3,
  "failed_predictions": 0
}
```

### Step 6: View Prediction History

```bash
curl -X GET "http://localhost:8000/predictions/history?model_id=1&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
[
  {
    "id": 12348,
    "model_id": 1,
    "model_name": "LSTM Stock Forecaster",
    "input_data": [0.3, 0.4, 0.5, 0.6, 0.7],
    "prediction_result": [0.75, 0.25],
    "confidence_score": 0.9,
    "execution_time_ms": 42,
    "created_at": "2025-12-30T14:32:00Z"
  }
]
```

## Python Client Example

```python
import requests

class QuantisPredictionClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        """Authenticate and store token."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token

    def get_headers(self):
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self.token}"}

    def list_models(self):
        """Get all available models."""
        response = requests.get(
            f"{self.base_url}/models",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def predict(self, model_id, input_data):
        """Make single prediction."""
        response = requests.post(
            f"{self.base_url}/predict",
            headers=self.get_headers(),
            json={"model_id": model_id, "input_data": input_data}
        )
        response.raise_for_status()
        return response.json()

    def predict_batch(self, model_id, input_data_list):
        """Make batch predictions."""
        response = requests.post(
            f"{self.base_url}/predict/batch",
            headers=self.get_headers(),
            json={"model_id": model_id, "input_data_list": input_data_list}
        )
        response.raise_for_status()
        return response.json()

    def get_prediction_history(self, model_id=None, limit=10):
        """Get prediction history."""
        params = {"limit": limit}
        if model_id:
            params["model_id"] = model_id

        response = requests.get(
            f"{self.base_url}/predictions/history",
            headers=self.get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    client = QuantisPredictionClient()

    # Login
    client.login("demo_user", "DemoPassword123!")
    print("✓ Logged in successfully")

    # List models
    models = client.list_models()
    print(f"✓ Found {len(models)} models")

    # Make prediction
    model_id = models[0]["id"]
    prediction = client.predict(
        model_id=model_id,
        input_data=[0.1, 0.2, 0.3, 0.4, 0.5]
    )
    print(f"✓ Prediction: {prediction['prediction_result']}")
    print(f"  Confidence: {prediction['confidence_score']:.2%}")

    # Batch predictions
    batch_results = client.predict_batch(
        model_id=model_id,
        input_data_list=[
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6],
            [0.3, 0.4, 0.5, 0.6, 0.7]
        ]
    )
    print(f"✓ Batch predictions: {batch_results['successful_predictions']} successful")

    # View history
    history = client.get_prediction_history(model_id=model_id, limit=5)
    print(f"✓ Recent predictions: {len(history)} records")
```

## JavaScript Example

```javascript
class QuantisPredictionClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = null;
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  getHeaders() {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async listModels() {
    const response = await fetch(`${this.baseURL}/models`, {
      headers: this.getHeaders(),
    });
    return await response.json();
  }

  async predict(modelId, inputData) {
    const response = await fetch(`${this.baseURL}/predict`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ model_id: modelId, input_data: inputData }),
    });
    return await response.json();
  }

  async predictBatch(modelId, inputDataList) {
    const response = await fetch(`${this.baseURL}/predict/batch`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        model_id: modelId,
        input_data_list: inputDataList,
      }),
    });
    return await response.json();
  }
}

// Usage
(async () => {
  const client = new QuantisPredictionClient();

  // Login
  await client.login('demo_user', 'DemoPassword123!');
  console.log('✓ Logged in');

  // List models
  const models = await client.listModels();
  console.log(`✓ Found ${models.length} models`);

  // Make prediction
  const prediction = await client.predict(models[0].id, [0.1, 0.2, 0.3]);
  console.log('✓ Prediction:', prediction.prediction_result);
})();
```

## Expected Results

- **Authentication**: Successfully obtain JWT token
- **Model Listing**: Retrieve list of trained models
- **Single Prediction**: Get prediction result with confidence score
- **Batch Prediction**: Process multiple inputs efficiently
- **History**: View past predictions for analysis

## Common Issues

### Issue: 401 Unauthorized

**Solution**: Token expired, re-authenticate

### Issue: 422 Validation Error

**Solution**: Check input_data matches model's expected input size

### Issue: 429 Rate Limit Exceeded

**Solution**: Implement exponential backoff, use batch endpoint

## Next Steps

- [Model Training Example](model-training.md)
- [Advanced Analytics Example](advanced-analytics.md)
- [API Reference](../API.md)

---
