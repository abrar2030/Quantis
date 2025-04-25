# Data Processing Documentation

This document provides comprehensive information about the data processing components of the Quantis time series forecasting platform, including data pipelines, feature engineering, and data management.

## Overview

The data processing module in Quantis is responsible for ingesting, cleaning, transforming, and preparing time series data for model training and inference. It ensures that data is in the correct format, handles missing values and outliers, and generates features that enhance model performance.

## Data Architecture

### Data Flow

The data processing pipeline follows these key steps:

1. **Data Ingestion**: Raw data is collected from various sources
2. **Data Validation**: Data is checked for quality and completeness
3. **Data Cleaning**: Missing values and outliers are handled
4. **Feature Engineering**: Features are created to enhance model performance
5. **Data Transformation**: Data is transformed into the format required by models
6. **Data Storage**: Processed data is stored for model training and inference

### Directory Structure

The data processing code is organized as follows:

```
data/
├── raw/                  # Storage for raw input data
├── processed/            # Storage for processed data
├── features/             # Feature engineering code
│   └── feature_store.py  # Feature store implementation
└── process_data.py       # Main data processing pipeline
```

## Data Ingestion

### Supported Data Sources

Quantis supports ingesting data from multiple sources:

1. **File Uploads**: CSV, Excel, JSON, and Parquet files
2. **Databases**: SQL databases via JDBC/ODBC connections
3. **APIs**: REST and GraphQL APIs
4. **Streaming Sources**: Kafka, Kinesis, and other streaming platforms
5. **Cloud Storage**: S3, Azure Blob Storage, Google Cloud Storage

### Data Formats

The platform expects time series data to include:

- **Timestamp Column**: Date/time values in ISO format or epoch timestamps
- **Target Column**: The value to be forecasted
- **Optional Feature Columns**: Additional variables that may influence the target

Example CSV format:

```csv
timestamp,sales,temperature,is_holiday,promotion
2023-01-01T00:00:00Z,1250,32,1,0
2023-01-02T00:00:00Z,1100,30,0,0
2023-01-03T00:00:00Z,1300,28,0,1
...
```

### Ingestion Configuration

Data ingestion can be configured through the API or configuration files:

```python
ingestion_config = {
    "source_type": "csv",
    "source_path": "data/raw/sales_data.csv",
    "timestamp_column": "timestamp",
    "timestamp_format": "ISO",  # or "epoch", "custom"
    "custom_timestamp_format": "%Y-%m-%d %H:%M:%S",  # if format is "custom"
    "target_column": "sales",
    "feature_columns": ["temperature", "is_holiday", "promotion"],
    "categorical_columns": ["is_holiday", "promotion"],
    "id_column": None,  # for panel data with multiple time series
}
```

## Data Validation

### Quality Checks

The data validation process performs several checks:

1. **Schema Validation**: Ensures data has the expected columns and types
2. **Timestamp Validation**: Checks for proper timestamp formatting and ordering
3. **Range Validation**: Verifies values are within expected ranges
4. **Completeness Check**: Identifies missing values and gaps in time series
5. **Duplicate Detection**: Finds and handles duplicate timestamps

### Validation Rules

Validation rules can be customized for each dataset:

```python
validation_rules = {
    "sales": {
        "min_value": 0,
        "max_value": 10000,
        "allow_missing": False
    },
    "temperature": {
        "min_value": -50,
        "max_value": 150,
        "allow_missing": True
    },
    "is_holiday": {
        "allowed_values": [0, 1],
        "allow_missing": False
    }
}
```

### Validation Reports

After validation, a report is generated with statistics and issues:

