# Example: Advanced Analytics Workflow

Comprehensive example demonstrating advanced analytics, monitoring, and financial calculations.

## Overview

This example shows:

- Financial transaction analysis
- NPV and interest calculations
- System monitoring and metrics
- Prediction analytics
- Model comparison

## Complete Workflow

### 1. Financial Transaction Analysis

#### Create Transaction

```bash
curl -X POST http://localhost:8000/financial/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10000.00,
    "currency": "USD",
    "transaction_type": "deposit",
    "description": "Initial investment"
  }'
```

#### Get Financial Summary

```bash
curl -X GET http://localhost:8000/financial/financial-summary \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "total_balance": 10000.0,
  "total_deposits": 10000.0,
  "total_withdrawals": 0.0,
  "pending_transactions": 0,
  "approved_transactions": 1,
  "last_transaction_date": "2025-12-30T14:00:00Z"
}
```

#### Calculate NPV

```bash
curl -X POST http://localhost:8000/financial/calculate-npv \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rate": 0.10,
    "cash_flows": [-10000, 3000, 4000, 5000, 6000]
  }'
```

**Response:**

```json
{
  "npv": 3914.21,
  "rate": 0.1,
  "initial_investment": -10000,
  "total_cash_flows": 18000,
  "payback_period_years": 2.5,
  "profitable": true
}
```

### 2. System Monitoring

#### Health Check

```bash
curl -X GET http://localhost:8000/monitoring/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T14:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy",
    "celery_workers": "healthy"
  },
  "uptime_seconds": 86400,
  "version": "1.0.0"
}
```

#### System Statistics

```bash
curl -X GET http://localhost:8000/monitoring/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "cpu_percent": 45.2,
  "memory_percent": 62.8,
  "disk_percent": 35.5,
  "active_users": 150,
  "total_requests_today": 10000,
  "average_response_time_ms": 85,
  "error_rate": 0.002,
  "active_predictions_per_minute": 250
}
```

### 3. Prediction Analytics

#### Get Prediction Statistics

```bash
curl -X GET http://localhost:8000/predictions/stats \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "total_predictions": 50000,
  "predictions_today": 5000,
  "avg_confidence": 0.87,
  "avg_execution_time_ms": 42,
  "predictions_by_model": {
    "1": 30000,
    "2": 20000
  },
  "predictions_by_day": {
    "2025-12-28": 4500,
    "2025-12-29": 4800,
    "2025-12-30": 5000
  },
  "confidence_distribution": {
    "0.0-0.5": 500,
    "0.5-0.7": 2000,
    "0.7-0.9": 20000,
    "0.9-1.0": 27500
  }
}
```

### 4. Model Comparison

#### Compare Multiple Models

```bash
curl -X GET "http://localhost:8000/models/compare?model_ids=1,2,3" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "models": [
    {
      "id": 1,
      "name": "LSTM Forecaster",
      "model_type": "lstm",
      "metrics": {
        "mse": 0.025,
        "mae": 0.015,
        "r2_score": 0.92
      },
      "training_time_seconds": 780,
      "prediction_time_ms": 42
    },
    {
      "id": 2,
      "name": "TFT Predictor",
      "model_type": "tft",
      "metrics": {
        "mse": 0.02,
        "mae": 0.012,
        "r2_score": 0.94
      },
      "training_time_seconds": 1200,
      "prediction_time_ms": 65
    },
    {
      "id": 3,
      "name": "Random Forest",
      "model_type": "random_forest",
      "metrics": {
        "mse": 0.03,
        "mae": 0.018,
        "r2_score": 0.89
      },
      "training_time_seconds": 300,
      "prediction_time_ms": 25
    }
  ],
  "comparison": {
    "best_accuracy": "TFT Predictor",
    "fastest_training": "Random Forest",
    "fastest_prediction": "Random Forest",
    "recommended": "TFT Predictor"
  }
}
```

## Python Analytics Script

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List

