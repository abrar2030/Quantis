# User Manual

This comprehensive user manual provides detailed instructions for using the Quantis time series forecasting platform. It covers all aspects of the platform from basic navigation to advanced forecasting features.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Data Management](#data-management)
5. [Creating Forecasts](#creating-forecasts)
6. [Analyzing Results](#analyzing-results)
7. [Model Management](#model-management)
8. [Account Settings](#account-settings)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Introduction

Quantis is an advanced time series forecasting platform that leverages machine learning to provide accurate predictions and valuable insights. The platform is designed for data scientists, business analysts, and decision-makers who need reliable forecasts for planning and strategy.

### Key Features

Quantis offers a comprehensive set of features for time series forecasting:

- Interactive dashboards with customizable visualizations
- Advanced machine learning models for accurate predictions
- Feature importance analysis to understand driving factors
- Model version tracking for reproducibility
- API integration for automated workflows
- Comprehensive monitoring and alerting

### Use Cases

Quantis is suitable for a wide range of forecasting applications:

- Demand forecasting for inventory management
- Financial forecasting for budgeting and planning
- Energy consumption prediction
- Website traffic forecasting
- Sales and revenue projections
- Resource allocation planning

## Getting Started

### Accessing the Platform

Quantis can be accessed through your web browser at the URL provided by your administrator. For local installations, the default URL is http://localhost:3000.

### Logging In

1. Navigate to the Quantis login page
2. Enter your username and password
3. Click the "Log In" button

If you don't have an account, contact your administrator or click the "Register" link if self-registration is enabled.

### First-Time Setup

Upon first login, you'll be guided through a setup wizard to:

1. Configure your user profile
2. Set notification preferences
3. Connect to data sources (optional)
4. Take a brief tour of the platform

## Dashboard Overview

The Quantis dashboard provides a comprehensive view of your forecasting projects and key metrics.

### Navigation

The main navigation menu is located on the left side of the screen and includes:

- **Dashboard**: Overview of recent activity and key metrics
- **Data**: Data management and import functionality
- **Models**: Model training and management
- **Predictions**: Create and view forecasts
- **Settings**: User and system configuration
- **Documentation**: Access to help resources

### Dashboard Widgets

The dashboard contains several widgets that can be customized:

- **Recent Forecasts**: Shows your most recent forecasting projects
- **Model Performance**: Displays performance metrics for your models
- **Data Health**: Indicates the quality and completeness of your datasets
- **System Status**: Shows the status of system components

To customize the dashboard:

1. Click the "Customize" button in the top-right corner
2. Drag and drop widgets to rearrange them
3. Click the gear icon on any widget to configure it
4. Click "Save Layout" when finished

## Data Management

### Importing Data

Quantis supports several methods for importing time series data:

#### File Upload

1. Navigate to the Data section
2. Click "Import Data"
3. Select "File Upload"
4. Choose a CSV, Excel, or JSON file from your computer
5. Map the columns to the required fields (timestamp, value, and optional dimensions)
6. Click "Import"

#### Database Connection

1. Navigate to the Data section
2. Click "Import Data"
3. Select "Database Connection"
4. Configure the connection parameters for your database
5. Write or select a SQL query to extract the data
6. Map the columns to the required fields
7. Click "Import"

#### API Integration

1. Navigate to the Data section
2. Click "Import Data"
3. Select "API Integration"
4. Configure the API connection details
5. Set up the data mapping
6. Configure the refresh schedule (if applicable)
7. Click "Import"

### Data Preprocessing

Quantis provides tools for preprocessing your time series data:

#### Handling Missing Values

1. Select your dataset
2. Click "Preprocess"
3. In the "Missing Values" section, choose a strategy:
   - Linear interpolation
   - Forward fill
   - Backward fill
   - Custom value
4. Click "Apply"

#### Outlier Detection

1. Select your dataset
2. Click "Preprocess"
3. In the "Outliers" section, choose a detection method:
   - Z-score
   - IQR (Interquartile Range)
   - Isolation Forest
4. Set the threshold parameters
5. Choose how to handle detected outliers:
   - Flag only
   - Remove
   - Replace with interpolated values
6. Click "Apply"

#### Resampling

1. Select your dataset
2. Click "Preprocess"
3. In the "Resampling" section, choose:
   - The target frequency (hourly, daily, weekly, etc.)
   - The aggregation method for values (mean, sum, etc.)
4. Click "Apply"

### Feature Engineering

Quantis can automatically generate features from your time series data:

1. Select your dataset
2. Click "Feature Engineering"
3. Select the features to generate:
   - Lag features
   - Rolling statistics
   - Seasonal components
   - Holiday indicators
   - Custom features (Python code)
4. Configure the parameters for each feature type
5. Click "Generate Features"

## Creating Forecasts

### Quick Forecast

For a simple forecast with default settings:

1. Navigate to the Predictions section
2. Click "New Forecast"
3. Select your dataset
4. Choose the target variable to forecast
5. Set the forecast horizon (how far into the future to predict)
6. Click "Generate Forecast"

### Advanced Forecast

For more control over the forecasting process:

1. Navigate to the Predictions section
2. Click "New Forecast"
3. Select "Advanced Options"
4. Configure the following settings:
   - Dataset and target variable
   - Forecast horizon
   - Model selection (or let Quantis choose automatically)
   - Feature selection
   - Training window
   - Validation strategy
   - Confidence interval width
5. Click "Generate Forecast"

### Scheduled Forecasts

To set up recurring forecasts:

1. Create a forecast using either the quick or advanced method
2. Click "Schedule" on the forecast results page
3. Configure the schedule:
   - Frequency (daily, weekly, monthly)
   - Time of day
   - Start and end dates (optional)
4. Set up notifications (optional)
5. Click "Save Schedule"

## Analyzing Results

### Forecast Visualization

After generating a forecast, you can visualize the results:

1. Select the forecast from the Predictions section
2. The main chart shows:
   - Historical data
   - Predicted values
   - Confidence intervals
   - Actual values (if available)

### Chart Controls

Use the chart controls to customize the visualization:

- Zoom: Use the slider below the chart or mouse wheel
- Pan: Click and drag the chart
- Time Range: Select a predefined range or set custom dates
- Export: Download the chart as PNG, SVG, or CSV

### Performance Metrics

Quantis provides several metrics to evaluate forecast accuracy:

- **MAPE** (Mean Absolute Percentage Error)
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Square Error)
- **R²** (Coefficient of Determination)

To view detailed metrics:

1. Select the forecast
2. Click the "Metrics" tab
3. Choose which metrics to display
4. Compare against baseline models or previous versions

### Feature Importance

To understand which factors influence your forecast:

1. Select the forecast
2. Click the "Feature Importance" tab
3. Review the chart showing the relative importance of each feature
4. Click on a feature to see its relationship with the target variable

### Scenario Analysis

To explore different scenarios:

1. Select the forecast
2. Click "Scenario Analysis"
3. Create a new scenario by adjusting input variables
4. Compare the scenario forecast with the baseline
5. Save scenarios for future reference

## Model Management

### Available Models

Quantis includes several forecasting models:

- **Temporal Fusion Transformer (TFT)**: Advanced deep learning model for multivariate time series
- **Prophet**: Facebook's model for business time series with seasonal patterns
- **ARIMA/SARIMA**: Traditional statistical models for time series
- **XGBoost/LightGBM**: Gradient boosting models with time-based features
- **Custom Models**: Python-based custom models

### Training a Model

To train a specific model:

1. Navigate to the Models section
2. Click "Train New Model"
3. Select the model type
4. Choose the dataset and target variable
5. Configure model-specific parameters
6. Set training and validation options
7. Click "Train Model"

### Model Versioning

Quantis tracks all model versions:

1. Navigate to the Models section
2. Select a model
3. Click the "Versions" tab
4. View all versions with performance metrics
5. Compare versions side by side
6. Promote a version to production

### Model Deployment

To deploy a model for production use:

1. Navigate to the Models section
2. Select the model
3. Click "Deploy"
4. Choose the deployment target:
   - API endpoint
   - Batch processing
   - Streaming
5. Configure deployment settings
6. Click "Deploy Model"

## Account Settings

### User Profile

To update your profile:

1. Click your username in the top-right corner
2. Select "Profile"
3. Update your information:
   - Name
   - Email
   - Password
   - Profile picture
4. Click "Save Changes"

### Notification Settings

To configure notifications:

1. Click your username in the top-right corner
2. Select "Notifications"
3. Choose which events trigger notifications:
   - Forecast completion
   - Model training completion
   - System alerts
   - Scheduled reports
4. Set notification methods (email, in-app, webhook)
5. Click "Save Settings"

### API Keys

To manage API keys for programmatic access:

1. Click your username in the top-right corner
2. Select "API Keys"
3. View existing keys or create a new one
4. Set permissions and expiration for each key
5. Copy the key value (only shown once)
6. Click "Save"

## Troubleshooting

### Common Issues

#### Forecast Taking Too Long

If forecasts are taking too long to generate:

1. Reduce the dataset size or time range
2. Simplify the model (fewer features or parameters)
3. Check system resource usage
4. Contact your administrator if the issue persists

#### Poor Forecast Accuracy

If forecast accuracy is lower than expected:

1. Check data quality (missing values, outliers)
2. Ensure sufficient historical data is available
3. Try different models or feature combinations
4. Consider adding external variables that might influence the target

#### Data Import Failures

If data import is failing:

1. Verify the data format matches the expected format
2. Check for special characters or encoding issues
3. Ensure date/time formats are consistent
4. Try importing a smaller sample first

### Error Messages

Common error messages and their solutions:

- **"Insufficient data for training"**: Provide more historical data
- **"Invalid date format"**: Ensure dates are in ISO format (YYYY-MM-DD)
- **"Model convergence failed"**: Try a different model or adjust parameters
- **"API rate limit exceeded"**: Reduce the frequency of API calls

### Support Resources

If you need additional help:

- **In-app Help**: Click the "?" icon in the top-right corner
- **Documentation**: Access the full documentation from the Help menu
- **Support Ticket**: Submit a ticket from the Help menu
- **Community Forum**: Discuss issues with other users at forum.quantis.example.com

## FAQ

### General Questions

**Q: How much historical data is needed for accurate forecasts?**

A: As a general rule, you should have at least 3 times as much historical data as the forecast horizon. For example, if you want to forecast 30 days ahead, aim for at least 90 days of history. More complex patterns may require more data.

**Q: Can Quantis handle multiple seasonality patterns?**

A: Yes, models like Temporal Fusion Transformer and Prophet can automatically detect and account for multiple seasonal patterns (daily, weekly, monthly, yearly).

**Q: How often should I retrain my models?**

A: It depends on how quickly your data patterns change. As a best practice, consider retraining:

- When new significant data becomes available
- When forecast accuracy starts to decline
- On a regular schedule (monthly or quarterly)
- After major events that might change the underlying patterns

**Q: Can I export forecasts to other systems?**

A: Yes, forecasts can be exported in several formats:

- CSV or Excel for spreadsheet applications
- JSON for programmatic use
- Direct API integration with other systems
- Scheduled reports via email

**Q: How does Quantis handle confidential data?**

A: Quantis implements several security measures:

- Data encryption in transit and at rest
- Role-based access control
- Audit logging of all actions
- Option for on-premises deployment for sensitive data

### Technical Questions

**Q: What browsers are supported?**

A: Quantis supports:

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

**Q: Can I use Quantis offline?**

A: The web interface requires an internet connection, but you can:

- Export forecasts for offline use
- Use the Python client library in offline environments
- Set up a local deployment for internal networks

**Q: Is there an API rate limit?**

A: Yes, API rate limits depend on your subscription level. Check the API documentation or your account settings for specific limits.

**Q: Can I integrate custom Python code?**

A: Yes, Quantis supports custom Python code in several areas:

- Custom feature engineering
- Custom models
- Custom preprocessing steps
- Post-processing of forecast results