```json
{
  "validation_summary": {
    "total_rows": 1000,
    "valid_rows": 980,
    "invalid_rows": 20,
    "missing_values": {
      "sales": 0,
      "temperature": 5,
      "is_holiday": 0,
      "promotion": 0
    },
    "out_of_range_values": {
      "sales": 3,
      "temperature": 0,
      "is_holiday": 0,
      "promotion": 0
    },
    "duplicate_timestamps": 2
  },
  "validation_status": "WARNING",
  "recommendations": [
    "Consider imputing missing temperature values",
    "Investigate sales outliers at timestamps: 2023-01-15, 2023-02-20, 2023-03-10"
  ]
}
```

## Data Cleaning

### Handling Missing Values

Quantis provides several strategies for handling missing values:

1. **Removal**: Remove rows with missing values
2. **Forward Fill**: Propagate last valid observation forward
3. **Backward Fill**: Use next valid observation
4. **Linear Interpolation**: Interpolate linearly between valid points
5. **Mean/Median/Mode**: Replace with statistical measures
6. **Custom Imputation**: Use domain-specific logic or models

Example configuration:

```python
missing_value_strategy = {
    "sales": "linear_interpolation",
    "temperature": "mean",
    "is_holiday": "mode",
    "promotion": "zero"
}
```

### Outlier Detection and Handling

For outlier detection, the platform supports:

1. **Statistical Methods**: Z-score, IQR, DBSCAN
2. **Machine Learning**: Isolation Forest, One-Class SVM
3. **Time Series Specific**: Seasonal Hybrid ESD (S-H-ESD)

Outlier handling options include:

1. **Removal**: Remove outlier points
2. **Capping**: Cap values at specified percentiles
3. **Interpolation**: Replace with interpolated values
4. **Flagging**: Keep but flag for model awareness

Example configuration:

```python
outlier_config = {
    "detection_method": "iqr",  # z_score, iqr, isolation_forest
    "threshold": 1.5,  # for IQR method
    "handling_strategy": "capping",  # removal, capping, interpolation, flagging
    "apply_to_columns": ["sales", "temperature"]
}
```

### Time Series Specific Cleaning

Additional cleaning steps for time series data:

1. **Resampling**: Convert to regular time intervals
2. **Gap Filling**: Handle missing timestamps
3. **Seasonality Adjustment**: Remove or normalize seasonal patterns
4. **Trend Adjustment**: Detrend data if needed
5. **Smoothing**: Apply moving averages or other smoothing techniques

## Feature Engineering

### Temporal Features

Automatically generated temporal features:

1. **Calendar Features**:
   - Hour of day, day of week, day of month, month, quarter, year
   - Is weekend, is holiday, is end of month
   - Week of year, day of year

2. **Lag Features**:
   - Previous values (t-1, t-2, t-3, etc.)
   - Same time last week, month, year
   - Custom lag periods

3. **Window Features**:
   - Rolling mean, median, min, max
   - Rolling standard deviation, variance
   - Rolling quantiles
   - Expanding window statistics

4. **Seasonal Features**:
   - Fourier terms for different frequencies
   - Seasonal indicators
   - Cyclical encodings of time features

### Feature Store

The feature store manages feature creation and storage:

```python
# Example from feature_store.py
class FeatureStore:
    def __init__(self, config):
        self.config = config
        self.features = {}
        
    def add_feature(self, feature_name, feature_type, params):
        """Add a feature definition to the store."""
        self.features[feature_name] = {
            "type": feature_type,
            "params": params,
            "created_at": datetime.now().isoformat()
        }
        
    def generate_features(self, df):
        """Generate all registered features for a dataframe."""
        result = df.copy()
        
        for feature_name, feature_config in self.features.items():
            if feature_config["type"] == "lag":
                result = self._create_lag_feature(
                    result, 
                    feature_config["params"]["column"],
                    feature_config["params"]["lag_periods"],
                    feature_name
                )
            elif feature_config["type"] == "rolling":
                result = self._create_rolling_feature(
                    result,
                    feature_config["params"]["column"],
                    feature_config["params"]["window"],
                    feature_config["params"]["function"],
                    feature_name
                )
            # Additional feature types...
            
        return result
    
    def _create_lag_feature(self, df, column, lag_periods, feature_name):
        """Create lag features for a column."""
        df[feature_name] = df[column].shift(lag_periods)
        return df
    
    def _create_rolling_feature(self, df, column, window, function, feature_name):
        """Create rolling window features for a column."""
        if function == "mean":
            df[feature_name] = df[column].rolling(window=window).mean()
        elif function == "std":
            df[feature_name] = df[column].rolling(window=window).std()
        # Additional functions...
        
        return df
```

