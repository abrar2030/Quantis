# Usage Guide

Comprehensive guide for using the Quantis platform, covering common workflows, API usage, and best practices.

## Table of Contents

- [Getting Started](#getting-started)
- [Common Workflows](#common-workflows)
- [CLI Usage](#cli-usage)
- [Library/SDK Usage](#librarysdk-usage)
- [Web Dashboard Usage](#web-dashboard-usage)
- [API Client Examples](#api-client-examples)
- [Model Training](#model-training)
- [Making Predictions](#making-predictions)
- [Dataset Management](#dataset-management)
- [Monitoring & Analytics](#monitoring--analytics)
- [Best Practices](#best-practices)

---

## Getting Started

### Quick Start (3 Steps)

```bash
# 1. Clone and setup
git clone https://github.com/quantsingularity/Quantis.git && cd Quantis
./scripts/setup_quantis_env.sh

# 2. Start services
./scripts/run_quantis.sh dev

# 3. Access the platform
# Web UI: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## Common Workflows

### Workflow 1: Train a Model and Make Predictions

```bash
# Step 1: Upload dataset
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@stock_data.csv" \
  -F "name=Stock Prices 2024"
# Response: {"id": 1, "name": "Stock Prices 2024", ...}

# Step 2: Create a model
curl -X POST http://localhost:8000/models \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LSTM Stock Forecaster",
    "model_type": "lstm",
    "hyperparameters": {"hidden_size": 64, "num_layers": 2}
  }'
# Response: {"id": 1, "name": "LSTM Stock Forecaster", ...}

# Step 3: Train the model
curl -X POST http://localhost:8000/models/1/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "epochs": 100,
    "batch_size": 32
  }'
# Response: {"status": "training_started", "training_id": "abc123"}

# Step 4: Check training status
curl -X GET http://localhost:8000/models/1/training-status \
  -H "Authorization: Bearer <token>"
# Response: {"status": "completed", "metrics": {...}}

# Step 5: Make predictions
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "input_data": [0.15, 0.25, 0.35, 0.45]
  }'
# Response: {"prediction_result": [0.72, 0.28], "confidence": 0.85}
```

### Workflow 2: Financial Transaction Analysis

```bash
# Step 1: Create a transaction
curl -X POST http://localhost:8000/financial/transactions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.00,
    "currency": "USD",
    "transaction_type": "deposit"
  }'

# Step 2: Get financial summary
curl -X GET http://localhost:8000/financial/financial-summary \
  -H "Authorization: Bearer <token>"
# Response: {"total_balance": 1000.00, ...}

# Step 3: Calculate NPV for investment
curl -X POST http://localhost:8000/financial/calculate-npv \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rate": 0.1,
    "cash_flows": [100, 200, 300, 400]
  }'
# Response: {"npv": 834.56}
```

### Workflow 3: Real-time Monitoring

```bash
# Step 1: Check system health
curl -X GET http://localhost:8000/monitoring/health
# Response: {"status": "healthy", "services": {...}}

# Step 2: Get system statistics
curl -X GET http://localhost:8000/monitoring/stats \
  -H "Authorization: Bearer <token>"
# Response: {"cpu_percent": 45.2, "memory_percent": 62.8, ...}

# Step 3: View prediction analytics
curl -X GET http://localhost:8000/monitoring/analytics/predictions \
  -H "Authorization: Bearer <token>"
# Response: {"total_predictions": 5000, "avg_confidence": 0.87, ...}
```

---

## CLI Usage

### Development Mode

```bash
# Start all services in development mode
./scripts/run_quantis.sh dev

# In separate terminals, you can:
# - View API logs
# - Run tests
# - Process data
```

### Testing

```bash
# Run all tests
./scripts/test_quantis.sh

# Run specific test categories
./scripts/test_quantis.sh --unit
./scripts/test_quantis.sh --integration

# Run with coverage
./scripts/test_quantis.sh --coverage
```

### Data Processing

```bash
# Process a dataset
./scripts/data_processor.sh process market_data.csv --clean --normalize

# Validate dataset
./scripts/data_processor.sh validate data.parquet
```

### Code Quality

```bash
# Run linters and formatters
./scripts/linting.sh --fix

# Check all file types
./scripts/lint-all.sh
```

---

## Library/SDK Usage

### Python Library Usage

Quantis can be used as a Python library for programmatic access.

#### Example 1: Train a Model

```python
import sys
sys.path.insert(0, '/path/to/Quantis/code')

from models.train_model import train_model
import numpy as np

# Prepare training data
data_path = "data/processed/stock_prices.parquet"

# Define hyperparameters
params = {
    "input_size": 10,
    "hidden_size": 64,
    "output_size": 3,
    "num_layers": 2,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
}

# Train the model
model = train_model(data_path, params)
print("Model trained successfully!")
```

#### Example 2: Data Processing

```python
from data.process_data import DataEngine

# Initialize data engine
engine = DataEngine()

# Process raw data
raw_data_path = "data/raw/market_data.parquet"
processed_data = engine.process(raw_data_path)

print(f"Processed {len(processed_data)} records")
```

#### Example 3: API Client

```python
import requests

class QuantisClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        return self.token

    def create_model(self, name, model_type, hyperparameters=None):
        response = requests.post(
            f"{self.base_url}/models",
            headers=self.headers,
            json={
                "name": name,
                "model_type": model_type,
                "hyperparameters": hyperparameters or {}
            }
        )
        return response.json()

    def predict(self, model_id, input_data):
        response = requests.post(
            f"{self.base_url}/predict",
            headers=self.headers,
            json={"model_id": model_id, "input_data": input_data}
        )
        return response.json()

# Usage
client = QuantisClient()
client.login("john_doe", "MyP@ssw0rd!2025")

# Create model
model = client.create_model(
    "My LSTM Model",
    "lstm",
    {"hidden_size": 64}
)

# Make prediction
result = client.predict(model["id"], [0.1, 0.2, 0.3])
print(f"Prediction: {result['prediction_result']}")
```

---

## Web Dashboard Usage

### Accessing the Dashboard

1. Start the services: `./scripts/run_quantis.sh dev`
2. Navigate to: http://localhost:3000
3. Login with your credentials

### Dashboard Features

#### 1. Model Management

- **Create Models**: Click "New Model" → Select type → Configure hyperparameters
- **Train Models**: Select model → Click "Train" → Choose dataset → Start training
- **View Metrics**: Navigate to model detail page → View accuracy, loss, and performance metrics

#### 2. Dataset Management

- **Upload Datasets**: Click "Upload Dataset" → Select file (CSV, Parquet, JSON)
- **Preview Data**: Click dataset → View sample rows and statistics
- **Download**: Click download icon to export processed datasets

#### 3. Predictions

- **Single Prediction**: Models → Select model → Enter input values → Click "Predict"
- **Batch Prediction**: Upload CSV with multiple rows → Select model → Execute batch
- **View History**: Predictions tab → Filter by model, date range, or confidence score

#### 4. Analytics Dashboard

- **Model Performance**: View accuracy trends, training curves, and comparison charts
- **Prediction Analytics**: Total predictions, average confidence, execution times
- **System Metrics**: CPU usage, memory usage, request rates

---

## API Client Examples

### JavaScript/TypeScript Example

```typescript
import axios from 'axios';

class QuantisAPI {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async login(username: string, password: string): Promise<string> {
    const response = await axios.post(`${this.baseURL}/auth/login`, {
      username,
      password,
    });
    this.token = response.data.access_token;
    return this.token;
  }

  private getHeaders() {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async getModels(): Promise<any[]> {
    const response = await axios.get(`${this.baseURL}/models`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async predict(modelId: number, inputData: number[]): Promise<any> {
    const response = await axios.post(
      `${this.baseURL}/predict`,
      { model_id: modelId, input_data: inputData },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

// Usage
const api = new QuantisAPI();
await api.login('john_doe', 'MyP@ssw0rd!2025');
const models = await api.getModels();
const prediction = await api.predict(1, [0.1, 0.2, 0.3]);
console.log('Prediction:', prediction);
```

### cURL Examples

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "MyP@ssw0rd!2025"}'

# Store token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# List models
curl -X GET http://localhost:8000/models \
  -H "Authorization: Bearer $TOKEN"

# Create dataset
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data.csv" \
  -F "name=My Dataset"

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model_id": 1, "input_data": [0.1, 0.2, 0.3]}'
```

---

## Model Training

### Supported Model Types

| Model Type                      | Code            | Description                 | Use Case                   |
| ------------------------------- | --------------- | --------------------------- | -------------------------- |
| **LSTM**                        | `lstm`          | Long Short-Term Memory      | Time series forecasting    |
| **Temporal Fusion Transformer** | `tft`           | Attention-based forecasting | Complex time series        |
| **Random Forest**               | `random_forest` | Ensemble learning           | Classification, regression |
| **XGBoost**                     | `xgboost`       | Gradient boosting           | High-performance ML        |

### Training Configuration

```python
# Example: LSTM Training
{
  "model_id": 1,
  "dataset_id": 1,
  "epochs": 100,
  "batch_size": 32,
  "learning_rate": 0.001,
  "validation_split": 0.2,
  "early_stopping": true,
  "patience": 10
}
```

### Monitoring Training Progress

```bash
# Check training status
curl -X GET http://localhost:8000/models/1/training-status \
  -H "Authorization: Bearer $TOKEN"

# View metrics
curl -X GET http://localhost:8000/models/1/metrics \
  -H "Authorization: Bearer $TOKEN"
```

---

## Making Predictions

### Single Prediction

```python
# Python example
import requests

response = requests.post(
    "http://localhost:8000/predict",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model_id": 1,
        "input_data": [0.15, 0.25, 0.35, 0.45, 0.55]
    }
)

result = response.json()
print(f"Prediction: {result['prediction_result']}")
print(f"Confidence: {result['confidence_score']}")
```

### Batch Predictions

```python
# Batch prediction example
response = requests.post(
    "http://localhost:8000/predict/batch",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "model_id": 1,
        "input_data_list": [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ]
    }
)

results = response.json()
print(f"Total predictions: {results['total_predictions']}")
print(f"Successful: {results['successful_predictions']}")
```

---

## Dataset Management

### Uploading Datasets

**Supported Formats:**

- CSV (`.csv`)
- Parquet (`.parquet`)
- JSON (`.json`)
- Excel (`.xlsx`)

**Example:**

```bash
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@market_data.csv" \
  -F "name=Market Data 2024" \
  -F "description=Daily market prices"
```

### Dataset Statistics

```bash
# Get statistics
curl -X GET http://localhost:8000/datasets/1/stats \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "total_rows": 10000,
  "total_columns": 15,
  "numeric_columns": 12,
  "categorical_columns": 3,
  "missing_values": 25,
  "memory_usage_mb": 1.5
}
```

### Preview Dataset

```bash
# Preview first 20 rows
curl -X GET "http://localhost:8000/datasets/1/preview?limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Monitoring & Analytics

### System Health

```bash
# Check health
curl http://localhost:8000/monitoring/health

# Get system statistics
curl -X GET http://localhost:8000/monitoring/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Prometheus Metrics

Access Prometheus metrics at: http://localhost:9090

**Key Metrics:**

- `quantis_requests_total` - Total HTTP requests
- `quantis_request_duration_seconds` - Request latency
- `quantis_websocket_connections_total` - WebSocket connections
- `data_drift` - Model data drift
- `concept_drift` - Model performance drift

### Grafana Dashboards

Access Grafana at: http://localhost:3000

**Pre-configured Dashboards:**

- System Overview
- Model Performance
- Prediction Analytics
- API Usage Statistics

---

## Best Practices

### 1. Authentication

- Always use HTTPS in production
- Rotate JWT tokens regularly
- Store tokens securely (not in localStorage for sensitive apps)
- Use API keys for service-to-service communication

### 2. Rate Limiting

- Implement exponential backoff for rate limit errors
- Use batch endpoints when making multiple similar requests
- Monitor rate limit headers in responses

### 3. Data Management

- Validate data before uploading
- Use appropriate file formats (Parquet for large datasets)
- Clean and normalize data before training
- Version your datasets

### 4. Model Training

- Start with default hyperparameters
- Use validation split for model evaluation
- Enable early stopping to prevent overfitting
- Monitor training metrics via MLflow

### 5. Predictions

- Batch predictions when possible for better performance
- Cache prediction results for frequently-used inputs
- Monitor prediction confidence scores
- Log predictions for audit trails

### 6. Error Handling

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    return response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except RequestException as e:
    print(f"Request failed: {e}")
```

### 7. Performance Optimization

- Use connection pooling for multiple requests
- Enable compression for large payloads
- Implement client-side caching
- Use WebSockets for real-time updates

---

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Issue**: 401 Unauthorized  
**Solution**: Check token expiration, refresh if needed

#### 2. Slow Predictions

**Issue**: Predictions taking too long  
**Solution**: Use batch predictions, check model complexity

#### 3. Training Failures

**Issue**: Model training fails  
**Solution**: Validate dataset format, check resource availability

#### 4. Connection Errors

**Issue**: Cannot connect to API  
**Solution**: Verify services are running, check firewall settings

---

## Next Steps

- [API Reference](API.md) - Detailed API endpoint documentation
- [Configuration Guide](CONFIGURATION.md) - Environment configuration
- [Examples](examples/) - Working code examples
- [CLI Reference](CLI.md) - Command-line tools

---
