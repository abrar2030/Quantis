# Quantis

![CI/CD Status](https://img.shields.io/github/actions/workflow/status/abrar2030/Quantis/cicd.yml?branch=main&label=CI/CD&logo=github)
[![Test Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen)](https://github.com/abrar2030/Quantis/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📈 Quantitative Trading & Investment Analytics Platform

Quantis is a comprehensive quantitative trading and investment analytics platform that combines advanced statistical models, machine learning algorithms, and real-time market data to provide powerful insights and automated trading strategies.

<div align="center">
  <img src="docs/images/Quantis_dashboard.bmp" alt="Quantis Dashboard" width="80%">
</div>

> **Note**: This project is under active development. Features and functionalities are continuously being enhanced to improve trading capabilities and user experience.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
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
* **Real-time Market Data**: Integration with multiple data sources for comprehensive market coverage
* **Historical Data Analysis**: Tools for backtesting and historical performance evaluation
* **Alternative Data Processing**: Analysis of non-traditional data sources for unique insights
* **Data Quality Assurance**: Automated validation and cleaning of financial data

### Quantitative Analysis
* **Statistical Models**: Time series analysis, regression models, and factor analysis
* **Machine Learning Algorithms**: Classification, regression, and clustering for market prediction
* **Risk Models**: Value at Risk (VaR), Expected Shortfall, and stress testing
* **Portfolio Optimization**: Modern Portfolio Theory implementation with custom constraints

### Trading Strategies
* **Strategy Development Framework**: Tools for creating and testing trading algorithms
* **Algorithmic Trading**: Automated execution of trading strategies
* **Signal Generation**: Technical and fundamental indicators for trade signals
* **Backtesting Engine**: Historical performance evaluation of trading strategies

### Portfolio Management
* **Asset Allocation**: Optimal distribution of investments across asset classes
* **Risk Management**: Tools for monitoring and controlling portfolio risk
* **Performance Analytics**: Comprehensive metrics for evaluating investment performance
* **Rebalancing Strategies**: Automated portfolio rebalancing based on defined rules

## Technology Stack

### Backend
* **Language**: Python, Rust (for performance-critical components)
* **Framework**: FastAPI, Flask
* **Database**: PostgreSQL, InfluxDB (time series data)
* **Task Queue**: Celery, Redis
* **ML Libraries**: scikit-learn, PyTorch, TensorFlow
* **Financial Libraries**: pandas-ta, pyfolio, zipline

### Frontend
* **Framework**: React with TypeScript
* **State Management**: Redux Toolkit
* **Data Visualization**: D3.js, Plotly, TradingView
* **Styling**: Tailwind CSS, Styled Components
* **API Client**: Axios, React Query

### Infrastructure
* **Containerization**: Docker
* **Orchestration**: Kubernetes
* **CI/CD**: GitHub Actions
* **Monitoring**: Prometheus, Grafana
* **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

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
## Getting Started

### Prerequisites
* Python 3.9+
* Node.js 16+
* Docker and Docker Compose
* Kubernetes (for production deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/abrar2030/Quantis.git
   cd Quantis
   ```

2. **Run the setup script**
   ```bash
   ./setup_quantis_env.sh
   ```

3. **Start the development environment**
   ```bash
   ./run_quantis.sh dev
   ```

4. **Access the application**
   * Web Dashboard: [http://localhost:3000](http://localhost:3000)
   * API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   * Monitoring Dashboard: [http://localhost:9090](http://localhost:9090)

### Docker Compose Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Check deployment status
kubectl get pods -n quantis

# Port forward to access the dashboard
kubectl port-forward svc/quantis-web 3000:3000 -n quantis
```

## API Documentation

Quantis provides a comprehensive API for interacting with the platform:

### Market Data API
* `GET /api/v1/market/prices` - Get real-time market prices
* `GET /api/v1/market/historical` - Get historical market data
* `GET /api/v1/market/indicators` - Get technical indicators

### Strategy API
* `POST /api/v1/strategies` - Create a new trading strategy
* `GET /api/v1/strategies` - List all strategies
* `GET /api/v1/strategies/{id}` - Get strategy details
* `POST /api/v1/strategies/{id}/backtest` - Run strategy backtest

### Portfolio API
* `GET /api/v1/portfolios` - List all portfolios
* `POST /api/v1/portfolios` - Create a new portfolio
* `GET /api/v1/portfolios/{id}/performance` - Get portfolio performance
* `POST /api/v1/portfolios/{id}/rebalance` - Rebalance portfolio

## Testing

The project maintains comprehensive test coverage across all components to ensure reliability and accuracy.

### Test Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| Data Services | 85% | ✅ |
| Analytical Services | 83% | ✅ |
| Trading Services | 87% | ✅ |
| Portfolio Management | 80% | ✅ |
| API Layer | 90% | ✅ |
| Frontend Components | 75% | ✅ |
| Overall | 82% | ✅ |

### Unit Tests
* Data processing pipeline tests
* Statistical model tests
* Trading strategy tests
* Portfolio optimization tests

### Integration Tests
* End-to-end trading workflow tests
* API endpoint tests
* Database integration tests
* Third-party service integration tests

### Performance Tests
* Data processing throughput tests
* Strategy backtesting performance tests
* API response time tests
* Concurrent user load tests

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage report
pytest --cov=quantis
```

## CI/CD Pipeline

Quantis uses GitHub Actions for continuous integration and deployment:

* Automated testing on each pull request
* Code quality checks with pylint, flake8, and ESLint
* Security scanning with Bandit and npm audit
* Docker image building and publishing
* Automated deployment to staging and production environments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.