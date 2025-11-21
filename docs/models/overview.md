# Models Documentation

This document provides comprehensive information about the machine learning models used in the Quantis time series forecasting platform, including their architecture, training process, and deployment.

## Overview

Quantis uses state-of-the-art machine learning models for time series forecasting. The primary model is the Temporal Fusion Transformer (TFT), which is specifically designed for multi-horizon time series forecasting with mixed covariates. The platform also supports other models and allows for custom model implementation.

## Model Architecture

### Temporal Fusion Transformer (TFT)

The Temporal Fusion Transformer is the primary forecasting model in Quantis. It combines high-performance multi-horizon forecasting with interpretable insights into temporal relationships.

#### Architecture Components

The TFT architecture consists of several key components:

1. **Variable Selection Networks**: Identify relevant input features at each time step
2. **Gated Residual Networks (GRNs)**: Enable efficient information flow with skip connections
3. **Temporal Processing Layers**:
   - LSTM layers for local processing
   - Self-attention layers for long-range dependencies
4. **Multi-head Attention Mechanism**: Captures different temporal patterns simultaneously
5. **Quantile Outputs**: Provides prediction intervals rather than just point forecasts

#### Input Types

TFT handles three types of variables:

- **Static Covariates**: Features that remain constant for a time series (e.g., location, product category)
- **Known Future Inputs**: Variables known in advance for the forecast horizon (e.g., holidays, planned events)
- **Observed Inputs**: Historical values only available up to the forecast point (e.g., past values, weather)

#### Interpretability Features

TFT provides several interpretability mechanisms:

- **Variable Importance**: Identifies which features are most influential
- **Temporal Attention**: Shows which historical time points influence each forecast point
- **Persistent vs. Temporal Effects**: Distinguishes between long-term and short-term influences

### Other Supported Models

In addition to TFT, Quantis supports:

1. **Prophet**: Facebook's decomposable time series model that handles:
   - Multiple seasonality patterns
   - Holiday effects
   - Trend changepoints

2. **ARIMA/SARIMA**: Traditional statistical models for time series that capture:
   - Autoregressive components
   - Moving average components
   - Seasonal patterns

3. **XGBoost/LightGBM**: Gradient boosting models with engineered time features:
   - High performance on tabular data
   - Ability to capture non-linear relationships
   - Feature importance metrics

4. **DeepAR**: Recurrent neural network-based model:
   - Probabilistic forecasting
   - Handles multiple related time series
   - Captures complex patterns

## Model Training

### Training Process

The model training process in Quantis follows these steps:

1. **Data Preparation**:
   - Time series alignment
   - Feature engineering
   - Train/validation/test splitting
   - Normalization/scaling

2. **Hyperparameter Optimization**:
   - Automated hyperparameter tuning using Bayesian optimization
   - Cross-validation for robust evaluation
   - Early stopping to prevent overfitting

3. **Model Training**:
   - Distributed training for large datasets
   - Checkpointing for training resumption
   - Progress monitoring and logging

4. **Model Evaluation**:
   - Performance metrics calculation (MAPE, MAE, RMSE, etc.)
   - Comparison against baseline models
   - Backtesting on historical data

### Hyperparameter Tuning

Quantis uses a systematic approach to hyperparameter tuning:

1. **Optimization Strategy**: Bayesian optimization with Gaussian processes
2. **Search Space**: Model-specific parameter ranges defined by experts
3. **Objective Function**: Minimizing validation loss (typically quantile loss)
4. **Cross-Validation**: Time series cross-validation with expanding windows

Key hyperparameters for TFT include:

- Hidden layer sizes
- Number of attention heads
- Dropout rates
- Learning rate
- Batch size

### Training Configuration

Training can be configured through the UI or API with the following options:

```python
training_config = {
    "model_type": "tft",
    "hidden_size": 64,
    "attention_heads": 4,
    "dropout_rate": 0.1,
    "learning_rate": 0.001,
    "batch_size": 256,
    "max_epochs": 100,
    "early_stopping_patience": 10,
    "loss_function": "quantile",
    "quantiles": [0.1, 0.5, 0.9],
    "context_length": 30,  # Days of history to use
    "prediction_length": 14  # Days to forecast
}
```

## Model Serving

### Deployment Options

Quantis supports multiple deployment options for trained models:

1. **REST API**: Models are served via FastAPI endpoints for real-time predictions
2. **Batch Inference**: Scheduled batch processing for large-scale forecasting
3. **Edge Deployment**: Optimized models for edge devices (limited functionality)
4. **Embedded Python**: Models can be exported for use in external Python environments

### Serving Architecture

The model serving architecture consists of:

1. **Model Registry**: Central repository for trained models
2. **Serving Layer**: Scalable infrastructure for model inference
3. **Caching Layer**: Redis-based caching for frequent predictions
4. **Load Balancer**: Distributes requests across multiple model instances

### Scaling and Performance

To ensure high performance and scalability:

1. **Horizontal Scaling**: Multiple model instances behind a load balancer
2. **Model Optimization**: ONNX conversion for faster inference
3. **Batching**: Efficient processing of multiple prediction requests
4. **Resource Allocation**: Automatic scaling based on request volume