### Feature Selection

Methods for selecting the most relevant features:

1. **Statistical Tests**: Correlation analysis, chi-squared tests
2. **Model-Based**: Feature importance from tree-based models
3. **Wrapper Methods**: Recursive feature elimination
4. **Embedded Methods**: L1 regularization (Lasso)

## Data Transformation

### Scaling and Normalization

Supported scaling methods:

1. **Min-Max Scaling**: Scale to range [0, 1]
2. **Standard Scaling**: Zero mean, unit variance
3. **Robust Scaling**: Based on median and quantiles
4. **Log Transformation**: For skewed distributions
5. **Box-Cox Transformation**: For non-normal distributions

### Encoding Categorical Variables

Methods for encoding categorical features:

1. **One-Hot Encoding**: Binary columns for each category
2. **Label Encoding**: Integer representation
3. **Target Encoding**: Replace with target mean
4. **Frequency Encoding**: Replace with frequency
5. **Embedding**: For high-cardinality features

### Time Series Specific Transformations

Transformations specific to time series data:

1. **Differencing**: First or seasonal differences
2. **Decomposition**: Trend, seasonality, and residual components
3. **Spectral Transformations**: Fourier and wavelet transforms

## Data Pipeline Implementation

### Main Processing Pipeline

The `process_data.py` script implements the main data processing pipeline:

