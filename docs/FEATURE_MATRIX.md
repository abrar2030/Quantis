# Feature Matrix

Comprehensive feature table summarizing all capabilities, modules, and functionalities of the Quantis platform.

## Table of Contents

- [Core Features](#core-features)
- [Authentication & Security](#authentication--security)
- [Data Management](#data-management)
- [Machine Learning Models](#machine-learning-models)
- [Prediction Services](#prediction-services)
- [Financial Services](#financial-services)
- [Monitoring & Analytics](#monitoring--analytics)
- [API Features](#api-features)
- [Infrastructure Features](#infrastructure-features)
- [Frontend Features](#frontend-features)

---

## Core Features

| Feature                        | Short description                         | Module / File                     | CLI flag / API        | Example (path)                             | Notes                           |
| ------------------------------ | ----------------------------------------- | --------------------------------- | --------------------- | ------------------------------------------ | ------------------------------- |
| **FastAPI Backend**            | High-performance async API framework      | `code/api/app.py`                 | `uvicorn api.app:app` | [API Docs](examples/basic-api.md)          | Production-ready REST API       |
| **Microservices Architecture** | Independent, scalable services            | `infrastructure/`                 | Docker Compose, K8s   | [Architecture](ARCHITECTURE.md)            | API, ML, Data services          |
| **Real-time WebSocket**        | Bidirectional client-server communication | `code/api/endpoints/websocket.py` | `ws://host/ws/*`      | [WebSocket Example](examples/websocket.md) | Notifications, live updates     |
| **Async Task Queue**           | Background job processing with Celery     | `code/api/tasks.py`               | Celery workers        | -                                          | Model training, data processing |
| **Database Abstraction**       | SQLAlchemy ORM with multiple DB support   | `code/api/database.py`            | `DATABASE_URL`        | -                                          | PostgreSQL, MySQL, SQLite       |
| **Caching Layer**              | Redis-based caching for performance       | `code/api/database.py`            | `REDIS_URL`           | -                                          | Session storage, rate limiting  |

---

## Authentication & Security

| Feature                       | Short description                    | Module / File                 | CLI flag / API               | Example (path)                             | Notes                      |
| ----------------------------- | ------------------------------------ | ----------------------------- | ---------------------------- | ------------------------------------------ | -------------------------- |
| **JWT Authentication**        | Secure token-based auth              | `code/api/endpoints/auth.py`  | `POST /auth/login`           | [Auth Example](examples/authentication.md) | Access & refresh tokens    |
| **Two-Factor Auth (MFA)**     | TOTP-based 2FA                       | `code/api/endpoints/auth.py`  | `POST /auth/mfa/enable`      | -                                          | QR code generation         |
| **Role-Based Access Control** | Granular permission system           | `code/api/models.py`          | User roles                   | -                                          | Admin, User, ReadOnly      |
| **API Key Management**        | Service authentication               | `code/api/endpoints/auth.py`  | `POST /auth/api-keys`        | -                                          | For service-to-service     |
| **Rate Limiting**             | Request throttling per user/endpoint | `code/api/middleware/auth.py` | Automatic                    | -                                          | Configurable limits        |
| **Password Hashing**          | bcrypt password security             | `code/api/endpoints/auth.py`  | Automatic                    | -                                          | Secure password storage    |
| **Session Management**        | Multi-session support with tracking  | `code/api/models.py`          | `/auth/sessions`             | -                                          | Device tracking, logout    |
| **Audit Logging**             | Complete action audit trail          | `code/api/models.py`          | `GET /monitoring/audit-logs` | -                                          | Compliance, security       |
| **CORS Protection**           | Configurable cross-origin            | `code/api/app.py`             | `CORS_ORIGINS`               | -                                          | Production security        |
| **Input Validation**          | Pydantic schema validation           | `code/api/schemas.py`         | Automatic                    | -                                          | Prevents injection attacks |

---

## Data Management

| Feature                 | Short description               | Module / File                    | CLI flag / API                          | Example (path)                               | Notes                        |
| ----------------------- | ------------------------------- | -------------------------------- | --------------------------------------- | -------------------------------------------- | ---------------------------- |
| **Dataset Upload**      | Multi-format data ingestion     | `code/api/endpoints/datasets.py` | `POST /datasets/upload`                 | [Upload Example](examples/dataset-upload.md) | CSV, Parquet, JSON, Excel    |
| **Dataset Management**  | CRUD operations for datasets    | `code/api/endpoints/datasets.py` | `/datasets/*`                           | -                                            | Create, read, update, delete |
| **Data Statistics**     | Automated data profiling        | `code/api/endpoints/datasets.py` | `GET /datasets/{id}/stats`              | -                                            | Rows, columns, types, nulls  |
| **Data Preview**        | Sample data viewing             | `code/api/endpoints/datasets.py` | `GET /datasets/{id}/preview`            | -                                            | Paginated data samples       |
| **Data Download**       | Export processed datasets       | `code/api/endpoints/datasets.py` | `GET /datasets/{id}/download`           | -                                            | Download in original format  |
| **Data Processing**     | ETL and transformation pipeline | `code/data/process_data.py`      | `data_processor.sh`                     | -                                            | Scaling, encoding, features  |
| **Feature Engineering** | Automated feature creation      | `code/data/process_data.py`      | `DataEngine.create_temporal_features()` | -                                            | Rolling windows, lags        |
| **Data Validation**     | Schema and quality checks       | `code/data/process_data.py`      | Automatic                               | -                                            | Missing values, types        |
| **Dask Integration**    | Parallel data processing        | `code/data/process_data.py`      | Automatic                               | -                                            | Large dataset support        |

---

## Machine Learning Models

| Feature                         | Short description                     | Module / File                                   | CLI flag / API               | Example (path)                                 | Notes                       |
| ------------------------------- | ------------------------------------- | ----------------------------------------------- | ---------------------------- | ---------------------------------------------- | --------------------------- |
| **LSTM Models**                 | Long Short-Term Memory networks       | `code/models/train_model.py`                    | `model_type="lstm"`          | [LSTM Example](examples/model-training.md)     | Time series forecasting     |
| **Temporal Fusion Transformer** | Advanced time series model            | `code/models/train_model.py`                    | `model_type="tft"`           | -                                              | Attention-based forecasting |
| **Random Forest**               | Ensemble tree-based learning          | API endpoint                                    | `model_type="random_forest"` | -                                              | Classification, regression  |
| **XGBoost**                     | Gradient boosting framework           | API endpoint                                    | `model_type="xgboost"`       | -                                              | High-performance ML         |
| **Model Training**              | Async training with progress tracking | `code/api/endpoints/models.py`                  | `POST /models/{id}/train`    | [Training Example](examples/model-training.md) | GPU support, checkpointing  |
| **Hyperparameter Tuning**       | Automated optimization                | `code/models/hyperparameter_tuning/optimize.py` | -                            | -                                              | Grid search, Bayesian opt   |
| **Model Versioning**            | Track model iterations                | `code/api/models.py`                            | Automatic                    | -                                              | Version history, rollback   |
| **Model Registry**              | Centralized model catalog             | `code/api/endpoints/models.py`                  | `GET /models`                | -                                              | Search, filter, compare     |
| **Model Comparison**            | Side-by-side performance              | `code/api/endpoints/models.py`                  | `GET /models/compare`        | -                                              | Multi-model evaluation      |
| **Model Metrics**               | Performance evaluation                | `code/api/endpoints/models.py`                  | `GET /models/{id}/metrics`   | -                                              | Accuracy, MAE, MSE, R²      |
| **MLflow Integration**          | Experiment tracking                   | `code/models/mlflow_tracking.py`                | `MLFLOW_TRACKING_URI`        | -                                              | Metrics, params, artifacts  |
| **Model Export**                | Save trained models                   | `code/models/train_model.py`                    | Automatic                    | -                                              | Joblib, PyTorch formats     |
| **AWS Deployment**              | Cloud model serving                   | `code/models/aws_deploy.py`                     | -                            | -                                              | SageMaker integration       |

---

## Prediction Services

| Feature                | Short description             | Module / File                      | CLI flag / API             | Example (path)                                     | Notes                       |
| ---------------------- | ----------------------------- | ---------------------------------- | -------------------------- | -------------------------------------------------- | --------------------------- |
| **Single Prediction**  | Real-time inference           | `code/api/endpoints/prediction.py` | `POST /predict`            | [Prediction Example](examples/basic-prediction.md) | Low-latency predictions     |
| **Batch Prediction**   | Bulk inference processing     | `code/api/endpoints/prediction.py` | `POST /predict/batch`      | -                                                  | Process multiple inputs     |
| **Prediction History** | Track all predictions         | `code/api/endpoints/prediction.py` | `GET /predictions/history` | -                                                  | Audit trail, analysis       |
| **Prediction Stats**   | Aggregated analytics          | `code/api/endpoints/prediction.py` | `GET /predictions/stats`   | -                                                  | Volume, confidence, timing  |
| **Model Health Check** | Validate model status         | `code/api/endpoints/prediction.py` | `GET /models/{id}/health`  | -                                                  | Drift detection, validation |
| **Confidence Scoring** | Prediction reliability metric | `code/api/endpoints/prediction.py` | Automatic                  | -                                                  | Per-prediction confidence   |
| **Execution Timing**   | Performance monitoring        | `code/api/endpoints/prediction.py` | Automatic                  | -                                                  | Latency tracking            |

---

## Financial Services

| Feature                    | Short description          | Module / File                     | CLI flag / API                       | Example (path) | Notes                         |
| -------------------------- | -------------------------- | --------------------------------- | ------------------------------------ | -------------- | ----------------------------- |
| **Transaction Management** | Financial transaction CRUD | `code/api/endpoints/financial.py` | `POST /financial/transactions`       | -              | Deposits, withdrawals, trades |
| **Transaction Approval**   | Workflow approval system   | `code/api/endpoints/financial.py` | `POST /transactions/{id}/approve`    | -              | Multi-level approval          |
| **Financial Summary**      | Portfolio overview         | `code/api/endpoints/financial.py` | `GET /financial/financial-summary`   | -              | Balance, totals, pending      |
| **NPV Calculation**        | Net present value          | `code/api/endpoints/financial.py` | `POST /financial/calculate-npv`      | -              | Investment analysis           |
| **Interest Calculation**   | Compound interest          | `code/api/endpoints/financial.py` | `POST /financial/calculate-interest` | -              | Loan, savings calculations    |
| **Compliance Limits**      | Transaction limits         | `code/api/endpoints/financial.py` | `GET /compliance/limits`             | -              | Regulatory compliance         |
| **Multi-Currency**         | Currency support           | `code/api/endpoints/financial.py` | Currency field                       | -              | USD, EUR, GBP, etc.           |

---

## Monitoring & Analytics

| Feature                  | Short description       | Module / File                         | CLI flag / API               | Example (path) | Notes                           |
| ------------------------ | ----------------------- | ------------------------------------- | ---------------------------- | -------------- | ------------------------------- |
| **System Health Check**  | Overall system status   | `code/api/endpoints/monitoring.py`    | `GET /monitoring/health`     | -              | Service availability            |
| **System Statistics**    | Resource utilization    | `code/api/endpoints/monitoring.py`    | `GET /monitoring/stats`      | -              | CPU, memory, disk               |
| **Prometheus Metrics**   | Time-series metrics     | `code/api/app.py`                     | `GET /metrics`               | -              | Request rates, latencies        |
| **Grafana Dashboards**   | Visual monitoring       | `monitoring/grafana_dashboards/`      | Grafana UI                   | -              | Pre-built dashboards            |
| **Model Monitoring**     | ML performance tracking | `monitoring/model_monitor.py`         | Automatic                    | -              | Drift detection, KL divergence  |
| **Prediction Analytics** | Inference insights      | `code/api/endpoints/monitoring.py`    | `GET /analytics/predictions` | -              | Volume, accuracy trends         |
| **Model Analytics**      | Training metrics        | `code/api/endpoints/monitoring.py`    | `GET /analytics/models`      | -              | Training duration, success rate |
| **Audit Logs**           | Complete action history | `code/api/endpoints/monitoring.py`    | `GET /monitoring/audit-logs` | -              | User actions, API calls         |
| **Custom Metrics**       | User-defined metrics    | `code/api/endpoints/monitoring.py`    | `POST /monitoring/metrics`   | -              | Business KPIs                   |
| **Log Aggregation**      | Structured logging      | `code/api/app.py`                     | structlog                    | -              | JSON logs, easy parsing         |
| **Alert System**         | Notification on events  | `code/api/endpoints/notifications.py` | WebSocket, Email             | -              | System alerts, model events     |

---

## API Features

| Feature                  | Short description             | Module / File          | CLI flag / API             | Example (path)     | Notes                          |
| ------------------------ | ----------------------------- | ---------------------- | -------------------------- | ------------------ | ------------------------------ |
| **OpenAPI/Swagger Docs** | Interactive API documentation | `code/api/app.py`      | `/docs`, `/redoc`          | [API Docs](API.md) | Auto-generated, always current |
| **RESTful Design**       | Standard HTTP methods         | All endpoints          | GET/POST/PUT/DELETE        | -                  | Consistent API patterns        |
| **Pagination**           | Efficient large result sets   | All list endpoints     | `?skip=0&limit=100`        | -                  | Offset-based pagination        |
| **Filtering & Sorting**  | Query parameters              | List endpoints         | `?filter=value&sort=field` | -                  | Flexible data retrieval        |
| **Versioning**           | API version control           | `code/api/app.py`      | `/api/v1/*`                | -                  | Backward compatibility         |
| **Error Handling**       | Consistent error responses    | `code/api/app.py`      | Automatic                  | -                  | Standard error format          |
| **Request Validation**   | Input sanitization            | All endpoints          | Pydantic                   | -                  | Type safety, auto-docs         |
| **Response Models**      | Typed responses               | All endpoints          | Pydantic                   | -                  | Guaranteed structure           |
| **Middleware**           | Request/response processing   | `code/api/middleware/` | Automatic                  | -                  | Auth, CORS, logging            |
| **Compression**          | Gzip response compression     | `code/api/app.py`      | Automatic                  | -                  | Reduced bandwidth              |

---

## Infrastructure Features

| Feature                | Short description            | Module / File                             | CLI flag / API          | Example (path)                                                         | Notes                    |
| ---------------------- | ---------------------------- | ----------------------------------------- | ----------------------- | ---------------------------------------------------------------------- | ------------------------ |
| **Docker Support**     | Containerized deployment     | `infrastructure/docker-compose.yml`       | `docker-compose up`     | [Docker Guide](INSTALLATION.md#method-3-docker-compose)                | Multi-service stack      |
| **Kubernetes Ready**   | Orchestration manifests      | `infrastructure/kubernetes/`              | `kubectl apply`         | [K8s Guide](INSTALLATION.md#method-4-kubernetes-production-deployment) | Production-grade         |
| **Terraform IaC**      | Cloud infrastructure as code | `infrastructure/terraform/`               | `terraform apply`       | -                                                                      | AWS, Azure, GCP          |
| **Ansible Automation** | Configuration management     | `infrastructure/ansible/`                 | `ansible-playbook`      | -                                                                      | Server provisioning      |
| **CI/CD Pipeline**     | GitHub Actions workflow      | `.github/workflows/cicd.yml`              | Automatic               | -                                                                      | Test, build, deploy      |
| **Multi-Environment**  | Dev, staging, prod configs   | `infrastructure/kubernetes/environments/` | Environment-specific    | -                                                                      | Isolated deployments     |
| **Health Checks**      | Container liveness/readiness | K8s manifests                             | Automatic               | -                                                                      | Self-healing deployments |
| **Auto-Scaling**       | Horizontal pod autoscaling   | K8s HPA                                   | Automatic               | -                                                                      | Traffic-based scaling    |
| **Load Balancing**     | Request distribution         | K8s Service                               | Automatic               | -                                                                      | High availability        |
| **Secret Management**  | Secure credential storage    | K8s Secrets                               | `kubectl create secret` | -                                                                      | Encrypted at rest        |

---

## Frontend Features

| Feature               | Short description       | Module / File       | CLI flag / API | Example (path) | Notes                       |
| --------------------- | ----------------------- | ------------------- | -------------- | -------------- | --------------------------- |
| **React SPA**         | Single-page application | `web-frontend/`     | `npm start`    | -              | Modern UI framework         |
| **TypeScript**        | Type-safe JavaScript    | `web-frontend/src/` | Automatic      | -              | Better developer experience |
| **Redux Toolkit**     | State management        | `web-frontend/src/` | Integrated     | -              | Predictable state           |
| **D3.js Charts**      | Data visualization      | `web-frontend/src/` | Components     | -              | Custom chart types          |
| **TradingView**       | Financial charts        | `web-frontend/src/` | Integration    | -              | Professional trading charts |
| **Responsive Design** | Mobile-friendly UI      | All components      | Automatic      | -              | Works on all devices        |
| **Dark Mode**         | Theme switching         | UI settings         | Toggle         | -              | Eye-friendly interface      |
| **Real-time Updates** | WebSocket integration   | WebSocket client    | Automatic      | -              | Live notifications          |
| **Form Validation**   | Client-side validation  | React forms         | Automatic      | -              | Immediate feedback          |
| **PWA Support**       | Progressive web app     | Service worker      | Automatic      | -              | Offline capabilities        |

---
