# Quantis Project

Quantis is an advanced time series forecasting platform that provides machine learning-based predictions and analytics.

<div align="center">
  <img src="docs/Quantis.bmp" alt="An Advanced Time Series Forecasting Platform" width="100%">
</div>

> **Note**: This Project is currently under active development. Features and functionalities are being added and improved continuously to enhance user experience.

## Project Structure

```
quantis/
├── api/                  # Backend API
│   ├── endpoints/        # API endpoint implementations
│   ├── middleware/       # API middleware (auth, etc.)
│   ├── app.py            # FastAPI application
│   └── schemas.py        # Pydantic schemas
├── data/                 # Data processing
│   ├── features/         # Feature engineering
│   ├── processed/        # Processed data storage
│   ├── raw/              # Raw data storage
│   └── process_data.py   # Data processing pipeline
├── frontend/             # React frontend application
│   ├── public/           # Static public assets
│   └── src/              # React source code
│       ├── components/   # Reusable UI components
│       ├── context/      # React context providers
│       ├── hooks/        # Custom React hooks
│       ├── pages/        # Application pages
│       ├── services/     # API service integrations
│       ├── styles/       # CSS and styling
│       ├── utils/        # Utility functions
│       ├── App.js        # Main application component
│       └── index.js      # Application entry point
├── infrastructure/       # Deployment configuration
│   ├── kubernetes/       # Kubernetes manifests
│   ├── terraform/        # Infrastructure as code
│   └── docker-compose.yml # Docker Compose configuration
├── models/               # ML models
│   ├── hyperparameter_tuning/ # Hyperparameter optimization
│   ├── model_serving/    # Model serving code
│   ├── train_model.py    # Model training script
│   └── tft_model.pkl     # Serialized model
├── monitoring/           # Monitoring and observability
│   ├── grafana_dashboards/ # Grafana dashboard configs
│   ├── model_monitor.py  # Model monitoring code
│   └── prometheus.yml    # Prometheus configuration
└── tests/                # Test suite
    └── test_model.py     # Model tests
```

## Features

- Time series forecasting with advanced ML models
- Interactive dashboard with performance metrics
- Feature importance analysis
- Model version tracking
- API for integration with other systems
- Monitoring and observability

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker and Docker Compose (for containerized deployment)

### Installation

1. Clone the repository
2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

### Running the Application

#### Backend

```
cd api
uvicorn app:app --reload
```

#### Frontend

```
cd frontend
npm start
```

#### Using Docker Compose

```
docker-compose up -d
```

## API Documentation

API documentation is available at `/docs` when the backend is running.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