```python
# Example from process_data.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from features.feature_store import FeatureStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.feature_store = FeatureStore(config.get("feature_store", {}))
        
    def run_pipeline(self, input_path, output_path):
        """Run the complete data processing pipeline."""
        logger.info(f"Starting data processing pipeline for {input_path}")
        
        # Step 1: Load data
        df = self.load_data(input_path)
        logger.info(f"Loaded data with shape {df.shape}")
        
        # Step 2: Validate data
        validation_result = self.validate_data(df)
        if validation_result["validation_status"] == "ERROR":
            logger.error("Data validation failed")
            return validation_result
        
        # Step 3: Clean data
        df = self.clean_data(df)
        logger.info(f"Data cleaned, new shape {df.shape}")
        
        # Step 4: Generate features
        df = self.generate_features(df)
        logger.info(f"Features generated, final shape {df.shape}")
        
        # Step 5: Transform data
        df = self.transform_data(df)
        logger.info("Data transformation completed")
        
        # Step 6: Save processed data
        self.save_data(df, output_path)
        logger.info(f"Processed data saved to {output_path}")
        
        return {
            "status": "success",
            "rows_processed": len(df),
            "features_created": len(df.columns) - len(self.config["feature_columns"]) - 2,
            "output_path": output_path
        }
    
    def load_data(self, input_path):
        """Load data from the specified source."""
        source_type = self.config["source_type"]
        
        if source_type == "csv":
            return pd.read_csv(input_path, parse_dates=[self.config["timestamp_column"]])
        elif source_type == "excel":
            return pd.read_excel(input_path, parse_dates=[self.config["timestamp_column"]])
        elif source_type == "json":
            return pd.read_json(input_path, convert_dates=[self.config["timestamp_column"]])
        # Additional source types...
    
    def validate_data(self, df):
        """Validate the input data."""
        # Implementation of validation logic
        # ...
        
    def clean_data(self, df):
        """Clean the data by handling missing values and outliers."""
        # Handle missing values
        for column, strategy in self.config.get("missing_value_strategy", {}).items():
            if column in df.columns:
                if strategy == "remove":
                    df = df.dropna(subset=[column])
                elif strategy == "forward_fill":
                    df[column] = df[column].ffill()
                elif strategy == "backward_fill":
                    df[column] = df[column].bfill()
                elif strategy == "linear_interpolation":
                    df[column] = df[column].interpolate(method='linear')
                elif strategy == "mean":
                    df[column] = df[column].fillna(df[column].mean())
                elif strategy == "median":
                    df[column] = df[column].fillna(df[column].median())
                elif strategy == "mode":
                    df[column] = df[column].fillna(df[column].mode()[0])
                elif strategy == "zero":
                    df[column] = df[column].fillna(0)
        
        # Handle outliers
        outlier_config = self.config.get("outlier_config", {})
        if outlier_config:
            for column in outlier_config.get("apply_to_columns", []):
                if column in df.columns:
                    if outlier_config["detection_method"] == "iqr":
                        Q1 = df[column].quantile(0.25)
                        Q3 = df[column].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - outlier_config["threshold"] * IQR
                        upper_bound = Q3 + outlier_config["threshold"] * IQR
                        
                        if outlier_config["handling_strategy"] == "removal":
                            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                        elif outlier_config["handling_strategy"] == "capping":
                            df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
                            df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
                        # Additional handling strategies...
        
        return df
    
    def generate_features(self, df):
        """Generate features for the dataset."""
        # Set timestamp as index if not already
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.set_index(self.config["timestamp_column"])
        
        # Generate temporal features
        if self.config.get("generate_temporal_features", True):
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['day_of_month'] = df.index.day
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['year'] = df.index.year
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Generate features from feature store
        df = self.feature_store.generate_features(df)
        
        # Reset index to get timestamp as column again
        df = df.reset_index()
        
        return df
    
    def transform_data(self, df):
        """Apply transformations to prepare data for modeling."""
        # Scaling numerical features
        scaling_config = self.config.get("scaling", {})
        for column, method in scaling_config.items():
            if column in df.columns:
                if method == "min_max":
                    min_val = df[column].min()
                    max_val = df[column].max()
                    df[column] = (df[column] - min_val) / (max_val - min_val)
                elif method == "standard":
                    mean = df[column].mean()
                    std = df[column].std()
                    df[column] = (df[column] - mean) / std
                # Additional scaling methods...
        
        # Encoding categorical features
        encoding_config = self.config.get("encoding", {})
        for column, method in encoding_config.items():
            if column in df.columns:
                if method == "one_hot":
                    one_hot = pd.get_dummies(df[column], prefix=column)
                    df = pd.concat([df.drop(column, axis=1), one_hot], axis=1)
                elif method == "label":
                    df[column] = df[column].astype('category').cat.codes
                # Additional encoding methods...
        
        return df
    
    def save_data(self, df, output_path):
        """Save the processed data to the specified location."""
        output_format = self.config.get("output_format", "csv")
        
        if output_format == "csv":
            df.to_csv(output_path, index=False)
        elif output_format == "parquet":
            df.to_parquet(output_path, index=False)
        elif output_format == "pickle":
            df.to_pickle(output_path)
        # Additional output formats...


if __name__ == "__main__":
    # Example configuration
    config = {
        "source_type": "csv",
        "timestamp_column": "timestamp",
        "target_column": "sales",
        "feature_columns": ["temperature", "is_holiday", "promotion"],
        "categorical_columns": ["is_holiday", "promotion"],
        "missing_value_strategy": {
            "sales": "linear_interpolation",
            "temperature": "mean",
            "is_holiday": "mode",
            "promotion": "zero"
        },
        "outlier_config": {
            "detection_method": "iqr",
            "threshold": 1.5,
            "handling_strategy": "capping",
            "apply_to_columns": ["sales", "temperature"]
        },
        "generate_temporal_features": True,
        "scaling": {
            "sales": "min_max",
            "temperature": "standard"
        },
        "encoding": {
            "is_holiday": "one_hot",
            "promotion": "one_hot"
        },
        "output_format": "csv",
        "feature_store": {
            "enabled": True,
            "storage_path": "data/features/store"
        }
    }
    
    processor = DataProcessor(config)
    result = processor.run_pipeline(
        input_path="data/raw/sales_data.csv",
        output_path="data/processed/sales_data_processed.csv"
    )
    
    print(result)
```