class QuantisAnalytics:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_financial_summary(self) -> Dict:
        """Get financial summary."""
        response = requests.get(
            f"{self.base_url}/financial/financial-summary",
            headers=self.headers
        )
        return response.json()

    def calculate_npv(self, rate: float, cash_flows: List[float]) -> Dict:
        """Calculate NPV for investment analysis."""
        response = requests.post(
            f"{self.base_url}/financial/calculate-npv",
            headers={**self.headers, 'Content-Type': 'application/json'},
            json={"rate": rate, "cash_flows": cash_flows}
        )
        return response.json()

    def get_prediction_stats(self) -> Dict:
        """Get prediction statistics."""
        response = requests.get(
            f"{self.base_url}/predictions/stats",
            headers=self.headers
        )
        return response.json()

    def compare_models(self, model_ids: List[int]) -> Dict:
        """Compare multiple models."""
        ids_str = ','.join(map(str, model_ids))
        response = requests.get(
            f"{self.base_url}/models/compare?model_ids={ids_str}",
            headers=self.headers
        )
        return response.json()

    def get_system_stats(self) -> Dict:
        """Get system statistics."""
        response = requests.get(
            f"{self.base_url}/monitoring/stats",
            headers=self.headers
        )
        return response.json()

    def plot_model_comparison(self, comparison_data: Dict):
        """Visualize model comparison."""
        models = comparison_data['models']

        # Extract data
        names = [m['name'] for m in models]
        mae = [m['metrics']['mae'] for m in models]
        mse = [m['metrics']['mse'] for m in models]
        r2 = [m['metrics']['r2_score'] for m in models]
        training_time = [m['training_time_seconds'] for m in models]

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # MAE comparison
        axes[0, 0].bar(names, mae, color='steelblue')
        axes[0, 0].set_title('Mean Absolute Error')
        axes[0, 0].set_ylabel('MAE')

        # MSE comparison
        axes[0, 1].bar(names, mse, color='coral')
        axes[0, 1].set_title('Mean Squared Error')
        axes[0, 1].set_ylabel('MSE')

        # R² comparison
        axes[1, 0].bar(names, r2, color='green')
        axes[1, 0].set_title('R² Score')
        axes[1, 0].set_ylabel('R²')

        # Training time comparison
        axes[1, 1].bar(names, training_time, color='purple')
        axes[1, 1].set_title('Training Time')
        axes[1, 1].set_ylabel('Seconds')

        plt.tight_layout()
        plt.savefig('model_comparison.png')
        print("✓ Saved comparison chart to model_comparison.png")

    def analyze_predictions(self, stats: Dict):
        """Analyze prediction statistics."""
        print("\n=== Prediction Analysis ===")
        print(f"Total predictions: {stats['total_predictions']:,}")
        print(f"Today's predictions: {stats['predictions_today']:,}")
        print(f"Average confidence: {stats['avg_confidence']:.2%}")
        print(f"Average execution time: {stats['avg_execution_time_ms']:.1f}ms")

        # Predictions by model
        print("\nPredictions by model:")
        for model_id, count in stats['predictions_by_model'].items():
            print(f"  Model {model_id}: {count:,}")

        # Confidence distribution
        print("\nConfidence distribution:")
        for range_str, count in stats['confidence_distribution'].items():
            percentage = (count / stats['total_predictions']) * 100
            print(f"  {range_str}: {count:,} ({percentage:.1f}%)")

# Usage example
if __name__ == "__main__":
    # Login
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "demo_user", "password": "DemoPassword123!"}
    )
    token = login_response.json()['access_token']

    # Initialize analytics
    analytics = QuantisAnalytics(token=token)

    # Financial analysis
    print("=== Financial Analysis ===")
    summary = analytics.get_financial_summary()
    print(f"Total balance: ${summary['total_balance']:,.2f}")

    # NPV calculation
    npv_result = analytics.calculate_npv(
        rate=0.10,
        cash_flows=[-10000, 3000, 4000, 5000, 6000]
    )
    print(f"Investment NPV: ${npv_result['npv']:,.2f}")
    print(f"Profitable: {npv_result['profitable']}")

    # System monitoring
    print("\n=== System Status ===")
    sys_stats = analytics.get_system_stats()
    print(f"CPU: {sys_stats['cpu_percent']:.1f}%")
    print(f"Memory: {sys_stats['memory_percent']:.1f}%")
    print(f"Active users: {sys_stats['active_users']}")

    # Prediction analytics
    pred_stats = analytics.get_prediction_stats()
    analytics.analyze_predictions(pred_stats)

    # Model comparison
    print("\n=== Model Comparison ===")
    comparison = analytics.compare_models([1, 2, 3])
    analytics.plot_model_comparison(comparison)

    print(f"\n✓ Recommended model: {comparison['comparison']['recommended']}")
```

## Dashboard Integration

### Real-time Metrics Dashboard

```javascript
// Fetch and display real-time metrics
async function updateDashboard() {
  // System stats
  const sysStats = await fetch('/monitoring/stats', {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json());

  updateCharts({
    cpu: sysStats.cpu_percent,
    memory: sysStats.memory_percent,
    requests: sysStats.total_requests_today,
  });

  // Prediction stats
  const predStats = await fetch('/predictions/stats', {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json());

  updatePredictionMetrics({
    total: predStats.total_predictions,
    confidence: predStats.avg_confidence,
    speed: predStats.avg_execution_time_ms,
  });
}

// Update every 5 seconds
setInterval(updateDashboard, 5000);
```

## Key Insights

### Performance Metrics

- Average prediction time: 42ms
- System uptime: 99.9%
- Request success rate: 99.8%

### Model Performance

- Best accuracy: TFT Predictor (94% R²)
- Fastest inference: Random Forest (25ms)
- Best balance: LSTM Forecaster

### Financial Insights

- Positive NPV on investment
- Healthy transaction flow
- Balanced portfolio

## Next Steps

- [Basic Prediction Example](basic-prediction.md)
- [Model Training Example](model-training.md)
- [API Reference](../API.md)
- [Monitoring Guide](../USAGE.md#monitoring--analytics)

---
