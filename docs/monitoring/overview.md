# Monitoring Documentation

This document provides comprehensive information about the monitoring and observability components of the Quantis time series forecasting platform, including system monitoring, model performance tracking, and alerting.

## Overview

The monitoring system in Quantis provides comprehensive observability into both the technical infrastructure and the machine learning models. It enables tracking of system health, model performance, data quality, and user activity to ensure reliable operation and continuous improvement of the platform.

## Monitoring Architecture

### Components

The monitoring architecture consists of several key components:

1. **Metrics Collection**: Gathering performance and operational metrics
2. **Logging System**: Capturing detailed logs for debugging and audit
3. **Model Monitoring**: Tracking ML model performance and behavior
4. **Alerting System**: Notifying stakeholders of issues
5. **Visualization**: Dashboards for monitoring and analysis

### Technology Stack

The monitoring system leverages the following technologies:

- **Prometheus**: Time series database for metrics collection
- **Grafana**: Visualization and dashboarding
- **ELK Stack** (optional): Log aggregation and analysis
- **Custom Model Monitor**: Specialized monitoring for ML models
- **AlertManager**: Alert routing and notification

## System Monitoring

### Infrastructure Metrics

Key infrastructure metrics monitored include:

1. **Resource Utilization**:
   - CPU usage (overall and per-process)
   - Memory usage and allocation
   - Disk space and I/O
   - Network throughput and latency

2. **Service Health**:
   - Service uptime and availability
   - Response times and error rates
   - Request throughput
   - Queue lengths and processing times

3. **Database Performance**:
   - Query performance
   - Connection pool utilization
   - Transaction rates
   - Index and cache efficiency

### Prometheus Configuration

The `prometheus.yml` configuration file defines what metrics to collect:

```yaml
# Global configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

# Alerting configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

# Rule files
rule_files:
  - "rules/system_alerts.yml"
  - "rules/model_alerts.yml"

# Scrape configurations
scrape_configs:
  # API service metrics
  - job_name: 'api'
    scrape_interval: 5s
    static_configs:
      - targets: ['api:8000']
    
  # Model service metrics
  - job_name: 'model_service'
    scrape_interval: 10s
    static_configs:
      - targets: ['model-service:8001']
    
  # Database metrics
  - job_name: 'database'
    static_configs:
      - targets: ['db-exporter:9187']
    
  # Node metrics (system-level)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    
  # Kubernetes metrics (if deployed on Kubernetes)
  - job_name: 'kubernetes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):10250'
        replacement: '${1}:9100'
        target_label: __address__
        action: replace
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
```

### Grafana Dashboards

Grafana dashboards provide visualization of system metrics:

1. **System Overview Dashboard**: High-level view of all components
2. **API Performance Dashboard**: Detailed metrics for the API service
3. **Database Dashboard**: Database performance and health
4. **Infrastructure Dashboard**: Underlying infrastructure metrics

Example dashboard configuration:

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "interval": "",
          "legendFormat": "{{method}} {{path}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "API Request Rate",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": "Requests/sec",
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 3,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, path))",
          "interval": "",
          "legendFormat": "{{path}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "API Response Time (p95)",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "s",
          "label": "Response Time",
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 22,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "API Performance",
  "uid": "api-performance",
  "version": 1
}
```

## Model Monitoring

### Model Performance Metrics

Key metrics for monitoring model performance:

1. **Accuracy Metrics**:
   - Mean Absolute Error (MAE)
   - Mean Absolute Percentage Error (MAPE)
   - Root Mean Square Error (RMSE)
   - R² (Coefficient of Determination)

2. **Prediction Characteristics**:
   - Prediction distribution
   - Confidence interval width
   - Prediction bias
   - Anomaly scores

3. **Operational Metrics**:
   - Prediction latency
   - Model loading time
   - Memory usage
   - Batch throughput

### Model Monitor Implementation

The `model_monitor.py` script implements model performance monitoring:

```python
# Example from model_monitor.py
import pandas as pd
import numpy as np
import time
import logging
import json
from datetime import datetime, timedelta
import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
PREDICTION_COUNT = Counter('model_predictions_total', 'Total number of predictions', ['model_id', 'model_version'])
PREDICTION_ERROR = Gauge('model_prediction_error', 'Prediction error metrics', ['model_id', 'model_version', 'metric_type'])
PREDICTION_LATENCY = Histogram('model_prediction_latency_seconds', 'Prediction latency in seconds', ['model_id', 'model_version'])
FEATURE_IMPORTANCE = Gauge('model_feature_importance', 'Feature importance scores', ['model_id', 'model_version', 'feature_name'])
DRIFT_SCORE = Gauge('model_drift_score', 'Data drift score', ['model_id', 'model_version', 'feature_name'])

