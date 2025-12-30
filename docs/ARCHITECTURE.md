# Architecture Overview

High-level system architecture, design patterns, and module structure for the Quantis platform.

## Table of Contents

- [System Architecture](#system-architecture)
- [Architecture Diagram](#architecture-diagram)
- [Component Overview](#component-overview)
- [Module Structure](#module-structure)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability](#scalability)
- [Security Architecture](#security-architecture)

---

## System Architecture

Quantis follows a **microservices architecture** with clear separation of concerns. The platform is organized into three main service layers:

1. **Data Services Layer**: Data ingestion, processing, and storage
2. **Analytical Services Layer**: ML models, statistical analysis, predictions
3. **Presentation Layer**: API gateway, web frontend, monitoring

### Architecture Principles

- **Microservices**: Independent, loosely-coupled services
- **API-First**: RESTful API as the primary interface
- **Event-Driven**: Asynchronous processing via message queues
- **Stateless**: Horizontally scalable, no session affinity required
- **Database Per Service**: Each service owns its data
- **Cloud-Native**: Containerized, Kubernetes-ready

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
├──────────────────────┬──────────────────────┬───────────────────┤
│   Web Dashboard      │   Mobile App         │   API Clients     │
│   (React/TypeScript) │   (Planned)          │   (Python/JS)     │
└──────────┬───────────┴──────────────────────┴───────────┬───────┘
           │                                               │
           │              HTTPS / WebSocket                │
           │                                               │
┌──────────▼───────────────────────────────────────────────▼───────┐
│                        API Gateway Layer                         │
├────────────────────────────────────────────────────────────────-─┤
│  • FastAPI Application (code/api/app.py)                         │
│  • Authentication & Authorization                                │
│  • Rate Limiting & Request Validation                            │
│  • CORS & Security Headers                                       │
│  • API Documentation (OpenAPI/Swagger)                           │
└──────────┬───────────────────────────────────────────────┬───────┘
           │                                               │
┌──────────▼───────────────────────────────────────────────▼───────┐
│                      Service Layer                               │
├──────────────────────┬────────────────────┬─────────────────────┤
│   Auth Service       │   Model Service    │   Data Service      │
│ ┌────────────────┐   │ ┌──────────────┐   │ ┌─────────────┐    │
│ │ User Mgmt      │   │ │ Training     │   │ │ Ingestion   │    │
│ │ JWT Tokens     │   │ │ Inference    │   │ │ Processing  │    │
│ │ RBAC           │   │ │ Versioning   │   │ │ Validation  │    │
│ │ Sessions       │   │ │ Comparison   │   │ │ Storage     │    │
│ └────────────────┘   │ └──────────────┘   │ └─────────────┘    │
├──────────────────────┼────────────────────┼─────────────────────┤
│ Financial Service    │ Prediction Service │ Monitoring Service  │
│ ┌────────────────┐   │ ┌──────────────┐   │ ┌─────────────┐    │
│ │ Transactions   │   │ │ Single Pred  │   │ │ Metrics     │    │
│ │ NPV Calc       │   │ │ Batch Pred   │   │ │ Health      │    │
│ │ Interest       │   │ │ History      │   │ │ Audit Logs  │    │
│ │ Compliance     │   │ │ Analytics    │   │ │ Alerts      │    │
│ └────────────────┘   │ └──────────────┘   │ └─────────────┘    │
└──────────────────────┴────────────────────┴─────────────────────┘
           │                      │                     │
┌──────────▼──────────────────────▼─────────────────────▼───────────┐
│                       Data Layer                                   │
├───────────────────┬─────────────────────┬──────────────────────────┤
│   PostgreSQL      │   Redis             │   Object Storage         │
│ ┌─────────────┐   │ ┌───────────────┐   │ ┌──────────────────┐    │
│ │ Users       │   │ │ Cache         │   │ │ ML Models        │    │
│ │ Models      │   │ │ Sessions      │   │ │ Datasets         │    │
│ │ Datasets    │   │ │ Rate Limits   │   │ │ Artifacts        │    │
│ │ Predictions │   │ │ Task Queue    │   │ │ Logs             │    │
│ │ Transactions│   │ └───────────────┘   │ └──────────────────┘    │
│ │ Audit Logs  │   │                     │                          │
│ └─────────────┘   │                     │                          │
└───────────────────┴─────────────────────┴──────────────────────────┘
           │                      │                     │
┌──────────▼──────────────────────▼─────────────────────▼───────────┐
│                    Infrastructure Layer                            │
├────────────────────┬────────────────────┬─────────────────────────┤
│  Docker Compose    │   Kubernetes       │   Monitoring Stack      │
│  (Local Dev)       │   (Production)     │   (Prometheus/Grafana)  │
└────────────────────┴────────────────────┴─────────────────────────┘
```

---

## Component Overview

### 1. API Gateway (`code/api/`)

**Purpose**: Single entry point for all client requests

**Responsibilities**:

- Request routing to appropriate services
- Authentication and authorization
- Rate limiting and throttling
- Request/response validation
- API documentation generation
- CORS handling

**Key Files**:

- `app.py` - Main FastAPI application
- `auth.py` - Authentication helpers
- `config.py` - Configuration management
- `database.py` - Database connections
- `models.py` - SQLAlchemy ORM models
- `schemas.py` - Pydantic validation schemas

### 2. Endpoint Modules (`code/api/endpoints/`)

**Purpose**: Business logic implementation for each domain

**Modules**:

| Module             | Purpose                        | Key Endpoints                     |
| ------------------ | ------------------------------ | --------------------------------- |
| `auth.py`          | Authentication & authorization | Login, register, MFA, API keys    |
| `users.py`         | User management                | CRUD users, roles, permissions    |
| `datasets.py`      | Dataset operations             | Upload, stats, preview, download  |
| `models.py`        | ML model management            | Create, train, compare, metrics   |
| `prediction.py`    | Inference service              | Single/batch predictions, history |
| `financial.py`     | Financial operations           | Transactions, NPV, interest calc  |
| `monitoring.py`    | System monitoring              | Health, stats, audit logs         |
| `notifications.py` | User notifications             | Get, mark read, delete            |
| `websocket.py`     | Real-time communication        | WebSocket connections             |

### 3. ML Models (`code/models/`)

**Purpose**: Machine learning training and serving

**Components**:

- `train_model.py` - Model training logic (LSTM, TFT)
- `mlflow_tracking.py` - Experiment tracking integration
- `aws_deploy.py` - Cloud deployment utilities
- `hyperparameter_tuning/optimize.py` - Auto-tuning
- `model_serving/serve.py` - Model serving endpoints

### 4. Data Processing (`code/data/`)

**Purpose**: Data transformation and feature engineering

**Components**:

- `process_data.py` - ETL pipeline with Dask
- `features/` - Feature engineering modules

### 5. Infrastructure (`infrastructure/`)

**Purpose**: Deployment and orchestration

**Components**:

- `docker-compose.yml` - Local multi-container setup
- `kubernetes/` - K8s manifests for production
- `terraform/` - Infrastructure as Code for cloud
- `ansible/` - Configuration management

### 6. Monitoring (`monitoring/`)

**Purpose**: Observability and alerting

**Components**:

- `prometheus.yml` - Metrics collection config
- `grafana_dashboards/` - Pre-built dashboards
- `model_monitor.py` - ML drift detection

---

## Module Structure

### Project Directory Layout

```
Quantis/
├── code/                           # Application code
│   ├── api/                        # FastAPI backend
│   │   ├── endpoints/              # API endpoints by domain
│   │   ├── middleware/             # Request/response middleware
│   │   ├── services/               # Business logic layer
│   │   ├── app.py                  # Main application
│   │   ├── models.py               # Database models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── config.py               # Settings management
│   │   ├── database.py             # DB connection & sessions
│   │   └── tasks.py                # Celery background tasks
│   ├── data/                       # Data processing
│   │   ├── process_data.py         # ETL pipeline
│   │   └── features/               # Feature engineering
│   ├── models/                     # ML models
│   │   ├── train_model.py          # Training logic
│   │   ├── mlflow_tracking.py      # Experiment tracking
│   │   ├── aws_deploy.py           # Cloud deployment
│   │   └── hyperparameter_tuning/  # Auto-tuning
│   └── scripts/                    # Utility scripts
├── docs/                           # Documentation
├── infrastructure/                 # Deployment configs
│   ├── docker-compose.yml          # Docker setup
│   ├── kubernetes/                 # K8s manifests
│   ├── terraform/                  # IaC templates
│   └── ansible/                    # Config management
├── monitoring/                     # Observability
│   ├── prometheus.yml              # Metrics config
│   ├── grafana_dashboards/         # Dashboards
│   └── model_monitor.py            # Drift detection
├── scripts/                        # Automation scripts
│   ├── setup_quantis_env.sh        # Initial setup
│   ├── run_quantis.sh              # Start services
│   ├── test_quantis.sh             # Run tests
│   └── build_quantis.sh            # Build artifacts
├── tests/                          # Test suites
│   ├── conftest.py                 # Test configuration
│   ├── test_api.py                 # API tests
│   └── requirements-test.txt       # Test dependencies
├── web-frontend/                   # React application
│   ├── public/                     # Static assets
│   ├── src/                        # React components
│   └── package.json                # Node dependencies
└── README.md                       # Project overview
```

---

## Data Flow

### 1. User Authentication Flow

```
User → POST /auth/login
  ↓
API Gateway (auth.py)
  ↓
Validate credentials (bcrypt)
  ↓
Check MFA if enabled (TOTP)
  ↓
Generate JWT tokens (access + refresh)
  ↓
Create session record (database)
  ↓
Log audit event
  ↓
Return tokens to user
```

### 2. Model Training Flow

```
User → POST /models/{id}/train
  ↓
API Gateway (models.py)
  ↓
Validate request & auth
  ↓
Create training task (Celery)
  ↓
Background Worker:
  ├─ Load dataset from storage
  ├─ Preprocess data (scaling, encoding)
  ├─ Initialize model (LSTM/TFT)
  ├─ Train model (epochs, batches)
  ├─ Track metrics (MLflow)
  ├─ Save model artifacts
  └─ Update model status
  ↓
Return training ID to user
  ↓
User polls /models/{id}/training-status
```

### 3. Prediction Flow

```
User → POST /predict
  ↓
API Gateway (prediction.py)
  ↓
Rate limit check (Redis)
  ↓
Validate input schema (Pydantic)
  ↓
Load model from cache/storage
  ↓
Preprocess input data
  ↓
Run inference (model.predict)
  ↓
Calculate confidence score
  ↓
Store prediction record (database)
  ↓
Log metrics (Prometheus)
  ↓
Return prediction result
```

### 4. Real-time Notification Flow

```
System Event (e.g., training complete)
  ↓
Create notification record (database)
  ↓
Publish to WebSocket connections
  ↓
Active WebSocket clients receive message
  ↓
Frontend displays notification
  ↓
User acknowledges (PATCH /notifications/{id}/read)
```

---

## Technology Stack

### Backend Technologies

| Technology     | Version | Purpose             |
| -------------- | ------- | ------------------- |
| **Python**     | 3.9+    | Primary language    |
| **FastAPI**    | 0.109+  | Web framework       |
| **Uvicorn**    | 0.27+   | ASGI server         |
| **SQLAlchemy** | 2.0+    | ORM layer           |
| **Pydantic**   | 2.5+    | Data validation     |
| **Celery**     | 5.3+    | Task queue          |
| **Redis**      | 5.0+    | Cache & queue       |
| **PostgreSQL** | 14+     | Relational database |

### ML & Data Technologies

| Technology       | Version | Purpose             |
| ---------------- | ------- | ------------------- |
| **PyTorch**      | 2.0+    | Deep learning       |
| **scikit-learn** | 1.4+    | Classical ML        |
| **pandas**       | 2.2+    | Data manipulation   |
| **numpy**        | 1.26+   | Numerical computing |
| **Dask**         | Latest  | Parallel processing |
| **MLflow**       | 2.8+    | Experiment tracking |

### Infrastructure Technologies

| Technology     | Version | Purpose                  |
| -------------- | ------- | ------------------------ |
| **Docker**     | 20.10+  | Containerization         |
| **Kubernetes** | 1.20+   | Orchestration            |
| **Terraform**  | 1.0+    | Infrastructure as Code   |
| **Ansible**    | 2.9+    | Configuration management |
| **Prometheus** | 2.45+   | Metrics collection       |
| **Grafana**    | 10.2+   | Visualization            |

---

## Design Patterns

### 1. Repository Pattern

**Used in**: Database access layer

```python
# code/api/database.py
class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int):
        return self.db.query(Model).filter(Model.id == id).first()

    def create(self, obj: dict):
        db_obj = Model(**obj)
        self.db.add(db_obj)
        self.db.commit()
        return db_obj
```

### 2. Dependency Injection

**Used in**: FastAPI endpoints

```python
# code/api/endpoints/users.py
@router.get("/users")
async def get_users(
    db: Session = Depends(get_db),          # DB injection
    current_user = Depends(get_current_user) # Auth injection
):
    return db.query(User).all()
```

### 3. Middleware Pattern

**Used in**: Request/response processing

```python
# code/api/middleware/auth.py
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Pre-processing
        token = request.headers.get("Authorization")
        # Process request
        response = await call_next(request)
        # Post-processing
        return response
```

### 4. Factory Pattern

**Used in**: Model instantiation

```python
# code/models/train_model.py
def create_model(model_type: str, params: dict):
    if model_type == "lstm":
        return LSTMModel(**params)
    elif model_type == "tft":
        return TFTModel(**params)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
```

### 5. Observer Pattern

**Used in**: Event-driven notifications

```python
# WebSocket notifications
class NotificationManager:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, websocket):
        self.subscribers.append(websocket)

    async def notify(self, message):
        for subscriber in self.subscribers:
            await subscriber.send_json(message)
```

---

## Scalability

### Horizontal Scaling

**Stateless Design**: All API instances are stateless, enabling horizontal scaling

```yaml
# Kubernetes HorizontalPodAutoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Database Scaling

- **Read Replicas**: Distribute read load across replicas
- **Connection Pooling**: Reuse connections efficiently
- **Caching**: Redis for frequently accessed data
- **Partitioning**: Table partitioning for large datasets

### Caching Strategy

```python
# Multi-layer caching
┌─────────────┐
│  Redis      │  ← Session data, rate limits (TTL: seconds-minutes)
├─────────────┤
│  Application│  ← Model cache, configs (TTL: hours)
├─────────────┤
│  Database   │  ← Persistent storage
└─────────────┘
```

---

## Security Architecture

### Defense in Depth

**Layer 1: Network Security**

- Firewall rules
- VPC isolation (cloud deployments)
- TLS/SSL encryption

**Layer 2: API Gateway**

- Rate limiting
- Input validation
- CORS policies
- Authentication

**Layer 3: Application**

- JWT token validation
- RBAC enforcement
- SQL injection prevention (ORM)
- XSS protection

**Layer 4: Data**

- Encrypted at rest (database)
- Encrypted in transit (TLS)
- Audit logging
- Backup encryption

### Security Best Practices

```python
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(plain_password)

# JWT with short expiration
token = create_access_token(
    data={"sub": user.id},
    expires_delta=timedelta(minutes=30)
)

# Rate limiting
@rate_limit(max_requests=100, window_seconds=60)
async def protected_endpoint():
    pass
```

---

## Module Dependencies

```
code/api/app.py
  ├─ endpoints/*          (API routes)
  ├─ middleware/*         (Request processing)
  ├─ database.py          (DB connections)
  ├─ models.py            (ORM models)
  ├─ schemas.py           (Validation)
  └─ config.py            (Settings)

code/api/endpoints/*
  ├─ services/*           (Business logic)
  ├─ middleware/auth.py   (Auth checks)
  ├─ schemas.py           (Input/output schemas)
  └─ database.py          (DB sessions)

code/models/train_model.py
  ├─ mlflow_tracking.py   (Experiment tracking)
  ├─ data/process_data.py (Data preprocessing)
  └─ PyTorch/scikit-learn (ML frameworks)
```

---

## Monitoring Architecture

```
Application
  ├─ Structured Logs (structlog) → Log Aggregation
  ├─ Prometheus Metrics → Prometheus Server → Grafana
  ├─ MLflow Tracking → MLflow Server
  └─ Audit Logs → Database → Compliance Reports
```

---
