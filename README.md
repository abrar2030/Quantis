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

## Executive Summary

Quantis is a comprehensive quantitative trading and investment analytics platform that combines **advanced statistical models, machine learning algorithms, and real-time market data** to provide powerful insights and automated trading strategies. It offers a robust framework for data processing, quantitative analysis, strategy development, and portfolio management, all built on a scalable **microservices architecture**.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Quantis provides a robust platform for quantitative analysis, algorithmic trading, and investment portfolio optimization. The system leverages advanced statistical models and machine learning algorithms to analyze market data, identify trading opportunities, and execute automated trading strategies. The microservices architecture ensures that each component—from data ingestion to strategy execution—is independent, resilient, and can be scaled horizontally to handle high-volume, low-latency market operations.

---

## Key Features

Quantis's functionality is divided into four main domains, each powered by dedicated services.

### 1. Data Processing & Analysis

The foundation of the platform lies in its ability to handle diverse financial data. This includes **Real-time Market Data** through seamless integration with multiple data sources, **Historical Data Analysis** using dedicated tools for efficient backtesting, and **Alternative Data Processing** to analyze non-traditional sources for unique insights. Furthermore, **Data Quality Assurance** is maintained through automated validation and cleaning processes to ensure the integrity of all financial data.

### 2. Quantitative Analysis

Advanced mathematical and computational tools are used for signal generation and risk assessment. Quantis implements various **Statistical Models**, including time series analysis and factor analysis, alongside **Machine Learning Algorithms** (classification, regression, and clustering) for market prediction. For risk, it provides robust **Risk Models** such as **Value at Risk (VaR)** and comprehensive stress testing. Finally, **Portfolio Optimization** is achieved through the implementation of Modern Portfolio Theory (MPT) with support for custom constraints and optimization objectives.

### 3. Trading Strategies

Quantis provides a flexible framework for developing, testing, and deploying automated strategies. This includes a **Strategy Development Framework** for rapid creation and rigorous testing of trading algorithms, leading to **Algorithmic Trading** with automated, low-latency execution across connected brokers. The platform also handles **Signal Generation** through the automated creation of technical and fundamental indicators, all supported by a powerful **Backtesting Engine** for historical performance evaluation and optimization.

### 4. Portfolio Management

Tools are provided for monitoring, optimizing, and controlling investment portfolios. Key features include **Asset Allocation** to determine the optimal distribution of investments, and **Risk Management** with comprehensive tools for real-time monitoring of portfolio risk exposures. Users benefit from **Performance Analytics** with detailed metrics and visualizations, and **Rebalancing Strategies** that automate portfolio adjustments based on predefined rules and optimization results.

---

## Architecture

Quantis follows a microservices architecture, logically grouped into three main service layers, supported by a common infrastructure.

### Architectural Components

| Layer                   | Key Services                                                                  | Description                                                                           |
| :---------------------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| **Data Services**       | Market Data, Alternative Data, Historical Data, Data Quality                  | Responsible for all data ingestion, storage, cleaning, and retrieval.                 |
| **Analytical Services** | Statistical Analysis, Machine Learning, Risk Analysis, Portfolio Optimization | Contains the core quantitative intelligence, running models and generating insights.  |
| **Trading Services**    | Strategy, Signal Generation, Backtesting, Execution                           | Manages the full lifecycle of trading strategies, from development to live execution. |
| **Infrastructure**      | API Gateway, Authentication Service, Monitoring Stack, Data Storage           | Provides common technical capabilities and ensures system stability and security.     |

---

## Technology Stack

The platform is built using a modern, performant, and well-supported technology stack.

| Category               | Key Technologies                                                   | Description                                                                                                                        |
| :--------------------- | :----------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**            | Python, Rust, FastAPI, Flask                                       | Python for data science and rapid development; Rust for performance-critical components. FastAPI/Flask for robust API development. |
| **Databases**          | PostgreSQL, InfluxDB                                               | PostgreSQL for relational data and core system state; InfluxDB for high-volume time series data storage.                           |
| **Task Queue**         | Celery, Redis                                                      | Celery for asynchronous task processing; Redis for task queuing and caching.                                                       |
| **ML/Quant Libraries** | scikit-learn, PyTorch, pandas-ta, pyfolio, zipline                 | Specialized libraries for machine learning, technical analysis, performance reporting, and event-driven backtesting.               |
| **Frontend**           | React, TypeScript, Redux Toolkit, D3.js, Plotly, TradingView       | Modern stack for a responsive, data-rich web dashboard with advanced visualization capabilities.                                   |
| **DevOps**             | Docker, Kubernetes, GitHub Actions, Prometheus, Grafana, ELK Stack | Full-stack CI/CD, container orchestration, and observability tools for production readiness.                                       |