class ModelMonitor:
    def __init__(self, config):
        self.config = config
        self.models_metadata = {}
        self.reference_data = {}
        self.current_data = {}
        
        # Start Prometheus metrics server
        start_http_server(config.get('metrics_port', 8002))
        logger.info(f"Started metrics server on port {config.get('metrics_port', 8002)}")
        
    def register_model(self, model_id, model_version, metadata=None):
        """Register a model for monitoring."""
        self.models_metadata[model_id] = {
            'version': model_version,
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        logger.info(f"Registered model {model_id} version {model_version} for monitoring")
        
    def load_reference_data(self, model_id, data_path):
        """Load reference data for drift detection."""
        try:
            self.reference_data[model_id] = pd.read_csv(data_path)
            logger.info(f"Loaded reference data for model {model_id} from {data_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading reference data for model {model_id}: {str(e)}")
            return False
    
    def record_prediction(self, model_id, features, prediction, actual=None, latency=None):
        """Record a single prediction for monitoring."""
        model_version = self.models_metadata.get(model_id, {}).get('version', 'unknown')
        
        # Update prediction counter
        PREDICTION_COUNT.labels(model_id=model_id, model_version=model_version).inc()
        
        # Record prediction latency
        if latency is not None:
            PREDICTION_LATENCY.labels(model_id=model_id, model_version=model_version).observe(latency)
        
        # Store features for drift detection
        if model_id not in self.current_data:
            self.current_data[model_id] = []
        
        self.current_data[model_id].append(features)
        
        # If we have actual values, calculate and record error metrics
        if actual is not None:
            error = abs(prediction - actual)
            percentage_error = abs(error / actual) if actual != 0 else float('inf')
            squared_error = error ** 2
            
            PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='mae').set(error)
            PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='mape').set(percentage_error * 100)
            PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='mse').set(squared_error)
            
            logger.debug(f"Recorded prediction error for model {model_id}: MAE={error}, MAPE={percentage_error*100}%")
    
    def record_batch_metrics(self, model_id, predictions, actuals, features_df):
        """Record metrics for a batch of predictions."""
        model_version = self.models_metadata.get(model_id, {}).get('version', 'unknown')
        
        # Calculate error metrics
        errors = np.abs(np.array(predictions) - np.array(actuals))
        percentage_errors = np.abs(errors / np.array(actuals))
        squared_errors = errors ** 2
        
        mae = np.mean(errors)
        mape = np.mean(percentage_errors) * 100
        rmse = np.sqrt(np.mean(squared_errors))
        
        # Record metrics
        PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='mae').set(mae)
        PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='mape').set(mape)
        PREDICTION_ERROR.labels(model_id=model_id, model_version=model_version, metric_type='rmse').set(rmse)
        
        # Update current data for drift detection
        if model_id not in self.current_data:
            self.current_data[model_id] = []
        
        self.current_data[model_id].extend(features_df.to_dict('records'))
        
        logger.info(f"Recorded batch metrics for model {model_id}: MAE={mae}, MAPE={mape}%, RMSE={rmse}")
    
    def record_feature_importance(self, model_id, feature_importance_dict):
        """Record feature importance scores."""
        model_version = self.models_metadata.get(model_id, {}).get('version', 'unknown')
        
        for feature_name, importance in feature_importance_dict.items():
            FEATURE_IMPORTANCE.labels(
                model_id=model_id, 
                model_version=model_version,
                feature_name=feature_name
            ).set(importance)
        
        logger.info(f"Recorded feature importance for model {model_id}")
    
    def detect_drift(self, model_id, method='ks', threshold=0.05):
        """Detect data drift between reference and current data."""
        if model_id not in self.reference_data or model_id not in self.current_data:
            logger.warning(f"Cannot detect drift for model {model_id}: missing reference or current data")
            return False
        
        model_version = self.models_metadata.get(model_id, {}).get('version', 'unknown')
        
        # Convert current data list to DataFrame
        current_df = pd.DataFrame(self.current_data[model_id])
        reference_df = self.reference_data[model_id]
        
        drift_detected = False
        
        # Check each numerical feature for drift
        for feature in reference_df.select_dtypes(include=['number']).columns:
            if feature in current_df.columns:
                # Calculate drift score based on method
                if method == 'ks':
                    from scipy.stats import ks_2samp
                    stat, p_value = ks_2samp(reference_df[feature].dropna(), current_df[feature].dropna())
                    drift_score = 1 - p_value  # Higher score = more drift
                elif method == 'js':
                    # Jensen-Shannon divergence (simplified implementation)
                    from scipy.spatial.distance import jensenshannon
                    from numpy import histogram
                    
                    # Create histograms with same bins
                    min_val = min(reference_df[feature].min(), current_df[feature].min())
                    max_val = max(reference_df[feature].max(), current_df[feature].max())
                    bins = np.linspace(min_val, max_val, 20)
                    
                    ref_hist, _ = histogram(reference_df[feature].dropna(), bins=bins, density=True)
                    cur_hist, _ = histogram(current_df[feature].dropna(), bins=bins, density=True)
                    
                    # Add small epsilon to avoid division by zero
                    ref_hist = ref_hist + 1e-10
                    cur_hist = cur_hist + 1e-10
                    
                    # Normalize
                    ref_hist = ref_hist / ref_hist.sum()
                    cur_hist = cur_hist / cur_hist.sum()
                    
                    drift_score = jensenshannon(ref_hist, cur_hist)
                else:
                    logger.warning(f"Unknown drift detection method: {method}")
                    continue
                
                # Record drift score
                DRIFT_SCORE.labels(
                    model_id=model_id,
                    model_version=model_version,
                    feature_name=feature
                ).set(drift_score)
                
                # Check if drift exceeds threshold
                if drift_score > threshold:
                    drift_detected = True
                    logger.warning(f"Drift detected for model {model_id}, feature {feature}: score={drift_score}")
        
        return drift_detected
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle for all registered models."""
        for model_id in self.models_metadata:
            try:
                # Detect drift if we have enough data
                if model_id in self.current_data and len(self.current_data[model_id]) >= self.config.get('min_samples_for_drift', 100):
                    drift_detected = self.detect_drift(
                        model_id, 
                        method=self.config.get('drift_method', 'ks'),
                        threshold=self.config.get('drift_threshold', 0.05)
                    )
                    
                    if drift_detected and self.config.get('alert_on_drift', True):
                        self._send_alert(
                            model_id=model_id,
                            alert_type='drift',
                            message=f"Data drift detected for model {model_id}"
                        )
                
                # Check performance if we have a performance endpoint configured
                if self.config.get('performance_endpoint'):
                    self._fetch_and_record_performance(model_id)
            
            except Exception as e:
                logger.error(f"Error in monitoring cycle for model {model_id}: {str(e)}")
    
    def _fetch_and_record_performance(self, model_id):
        """Fetch performance metrics from API and record them."""
        try:
            response = requests.get(
                f"{self.config['performance_endpoint']}/models/{model_id}/performance",
                headers=self.config.get('api_headers', {})
            )
            
            if response.status_code == 200:
                performance = response.json()
                
                # Record performance metrics
                for metric_type, value in performance.get('metrics', {}).items():
                    PREDICTION_ERROR.labels(
                        model_id=model_id,
                        model_version=self.models_metadata[model_id]['version'],
                        metric_type=metric_type
                    ).set(value)
                
                # Record feature importance if available
                if 'feature_importance' in performance:
                    self.record_feature_importance(model_id, performance['feature_importance'])
                
                logger.info(f"Recorded performance metrics for model {model_id}")
            else:
                logger.warning(f"Failed to fetch performance for model {model_id}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching performance for model {model_id}: {str(e)}")
    
    def _send_alert(self, model_id, alert_type, message):
        """Send an alert through configured channels."""
        if 'alert_webhook' in self.config:
            try:
                alert_data = {
                    'model_id': model_id,
                    'model_version': self.models_metadata[model_id]['version'],
                    'alert_type': alert_type,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    self.config['alert_webhook'],
                    json=alert_data,
                    headers=self.config.get('webhook_headers', {})
                )
                
                if response.status_code < 200 or response.status_code >= 300:
                    logger.warning(f"Alert webhook returned non-success status: {response.status_code}")
            
            except Exception as e:
                logger.error(f"Error sending alert to webhook: {str(e)}")
        
        logger.warning(f"ALERT: {message}")


if __name__ == "__main__":
    # Example configuration
    config = {
        'metrics_port': 8002,
        'min_samples_for_drift': 100,
        'drift_method': 'ks',
        'drift_threshold': 0.05,
        'alert_on_drift': True,
        'alert_webhook': 'http://alerts-service:8080/api/alerts',
        'performance_endpoint': 'http://api:8000/api',
        'monitoring_interval': 300  # seconds
    }
    
    monitor = ModelMonitor(config)
    
    # Register models
    monitor.register_model('tft-sales', '1.0.0', {'description': 'TFT model for sales forecasting'})
    
    # Load reference data
    monitor.load_reference_data('tft-sales', 'data/reference/sales_reference.csv')
    
    # Main monitoring loop
    try:
        while True:
            monitor.run_monitoring_cycle()
            logger.info(f"Completed monitoring cycle, sleeping for {config['monitoring_interval']} seconds")
            time.sleep(config['monitoring_interval'])
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
```

### Model Performance Dashboard

The Grafana dashboard for model performance visualization:

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 2,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": true,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "model_prediction_error{metric_type=\"mape\"}",
          "interval": "",
          "legendFormat": "{{model_id}} ({{model_version}})",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Model MAPE (%)",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "percent",
          "label": "MAPE",
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 3,
      "legend": {
        "avg": false,
        "current": true,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "model_prediction_error{metric_type=\"rmse\"}",
          "interval": "",
          "legendFormat": "{{model_id}} ({{model_version}})",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Model RMSE",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": "RMSE",
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 4,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(model_predictions_total[5m])",
          "interval": "",
          "legendFormat": "{{model_id}} ({{model_version}})",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Prediction Rate",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": "Predictions/sec",
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 5,
      "legend": {
        "avg": false,
        "current": true,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(model_prediction_latency_seconds_bucket[5m])) by (le, model_id, model_version))",
          "interval": "",
          "legendFormat": "{{model_id}} ({{model_version}})",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Prediction Latency (p95)",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "s",
          "label": "Latency",
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": true,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 16
      },
      "hiddenSeries": false,
      "id": 6,
      "legend": {
        "avg": false,
        "current": true,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": false,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "model_feature_importance{model_id=\"tft-sales\"}",
          "interval": "",
          "legendFormat": "{{feature_name}}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Feature Importance (TFT Sales Model)",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "series",
        "name": null,
        "show": true,
        "values": ["current"]
      },
      "yaxes": [
        {
          "format": "short",
          "label": "Importance",
          "logBase": 1,
          "max": null,
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 16
      },
      "hiddenSeries": false,
      "id": 7,
      "legend": {
        "avg": false,
        "current": true,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": true
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "model_drift_score{model_id=\"tft-sales\"}",
          "interval": "",
          "legendFormat": "{{feature_name}}",
          "refId": "A"
        }
      ],
      "thresholds": [
        {
          "colorMode": "critical",
          "fill": true,
          "line": true,
          "op": "gt",
          "value": 0.05,
          "yaxis": "left"
        }
      ],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Feature Drift Score",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": "Drift Score",
          "logBase": 1,
          "max": "1",
          "min": "0",
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "schemaVersion": 22,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-24h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "Model Performance",
  "uid": "model-performance",
  "version": 1
}
```

## Logging System

### Log Structure

Quantis uses structured logging with the following fields:

1. **Timestamp**: When the log was generated
2. **Level**: Severity level (INFO, WARNING, ERROR, etc.)
3. **Service**: Which component generated the log
4. **TraceID**: Unique identifier for request tracing
5. **Message**: Human-readable log message
6. **Context**: Additional structured data relevant to the log

Example log entry:

```json
{
  "timestamp": "2023-04-10T15:23:45.123Z",
  "level": "INFO",
  "service": "api",
  "trace_id": "abc123def456",
  "message": "Prediction request processed successfully",
  "context": {
    "user_id": "user123",
    "model_id": "tft-sales",
    "prediction_id": "pred789",
    "execution_time_ms": 125
  }
}
```

### Log Aggregation

Logs are aggregated using:

1. **Filebeat**: Collects logs from files
2. **Logstash**: Processes and transforms logs
3. **Elasticsearch**: Stores and indexes logs
4. **Kibana**: Visualizes and searches logs

## Alerting System

### Alert Types

The monitoring system generates several types of alerts:

1. **System Alerts**:
   - High resource utilization
   - Service unavailability
   - Database performance issues
   - Network problems

2. **Model Alerts**:
   - Accuracy degradation
   - Data drift detected
   - Prediction latency increases
   - Feature importance shifts

3. **Data Alerts**:
   - Data quality issues
   - Missing data
   - Outlier detection
   - Schema changes

### Alert Configuration

Alerts are configured in Prometheus AlertManager:

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-email'
  routes:
  - match:
      severity: critical
    receiver: 'pager'
    continue: true
  - match:
      category: model
    receiver: 'data-science-team'

receivers:
- name: 'team-email'
  email_configs:
  - to: 'team@quantis.example.com'
    send_resolved: true

- name: 'pager'
  pagerduty_configs:
  - service_key: '<pagerduty-service-key>'
    send_resolved: true

- name: 'data-science-team'
  slack_configs:
  - api_url: '<slack-webhook-url>'
    channel: '#data-science-alerts'
    send_resolved: true

inhibit_rules:
- source_match:
    severity: 'critical'
  target_match:
    severity: 'warning'
  equal: ['alertname', 'service']
```

### Alert Rules

Alert rules are defined in Prometheus:

```yaml
# system_alerts.yml
groups:
- name: system
  rules:
  - alert: HighCpuUsage
    expr: avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) < 0.2
    for: 5m
    labels:
      severity: warning
      category: system
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% for 5 minutes"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
    for: 5m
    labels:
      severity: warning
      category: system
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is above 90% for 5 minutes"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
      category: system
    annotations:
      summary: "Service {{ $labels.job }} is down"
      description: "Service has been down for more than 1 minute"

# model_alerts.yml
groups:
- name: models
  rules:
  - alert: HighModelError
    expr: model_prediction_error{metric_type="mape"} > 15
    for: 30m
    labels:
      severity: warning
      category: model
    annotations:
      summary: "High error rate for model {{ $labels.model_id }}"
      description: "MAPE is above 15% for 30 minutes"

  - alert: DataDriftDetected
    expr: max by(model_id, feature_name) (model_drift_score) > 0.05
    for: 1h
    labels:
      severity: warning
      category: model
    annotations:
      summary: "Data drift detected for model {{ $labels.model_id }}"
      description: "Feature {{ $labels.feature_name }} shows significant drift"

  - alert: SlowPredictions
    expr: histogram_quantile(0.95, sum(rate(model_prediction_latency_seconds_bucket[5m])) by (le, model_id)) > 0.5
    for: 15m
    labels:
      severity: warning
      category: model
    annotations:
      summary: "Slow predictions for model {{ $labels.model_id }}"
      description: "95th percentile prediction latency is above 500ms for 15 minutes"
```

## User Activity Monitoring

### User Metrics

The system tracks user activity metrics:

1. **Active Users**: Number of active users over time
2. **API Usage**: API calls per user/endpoint
3. **Feature Usage**: Which features are most used
4. **Session Duration**: How long users stay active
5. **Error Rates**: Errors encountered by users

### User Journey Tracking

For understanding user workflows:

1. **Funnel Analysis**: Track completion of multi-step processes
2. **Page Flow**: Analyze navigation patterns
3. **Feature Adoption**: Monitor new feature usage
4. **Retention Analysis**: Track returning users

## Security Monitoring

### Security Metrics

Security-related metrics monitored include:

1. **Authentication Events**: Successful and failed login attempts
2. **Authorization Checks**: Access control decisions
3. **Rate Limiting**: API rate limit hits
4. **Suspicious Activity**: Unusual access patterns
5. **Data Access Patterns**: Who accessed what data and when

### Audit Logging

Comprehensive audit logging for security and compliance:

1. **User Actions**: All significant user actions
2. **System Changes**: Configuration and deployment changes
3. **Data Access**: Records of data access and modification
4. **Authentication Events**: Login/logout and permission changes

## Integration with MLOps

### Model Lifecycle Monitoring

Monitoring throughout the model lifecycle:

1. **Training Monitoring**: Resource usage, convergence, metrics
2. **Validation Monitoring**: Performance on validation datasets
3. **Deployment Monitoring**: Deployment success and rollbacks
4. **Production Monitoring**: Real-world performance

### Experiment Tracking

Integration with experiment tracking:

1. **Hyperparameter Correlation**: Link parameters to performance
2. **Model Comparison**: Compare different model versions
3. **Dataset Versioning**: Track which data was used for training
4. **Reproducibility**: Ensure experiments can be reproduced

## Best Practices

### Monitoring Implementation

1. **Start Simple**: Begin with essential metrics
2. **Iterative Improvement**: Add more sophisticated monitoring over time
3. **Automate Responses**: Set up automated actions for common issues
4. **Regular Reviews**: Periodically review monitoring effectiveness
5. **Documentation**: Keep monitoring documentation up to date

### Alert Management

1. **Minimize Alert Fatigue**: Only alert on actionable issues
2. **Clear Ownership**: Define who is responsible for each alert
3. **Runbooks**: Create clear procedures for handling alerts
4. **Post-Mortems**: Learn from incidents to improve monitoring
5. **Escalation Paths**: Define clear escalation procedures

### Performance Optimization

1. **Sampling**: Use sampling for high-volume metrics
2. **Aggregation**: Pre-aggregate metrics where possible
3. **Retention Policies**: Define appropriate data retention periods
4. **Resource Allocation**: Ensure monitoring systems have adequate resources
5. **Cardinality Management**: Control the number of unique time series

## References

1. Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J. F., & Dennison, D. (2015). Hidden technical debt in machine learning systems. In Advances in neural information processing systems (pp. 2503-2511).

2. Breck, E., Cai, S., Nielsen, E., Salib, M., & Sculley, D. (2017). The ML test score: A rubric for ML production readiness and technical debt reduction. In 2017 IEEE International Conference on Big Data (Big Data) (pp. 1123-1132). IEEE.

3. Klaise, J., Van Looveren, A., Vacanti, G., & Coca, A. (2020). Monitoring and explainability of models in production. arXiv preprint arXiv:2007.06299.

4. Prometheus Documentation: https://prometheus.io/docs/introduction/overview/

5. Grafana Documentation: https://grafana.com/docs/grafana/latest/