## Model Monitoring

### Performance Monitoring

Quantis continuously monitors model performance:

1. **Accuracy Metrics**: Tracking prediction errors over time
2. **Drift Detection**: Identifying shifts in data patterns
3. **Outlier Detection**: Flagging unusual predictions
4. **Comparison to Baselines**: Ensuring models outperform simple alternatives

### Alerting

The platform provides alerting capabilities:

1. **Accuracy Thresholds**: Alerts when error metrics exceed thresholds
2. **Drift Alerts**: Notifications when significant data drift is detected
3. **System Health**: Monitoring of model serving infrastructure
4. **Custom Metrics**: User-defined KPIs for business-specific monitoring

## Model Versioning

### Version Control

Quantis implements comprehensive model versioning:

1. **Immutable Versions**: Each trained model receives a unique version
2. **Metadata Storage**: Training parameters, dataset information, and performance metrics
3. **Lineage Tracking**: Recording of data and code used for each version
4. **A/B Testing**: Comparison of different model versions in production

### Promotion Workflow

The model promotion workflow includes:

1. **Development**: Initial training and experimentation
2. **Staging**: Validation on recent data
3. **Production**: Deployment for actual forecasting
4. **Rollback**: Ability to revert to previous versions if issues arise

## Custom Models

### Integration Process

Quantis supports custom model integration:

1. **Python Interface**: Standard interface for model implementation
2. **Container Support**: Docker-based deployment of custom models
3. **Framework Flexibility**: Support for PyTorch, TensorFlow, scikit-learn, etc.

### Custom Model Example

```python
from quantis.models import BaseModel

class CustomForecaster(BaseModel):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Initialize model components

    def fit(self, training_data, validation_data=None):
        # Implement training logic
        return self

    def predict(self, data, prediction_length):
        # Implement prediction logic
        return forecasts

    def save(self, path):
        # Save model artifacts

    @classmethod
    def load(cls, path):
        # Load model from artifacts
        return model_instance
```

## Best Practices

### Model Selection

Guidelines for selecting the appropriate model:

1. **Data Volume**:
   - Small datasets: Statistical models (ARIMA, ETS)
   - Large datasets: Deep learning models (TFT, DeepAR)

2. **Forecast Horizon**:
   - Short-term: Any model type
   - Long-term: Models with attention mechanisms (TFT)

3. **Interpretability Requirements**:
   - High interpretability: Prophet, ARIMA, TFT
   - Performance focus: XGBoost, LightGBM

4. **Seasonality Patterns**:
   - Simple seasonality: Most models
   - Multiple seasonality: Prophet, TFT

### Feature Engineering

Recommended features for time series forecasting:

1. **Temporal Features**:
   - Time of day, day of week, month, quarter
   - Holiday indicators
   - Special event flags

2. **Lag Features**:
   - Recent values (t-1, t-2, etc.)
   - Same period in previous cycles (last week, last year)

3. **Window Features**:
   - Rolling means, standard deviations
   - Rolling min/max values
   - Expanding window statistics

4. **External Variables**:
   - Weather data
   - Economic indicators
   - Related time series

### Model Tuning

Tips for optimizing model performance:

1. **Start Simple**: Begin with baseline models before complex ones
2. **Systematic Tuning**: Use automated hyperparameter optimization
3. **Cross-Validation**: Always use time series cross-validation
4. **Feature Selection**: Remove irrelevant features that cause noise
5. **Ensemble Methods**: Combine multiple models for better performance

## Technical Details

### Model Persistence

Models are serialized and stored using:

1. **Pickle/Joblib**: For scikit-learn and basic models
2. **TorchScript**: For PyTorch models
3. **SavedModel**: For TensorFlow models
4. **ONNX**: For framework-independent representation

### Resource Requirements

Typical resource requirements for different models:

| Model Type | Training Memory | Training Time | Inference Memory | Inference Time |
| ---------- | --------------- | ------------- | ---------------- | -------------- |
| ARIMA      | Low             | Fast          | Very Low         | Very Fast      |
| Prophet    | Medium          | Medium        | Low              | Fast           |
| XGBoost    | Medium          | Medium        | Low              | Very Fast      |
| TFT        | High            | Slow          | Medium           | Medium         |
| DeepAR     | High            | Slow          | Medium           | Medium         |

### Distributed Training

For large datasets, Quantis supports distributed training:

1. **Data Parallelism**: Training across multiple GPUs
2. **Horovod Integration**: Efficient distributed deep learning
3. **Ray Tune**: Distributed hyperparameter optimization

## References

1. Lim, B., Arık, S. Ö., Loeff, N., & Pfister, T. (2021). Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting. International Journal of Forecasting.

2. Taylor, S. J., & Letham, B. (2018). Forecasting at scale. The American Statistician, 72(1), 37-45.

3. Salinas, D., Flunkert, V., Gasthaus, J., & Januschowski, T. (2020). DeepAR: Probabilistic forecasting with autoregressive recurrent networks. International Journal of Forecasting, 36(3), 1181-1191.

4. Box, G. E., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). Time series analysis: forecasting and control. John Wiley & Sons.