## Data Quality Monitoring

### Drift Detection

Methods for detecting data drift:

1. **Statistical Tests**: Kolmogorov-Smirnov, Chi-squared
2. **Distribution Metrics**: JS divergence, Wasserstein distance
3. **Visualization**: QQ plots, distribution comparisons

### Data Quality Metrics

Key metrics for monitoring data quality:

1. **Completeness**: Percentage of non-missing values
2. **Timeliness**: Recency of data
3. **Consistency**: Adherence to business rules
4. **Accuracy**: Comparison with ground truth (when available)
5. **Uniqueness**: Absence of duplicates

### Alerting

Alerts are triggered when:

1. Data quality metrics fall below thresholds
2. Significant data drift is detected
3. Pipeline failures occur
4. Data volume anomalies are detected

## Best Practices

### Data Processing Guidelines

1. **Start Simple**: Begin with basic cleaning and features
2. **Validate Early**: Check data quality before complex processing
3. **Document Transformations**: Keep track of all data changes
4. **Version Data**: Maintain versioned datasets for reproducibility
5. **Test Incrementally**: Validate each processing step

### Feature Engineering Tips

1. **Domain Knowledge**: Incorporate business understanding
2. **Feature Importance**: Regularly evaluate feature usefulness
3. **Feature Stability**: Monitor feature distributions over time
4. **Avoid Leakage**: Ensure features don't leak target information
5. **Balance Complexity**: More features aren't always better

### Performance Optimization

1. **Chunking**: Process large datasets in chunks
2. **Parallelization**: Use multiprocessing for independent operations
3. **Efficient Storage**: Use appropriate file formats (Parquet, HDF5)
4. **Incremental Processing**: Only process new or changed data
5. **Caching**: Cache intermediate results

## Advanced Topics

### Handling Multiple Time Series

Strategies for processing multiple related time series:

1. **Panel Data Structure**: Organize with entity and time dimensions
2. **Hierarchical Modeling**: Account for hierarchical relationships
3. **Cross-Series Features**: Create features that leverage related series
4. **Global vs. Local Processing**: Balance shared and series-specific processing

### Handling Irregular Time Series

Approaches for non-uniform time intervals:

1. **Event-Based Features**: Focus on events rather than regular intervals
2. **Gaussian Processes**: Model continuous time functions
3. **Point Process Models**: Model event occurrence directly
4. **Custom Resampling**: Domain-specific resampling strategies

### Online Learning

Supporting continuous model updates:

1. **Streaming Data Processing**: Handle data in real-time
2. **Incremental Feature Updates**: Update features without full recomputation
3. **Feature Store Versioning**: Track feature definitions and values over time

## References

1. Hyndman, R.J., & Athanasopoulos, G. (2018). Forecasting: principles and practice. OTexts.

2. De Prado, M.L. (2018). Advances in financial machine learning. John Wiley & Sons.

3. Christ, M., Braun, N., Neuffer, J., & Kempa-Liehr, A.W. (2018). Time series feature extraction on basis of scalable hypothesis tests (tsfresh–a Python package). Neurocomputing, 307, 72-77.

4. Kanter, J.M., & Veeramachaneni, K. (2015). Deep feature synthesis: Towards automating data science endeavors. In 2015 IEEE International Conference on Data Science and Advanced Analytics (DSAA) (pp. 1-10). IEEE.
