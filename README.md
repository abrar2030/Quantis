# Quantis

[![CI/CD Status](https://img.shields.io/github/actions/workflow/status/abrar2030/Quantis/ci-cd.yml?branch=main&label=CI/CD&logo=github)](https://github.com/abrar2030/Quantis/actions)
[![Test Coverage](https://img.shields.io/codecov/c/github/abrar2030/Quantis/main?label=Coverage)](https://codecov.io/gh/abrar2030/Quantis)
[![Code Quality](https://img.shields.io/lgtm/grade/python/g/abrar2030/Quantis?label=Code%20Quality)](https://lgtm.com/projects/g/abrar2030/Quantis/)
[![License](https://img.shields.io/github/license/abrar2030/Quantis)](https://github.com/abrar2030/Quantis/blob/main/LICENSE)

## 📈 Quantitative Trading & Investment Analytics Platform

Quantis is a comprehensive quantitative trading and investment analytics platform that combines advanced statistical models, machine learning algorithms, and real-time market data to provide powerful insights and automated trading strategies.

<div align="center">
  <img src="docs/images/quantis_dashboard.png" alt="Quantis Dashboard" width="80%">
</div>

> **Note**: This project is under active development. Features and functionalities are continuously being enhanced to improve trading capabilities and user experience.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Feature Implementation Status](#feature-implementation-status)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [License](#license)

## Overview

Quantis provides a robust platform for quantitative analysis, algorithmic trading, and investment portfolio optimization. The system leverages advanced statistical models and machine learning algorithms to analyze market data, identify trading opportunities, and execute automated trading strategies.

## Key Features

### Data Processing & Analysis
- **Real-time Market Data**: Integration with multiple data sources for comprehensive market coverage
- **Historical Data Analysis**: Tools for backtesting and historical performance evaluation
- **Alternative Data Processing**: Analysis of non-traditional data sources for unique insights
- **Data Quality Assurance**: Automated validation and cleaning of financial data

### Quantitative Modeling
- **Statistical Models**: Time series analysis, regression models, and factor analysis
- **Machine Learning Algorithms**: Classification, regression, and clustering for market prediction
- **Risk Models**: Value at Risk (VaR), Expected Shortfall, and stress testing
- **Portfolio Optimization**: Modern Portfolio Theory implementation with custom constraints

### Trading Strategies
- **Strategy Development Framework**: Tools for creating and testing trading algorithms
- **Algorithmic Trading**: Automated execution of trading strategies
- **Signal Generation**: Technical and fundamental indicators for trade signals
- **Backtesting Engine**: Historical performance evaluation of trading strategies

### Portfolio Management
- **Asset Allocation**: Optimal distribution of investments across asset classes
- **Risk Management**: Tools for monitoring and controlling portfolio risk
- **Performance Analytics**: Comprehensive metrics for evaluating investment performance
- **Rebalancing Strategies**: Automated portfolio rebalancing based on defined rules

## Technology Stack

### Backend
- **Language**: Python, Rust (for performance-critical components)
- **Framework**: FastAPI, Flask
- **Database**: PostgreSQL, InfluxDB (time series data)
- **Task Queue**: Celery, Redis
- **ML Libraries**: scikit-learn, PyTorch, TensorFlow
- **Financial Libraries**: pandas-ta, pyfolio, zipline

### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **Data Visualization**: D3.js, Plotly, TradingView
- **Styling**: Tailwind CSS, Styled Components
- **API Client**: Axios, React Query

### DevOps
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## Architecture

Quantis follows a microservices architecture with the following components:

```
Quantis/
├── Data Services
│   ├── Market Data Service
│   ├── Alternative Data Service
│   ├── Historical Data Service
│   └── Data Quality Service
├── Analytical Services
│   ├── Statistical Analysis Service
│   ├── Machine Learning Service
│   ├── Risk Analysis Service
│   └── Portfolio Optimization Service
├── Trading Services
│   ├── Strategy Service
│   ├── Signal Generation Service
│   ├── Backtesting Service
│   └── Execution Service
├── Frontend Applications
│   ├── Web Dashboard
│   └── Mobile App
└── Infrastructure
    ├── API Gateway
    ├── Authentication Service
    ├── Monitoring Stack
    └── Data Storage
```

## Feature Implementation Status

| Feature | Status | Description | Planned Release |
|---------|--------|-------------|----------------|
| **Data Processing** |
| Market Data Integration | ✅ Implemented | Real-time and historical market data | v1.0 |
| Data Cleaning | ✅ Implemented | Automated data validation | v1.0 |
| Feature Engineering | ✅ Implemented | Technical indicator calculation | v1.0 |
| Alternative Data | 🔄 In Progress | News, social media, satellite imagery | v1.1 |
| Data Versioning | 📅 Planned | Track data lineage and changes | v1.2 |
| **Quantitative Analysis** |
| Statistical Models | ✅ Implemented | Time series, regression analysis | v1.0 |
| Factor Analysis | ✅ Implemented | Multi-factor models | v1.0 |
| Machine Learning | ✅ Implemented | Predictive models for markets | v1.0 |
| Deep Learning | 🔄 In Progress | Neural networks for complex patterns | v1.1 |
| Reinforcement Learning | 📅 Planned | Adaptive trading strategies | v1.2 |
| **Trading Strategies** |
| Strategy Framework | ✅ Implemented | Tools for strategy development | v1.0 |
| Backtesting Engine | ✅ Implemented | Historical performance testing | v1.0 |
| Signal Generation | ✅ Implemented | Technical and fundamental signals | v1.0 |
| Strategy Optimization | 🔄 In Progress | Parameter tuning and optimization | v1.1 |
| Multi-asset Strategies | 📅 Planned | Cross-asset class strategies | v1.2 |
| **Portfolio Management** |
| Asset Allocation | ✅ Implemented | Portfolio construction tools | v1.0 |
| Risk Management | ✅ Implemented | Risk metrics and monitoring | v1.0 |
| Performance Analytics | ✅ Implemented | Return and risk attribution | v1.0 |
| Rebalancing | 🔄 In Progress | Automated portfolio rebalancing | v1.1 |
| Tax-efficient Strategies | 📅 Planned | Tax-loss harvesting and optimization | v1.2 |
| **Feature Engineering** |
| Technical Indicators | ✅ Implemented | Standard technical analysis | v1.0 |
| Feature Importance Analysis | ✅ Implemented | Quantify variable impact | v1.0 |
| Temporal Feature Extraction | ✅ Implemented | Time-based feature creation | v1.0 |
| External Data Integration | 🔄 In Progress | Incorporate external factors | v1.1 |
| Feature Store | 📅 Planned | Centralized feature management | v1.2 |
| **Model Management** |
| Version Tracking | ✅ Implemented | Model versioning system | v1.0 |
| A/B Testing | ✅ Implemented | Compare model performance | v1.0 |
| Automated Retraining | 🔄 In Progress | Scheduled model updates | v1.1 |
| Model Registry | 🔄 In Progress | Centralized model storage | v1.1 |
| Model Explainability | 📅 Planned | Interpretable predictions | v1.2 |
| **API & Integration** |
| REST API | ✅ Implemented | HTTP-based API access | v1.0 |
| Authentication | ✅ Implemented | Secure API access | v1.0 |
| Rate Limiting | ✅ Implemented | API usage controls | v1.0 |
| Streaming Data Support | 🔄 In Progress | Real-time data processing | v1.1 |
| SDK Development | 📅 Planned | Client libraries for integration | v1.2 |
| **Monitoring & Observability** |
| Performance Dashboards | ✅ Implemented | Grafana visualization | v1.0 |
| Alerting System | ✅ Implemented | Notification for issues | v1.0 |
| Model Drift Detection | 🔄 In Progress | Identify prediction degradation | v1.1 |
| Automated Remediation | 📅 Planned | Self-healing capabilities | v1.2 |

**Legend:**
- ✅ Implemented: Feature is complete and available
- 🔄 In Progress: Feature is currently being developed
- 📅 Planned: Feature is planned for future release

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- Docker and Docker Compose (for containerized deployment)

### Quick Start with Setup Script
```bash
# Clone the repository
git clone https://github.com/abrar2030/Quantis.git
cd Quantis

# Run the setup script
./setup_quantis_env.sh

# Start the application
./run_quantis.sh
```

### Manual Installation

#### Clone the Repository
```bash
git clone https://github.com/abrar2030/Quantis.git
cd Quantis
```

#### Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
cd api
uvicorn app:app --reload
```

#### Frontend Setup
```bash
cd web-frontend
npm install
npm start
```

#### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Documentation

API documentation is available at `/docs` when the backend is running. The API provides endpoints for:

- Market data retrieval
- Strategy backtesting
- Portfolio optimization
- Risk analysis
- Model training and inference
- Trading signal generation

Example API request:
```python
import requests

# Get historical market data
response = requests.get(
    "http://localhost:8000/api/v1/market-data/historical",
    params={
        "symbol": "AAPL",
        "start_date": "2022-01-01",
        "end_date": "2022-12-31",
        "interval": "1d"
    },
    headers={"Authorization": f"Bearer {api_key}"}
)

data = response.json()
```

## Testing

The project includes comprehensive testing to ensure reliability and accuracy:

### Unit Testing
- Model component tests
- API endpoint tests
- Data processing pipeline tests
- Strategy implementation tests

### Integration Testing
- End-to-end workflow tests
- Frontend-backend integration tests
- Data pipeline integration tests
- Trading strategy execution tests

### Performance Testing
- Model inference latency tests
- API throughput tests
- Backtesting performance tests
- Scalability tests

To run tests:
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_models.py
pytest tests/test_api.py

# Run with coverage
pytest --cov=quantis tests/

# Generate coverage report
pytest --cov=quantis --cov-report=html tests/
```

## CI/CD Pipeline

Quantis uses GitHub Actions for continuous integration and deployment:

### Continuous Integration
- Automated testing on each pull request and push to main
- Code quality checks with pylint and black
- Test coverage reporting with pytest-cov
- Security scanning for vulnerabilities
- Performance benchmarking

### Continuous Deployment
- Automated deployment to staging environment on merge to main
- Manual promotion to production after approval
- Docker image building and publishing
- Kubernetes deployment updates
- Database migration management

Current CI/CD Status:
- Build: ![Build Status](https://img.shields.io/github/actions/workflow/status/abrar2030/Quantis/ci-cd.yml?branch=main&label=build)
- Test Coverage: ![Coverage](https://img.shields.io/codecov/c/github/abrar2030/Quantis/main?label=coverage)
- Code Quality: ![Code Quality](https://img.shields.io/lgtm/grade/python/g/abrar2030/Quantis?label=code%20quality)

## Contributing

We welcome contributions to improve Quantis! Here's how you can contribute:

1. **Fork the repository**
   - Create your own copy of the project to work on

2. **Create a feature branch**
   - `git checkout -b feature/amazing-feature`
   - Use descriptive branch names that reflect the changes

3. **Make your changes**
   - Follow the coding standards and guidelines
   - Write clean, maintainable, and tested code
   - Update documentation as needed

4. **Commit your changes**
   - `git commit -m 'Add some amazing feature'`
   - Use clear and descriptive commit messages
   - Reference issue numbers when applicable

5. **Push to branch**
   - `git push origin feature/amazing-feature`

6. **Open Pull Request**
   - Provide a clear description of the changes
   - Link to any relevant issues
   - Respond to review comments and make necessary adjustments

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write unit tests for new features
- Update documentation for any changes
- Ensure all tests pass before submitting a pull request
- Keep pull requests focused on a single feature or fix

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