---

## Getting Started

### Prerequisites

To set up the platform, ensure you have the following installed:

- **Python** (v3.9+)
- **Node.js** (v16+)
- **Docker** and Docker Compose
- **Kubernetes** (for production deployment)

### Local Development Setup

The recommended way to set up the development environment is using the provided scripts:

| Step                    | Command                                                            | Description                                                     |
| :---------------------- | :----------------------------------------------------------------- | :-------------------------------------------------------------- |
| **1. Clone Repository** | `git clone https://github.com/abrar2030/Quantis.git && cd Quantis` | Download the source code and navigate to the project directory. |
| **2. Run Setup Script** | `./setup_quantis_env.sh`                                           | Installs dependencies and configures the local environment.     |
| **3. Start Services**   | `./run_quantis.sh dev`                                             | Starts all core services for development.                       |

**Access Points:**

- **Web Dashboard**: `http://localhost:3000`
- **API Documentation**: `http://localhost:8000/docs`
- **Monitoring Dashboard**: `http://localhost:9090`

### Deployment

Quantis supports both Docker Compose for local environments and Kubernetes for production deployment.

| Deployment Target  | Command Example                        |
| :----------------- | :------------------------------------- |
| **Docker Compose** | `docker-compose up -d`                 |
| **Kubernetes**     | `kubectl apply -f infrastructure/k8s/` |

---

## API Documentation

Quantis exposes a comprehensive, versioned API for all platform interactions, accessible via the API Gateway.

### Key API Endpoints

| Service         | Endpoint                              | Method | Description                                 |
| :-------------- | :------------------------------------ | :----- | :------------------------------------------ |
| **Market Data** | `/api/v1/market/prices`               | `GET`  | Get real-time market prices.                |
| **Strategy**    | `/api/v1/strategies`                  | `POST` | Create a new trading strategy.              |
| **Strategy**    | `/api/v1/strategies/{id}/backtest`    | `POST` | Run a strategy backtest and return results. |
| **Portfolio**   | `/api/v1/portfolios/{id}/performance` | `GET`  | Get detailed portfolio performance metrics. |
| **Portfolio**   | `/api/v1/portfolios/{id}/rebalance`   | `POST` | Trigger an automated portfolio rebalancing. |

Full API documentation, including request/response schemas, is available at `http://localhost:8000/docs`.

---

## Testing

The project maintains an overall test coverage of **82%** across all components, ensuring reliability and accuracy in financial calculations and trading logic.

### Test Coverage Summary

| Component                | Coverage | Status |
| :----------------------- | :------- | :----- |
| **Trading Services**     | 87%      | ✅     |
| **Data Services**        | 85%      | ✅     |
| **Analytical Services**  | 83%      | ✅     |
| **Portfolio Management** | 80%      | ✅     |
| **API Layer**            | 90%      | ✅     |
| **Frontend Components**  | 75%      | ✅     |

### Testing Types

Testing is categorized into four main types:

1.  **Unit Tests**: Focused on individual functions, statistical models, and core trading logic.
2.  **Integration Tests**: Validating end-to-end trading workflows, API endpoints, and database interactions.
3.  **Performance Tests**: Measuring data processing throughput, backtesting speed, and API response times under load.
4.  **Security Tests**: Ensuring the platform adheres to security standards and best practices.

**Running Tests:** All tests can be executed using the `pytest` command from the root directory: `pytest`. Specific categories can be targeted (e.g., `pytest tests/unit/`).

---

## CI/CD Pipeline

Quantis uses **GitHub Actions** for continuous integration and deployment, automating the development workflow:

- **Continuous Integration**: Automated testing, code quality checks (pylint, flake8, ESLint), and security scanning on every pull request.
- **Continuous Deployment**: Automated Docker image building/publishing and deployment to staging and production environments (managed via Kubernetes).

---

## Contributing

We welcome contributions to Quantis! To get involved:

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/your-feature-name`).
3.  Commit your changes and push to the branch.
4.  Open a Pull Request for review.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
