# Configuration Guide

Complete configuration reference for the Quantis platform, including environment variables, configuration files, and deployment settings.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Environment Variables](#environment-variables)
- [Configuration Files](#configuration-files)
- [Database Configuration](#database-configuration)
- [Security Configuration](#security-configuration)
- [API Configuration](#api-configuration)
- [ML Model Configuration](#ml-model-configuration)
- [Monitoring Configuration](#monitoring-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Docker Configuration](#docker-configuration)
- [Kubernetes Configuration](#kubernetes-configuration)

---

## Configuration Overview

Quantis uses a hierarchical configuration system:

1. **Environment Variables** (highest priority)
2. **Configuration Files** (`.env`, `config.yaml`)
3. **Default Values** (lowest priority, in code)

**Configuration Precedence:**

```
Environment Variables > .env File > config.yaml > Code Defaults
```

---

## Environment Variables

### Application Settings

| Option        | Type    | Default       | Description                                  | Where to set (env/file) |
| ------------- | ------- | ------------- | -------------------------------------------- | ----------------------- |
| `APP_NAME`    | string  | "Quantis API" | Application name                             | `.env`                  |
| `APP_VERSION` | string  | "1.0.0"       | Application version                          | `.env`                  |
| `ENVIRONMENT` | string  | "development" | Environment (development/staging/production) | `.env`                  |
| `DEBUG`       | boolean | False         | Enable debug mode                            | `.env`                  |
| `HOST`        | string  | "0.0.0.0"     | API host address                             | `.env`                  |
| `PORT`        | integer | 8000          | API port number                              | `.env`                  |
| `RELOAD`      | boolean | False         | Auto-reload on code changes                  | `.env`                  |

**Example:**

```bash
# .env file
APP_NAME=Quantis API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### Security Settings

| Option                        | Type    | Default                  | Description                     | Where to set (env/file) |
| ----------------------------- | ------- | ------------------------ | ------------------------------- | ----------------------- |
| `SECRET_KEY`                  | string  | "dev-key-change-in-prod" | Application secret key          | `.env` (required)       |
| `JWT_SECRET`                  | string  | "dev-jwt-change-in-prod" | JWT signing secret              | `.env` (required)       |
| `ALGORITHM`                   | string  | "HS256"                  | JWT algorithm                   | `.env`                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | 30                       | Access token lifetime (minutes) | `.env`                  |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | integer | 7                        | Refresh token lifetime (days)   | `.env`                  |
| `MAX_LOGIN_ATTEMPTS`          | integer | 5                        | Max failed login attempts       | `.env`                  |
| `LOCKOUT_DURATION_MINUTES`    | integer | 15                       | Account lockout duration        | `.env`                  |
| `MAX_CONCURRENT_SESSIONS`     | integer | 5                        | Max simultaneous sessions       | `.env`                  |

**Example:**

```bash
# Security configuration
SECRET_KEY=your-super-secret-key-min-32-chars-recommended
JWT_SECRET=your-jwt-secret-key-different-from-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ Security Best Practices:**

- Never commit `.env` file to version control
- Use strong, randomly generated keys (minimum 32 characters)
- Rotate secrets regularly in production
- Use different secrets for different environments

### Database Settings

| Option            | Type    | Default                  | Description              | Where to set (env/file) |
| ----------------- | ------- | ------------------------ | ------------------------ | ----------------------- |
| `DATABASE_URL`    | string  | "sqlite:///./quantis.db" | Database connection URL  | `.env` (required)       |
| `DB_POOL_SIZE`    | integer | 5                        | Connection pool size     | `.env`                  |
| `DB_MAX_OVERFLOW` | integer | 10                       | Max overflow connections | `.env`                  |
| `DB_POOL_TIMEOUT` | integer | 30                       | Pool timeout (seconds)   | `.env`                  |
| `DB_POOL_RECYCLE` | integer | 3600                     | Connection recycle time  | `.env`                  |

**Example:**

```bash
# SQLite (Development)
DATABASE_URL=sqlite:///./quantis.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/quantis

# PostgreSQL with SSL
DATABASE_URL=postgresql://user:password@host:5432/quantis?sslmode=require

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/quantis
```

### Redis Configuration

| Option                  | Type   | Default | Description           | Where to set (env/file) |
| ----------------------- | ------ | ------- | --------------------- | ----------------------- |
| `REDIS_URL`             | string | null    | Redis connection URL  | `.env` (optional)       |
| `CELERY_BROKER_URL`     | string | null    | Celery broker URL     | `.env` (optional)       |
| `CELERY_RESULT_BACKEND` | string | null    | Celery result backend | `.env` (optional)       |

**Example:**

```bash
# Redis configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Redis with authentication
REDIS_URL=redis://:password@localhost:6379/0

# Redis Sentinel
REDIS_URL=redis-sentinel://localhost:26379/mymaster/0
```

### CORS & Security Headers

| Option           | Type    | Default | Description               | Where to set (env/file) |
| ---------------- | ------- | ------- | ------------------------- | ----------------------- |
| `CORS_ORIGINS`   | list    | ["*"]   | Allowed CORS origins      | `.env`                  |
| `ALLOWED_HOSTS`  | list    | ["*"]   | Allowed host headers      | `.env`                  |
| `ENABLE_METRICS` | boolean | True    | Enable Prometheus metrics | `.env`                  |

**Example:**

```bash
# Development - allow all origins
CORS_ORIGINS=["*"]

# Production - specific origins only
CORS_ORIGINS=["https://quantis.example.com","https://app.quantis.example.com"]

ALLOWED_HOSTS=["quantis.example.com","www.quantis.example.com"]
```

### Email Configuration (Optional)

| Option            | Type    | Default   | Description          | Where to set (env/file) |
| ----------------- | ------- | --------- | -------------------- | ----------------------- |
| `SMTP_SERVER`     | string  | null      | SMTP server address  | `.env`                  |
| `SMTP_PORT`       | integer | 587       | SMTP server port     | `.env`                  |
| `SMTP_USERNAME`   | string  | null      | SMTP username        | `.env`                  |
| `SMTP_PASSWORD`   | string  | null      | SMTP password        | `.env`                  |
| `SMTP_USE_TLS`    | boolean | True      | Use TLS encryption   | `.env`                  |
| `SMTP_FROM_EMAIL` | string  | null      | Default sender email | `.env`                  |
| `SMTP_FROM_NAME`  | string  | "Quantis" | Default sender name  | `.env`                  |

**Example:**

```bash
# Gmail SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
SMTP_FROM_EMAIL=no-reply@quantis.example.com
SMTP_FROM_NAME=Quantis Platform

# AWS SES
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-username
SMTP_PASSWORD=your-ses-password
```

### Storage Configuration

| Option                      | Type    | Default                     | Description               | Where to set (env/file) |
| --------------------------- | ------- | --------------------------- | ------------------------- | ----------------------- |
| `STORAGE_DIRECTORY`         | string  | "./models"                  | Model storage directory   | `.env`                  |
| `DATASET_DIRECTORY`         | string  | "./datasets"                | Dataset storage directory | `.env`                  |
| `UPLOAD_MAX_SIZE_MB`        | integer | 100                         | Max upload size (MB)      | `.env`                  |
| `ALLOWED_UPLOAD_EXTENSIONS` | list    | [".csv",".parquet",".json"] | Allowed file types        | `.env`                  |

**Example:**

```bash
STORAGE_DIRECTORY=/var/lib/quantis/models
DATASET_DIRECTORY=/var/lib/quantis/datasets
UPLOAD_MAX_SIZE_MB=500
ALLOWED_UPLOAD_EXTENSIONS=[".csv",".parquet",".json",".xlsx"]
```

### Logging Configuration

| Option                 | Type    | Default | Description            | Where to set (env/file) |
| ---------------------- | ------- | ------- | ---------------------- | ----------------------- |
| `LOG_LEVEL`            | string  | "INFO"  | Logging level          | `.env`                  |
| `LOG_FORMAT`           | string  | "json"  | Log format (json/text) | `.env`                  |
| `ENABLE_AUDIT_LOGGING` | boolean | True    | Enable audit logs      | `.env`                  |
| `LOG_FILE_PATH`        | string  | null    | Log file path          | `.env`                  |

**Example:**

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_AUDIT_LOGGING=True
LOG_FILE_PATH=/var/log/quantis/api.log
```

---

## Configuration Files

### .env File Template

Create a `.env` file in `code/api/` directory:

```bash
# Application Settings
APP_NAME=Quantis API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-characters-recommended-use-strong-random
JWT_SECRET=your-jwt-secret-key-different-from-secret-key-also-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://quantis_user:secure_password@localhost:5432/quantis
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis (optional but recommended)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# CORS & Security
CORS_ORIGINS=["https://quantis.example.com"]
ALLOWED_HOSTS=["quantis.example.com","api.quantis.example.com"]

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True

# Storage
STORAGE_DIRECTORY=/var/lib/quantis/models
DATASET_DIRECTORY=/var/lib/quantis/datasets
UPLOAD_MAX_SIZE_MB=500

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_AUDIT_LOGGING=True

# Monitoring
ENABLE_METRICS=True
```

---

## Database Configuration

### SQLite (Development)

```bash
# Simplest setup for local development
DATABASE_URL=sqlite:///./quantis.db
```

**Pros:** No setup required, portable  
**Cons:** Not suitable for production, limited concurrency

### PostgreSQL (Recommended for Production)

```bash
# Standard connection
DATABASE_URL=postgresql://username:password@hostname:5432/database_name

# With connection pooling
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?pool_size=10

# With SSL
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require

# Unix socket connection
DATABASE_URL=postgresql:///database_name?host=/var/run/postgresql
```

**Connection Pool Settings:**

```bash
DB_POOL_SIZE=10          # Ideal: 10-20 for API server
DB_MAX_OVERFLOW=20       # Additional connections when needed
DB_POOL_TIMEOUT=30       # Seconds to wait for connection
DB_POOL_RECYCLE=3600     # Recycle connections every hour
```

### MySQL/MariaDB

```bash
DATABASE_URL=mysql+pymysql://username:password@hostname:3306/database_name
```

---

## Security Configuration

### Password Requirements

Configure in `code/api/schemas.py`:

```python
# Minimum password length: 12 characters
# Must include:
# - At least one uppercase letter
# - At least one lowercase letter
# - At least one digit
# - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
```

### Rate Limiting

Configure in `code/api/middleware/auth.py`:

| Endpoint Type  | Limit         | Window   |
| -------------- | ------------- | -------- |
| Authentication | 10 requests   | 1 minute |
| Predictions    | 100 requests  | 1 minute |
| General API    | 1000 requests | 1 hour   |

**Custom Rate Limits:**

```python
# In code/api/middleware/auth.py
@rate_limit(max_requests=50, window_seconds=60)
async def custom_endpoint():
    pass
```

### Two-Factor Authentication

Enable MFA for users:

```bash
# User enables MFA via API
POST /auth/mfa/enable
# Returns QR code for authenticator app

# Login with MFA
POST /auth/login
{
  "username": "user",
  "password": "password",
  "mfa_code": "123456"
}
```

---

## API Configuration

### Uvicorn Settings (Production)

```bash
# Start with production settings
uvicorn api.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log \
  --no-reload \
  --limit-concurrency 1000 \
  --limit-max-requests 10000
```

### Worker Configuration

```bash
# Number of workers (recommended: 2-4 * CPU cores)
WORKERS=4

# Worker class
WORKER_CLASS=uvicorn.workers.UvicornWorker

# Timeout (seconds)
TIMEOUT=120

# Keep alive (seconds)
KEEPALIVE=5
```

---

## ML Model Configuration

### Model Hyperparameters

Default hyperparameters in `code/models/train_model.py`:

```python
# LSTM Model
DEFAULT_LSTM_PARAMS = {
    "input_size": 10,
    "hidden_size": 64,
    "output_size": 3,
    "num_layers": 2,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
    "dropout": 0.2
}

# Temporal Fusion Transformer
DEFAULT_TFT_PARAMS = {
    "input_size": 128,
    "hidden_size": 160,
    "attention_heads": 4,
    "dropout": 0.1,
    "learning_rate": 0.0001
}
```

### MLflow Configuration

```bash
# MLflow tracking
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=quantis_models

# Artifact storage
MLFLOW_ARTIFACT_URI=s3://my-bucket/mlflow-artifacts
# Or local: file:///var/lib/quantis/mlflow
```

---

## Monitoring Configuration

### Prometheus Settings

Configure in `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'quantis-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana Configuration

```yaml
# grafana.ini
[server]
http_port = 3000
root_url = http://localhost:3000

[security]
admin_user = admin
admin_password = secure_password_change_me

[auth]
disable_login_form = false

[analytics]
reporting_enabled = false
```

---

## Frontend Configuration

### Environment Variables

Create `web-frontend/.env`:

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_NOTIFICATIONS=true

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
```

### Production Build

```bash
# Build for production
cd web-frontend
npm run build

# Serve with nginx or similar
```

---

## Docker Configuration

### Docker Compose Environment

Edit `infrastructure/docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/quantis
      - REDIS_URL=redis://redis:6379/0
    ports:
      - '8000:8000'

  frontend:
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000
    ports:
      - '80:80'

  db:
    environment:
      - POSTGRES_USER=quantis
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=quantis
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    command: redis-server --requirepass secure_redis_password

volumes:
  postgres-data:
```

---

## Kubernetes Configuration

### ConfigMap

Create `infrastructure/kubernetes/config/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: quantis-config
  namespace: quantis
data:
  APP_NAME: 'Quantis API'
  ENVIRONMENT: 'production'
  LOG_LEVEL: 'INFO'
  REDIS_URL: 'redis://redis-service:6379/0'
```

### Secrets

Create secrets securely:

```bash
# Create secret from literals
kubectl create secret generic quantis-secrets \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=JWT_SECRET='your-jwt-secret' \
  --from-literal=DATABASE_URL='postgresql://...' \
  -n quantis

# Or from file
kubectl create secret generic quantis-secrets \
  --from-env-file=.env.production \
  -n quantis
```

---

## Configuration Validation

### Validate Configuration

```bash
# Check configuration syntax
python -c "from api.config import get_settings; print(get_settings())"

# Validate database connection
python -c "from api.database import health_check; print(health_check())"

# Test Redis connection
redis-cli -u $REDIS_URL ping
```

---

## Environment-Specific Configurations

### Development

```bash
ENVIRONMENT=development
DEBUG=True
RELOAD=True
DATABASE_URL=sqlite:///./quantis.db
CORS_ORIGINS=["*"]
LOG_LEVEL=DEBUG
```

### Staging

```bash
ENVIRONMENT=staging
DEBUG=False
RELOAD=False
DATABASE_URL=postgresql://user:pass@staging-db:5432/quantis
CORS_ORIGINS=["https://staging.quantis.example.com"]
LOG_LEVEL=INFO
```

### Production

```bash
ENVIRONMENT=production
DEBUG=False
RELOAD=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/quantis
CORS_ORIGINS=["https://quantis.example.com"]
LOG_LEVEL=WARNING
ENABLE_METRICS=True
```

---

## Configuration Best Practices

1. **Never commit secrets** - Use `.gitignore` for `.env` files
2. **Use strong secrets** - Generate with `openssl rand -hex 32`
3. **Environment-specific configs** - Different settings for dev/staging/prod
4. **Validate on startup** - Fail fast if configuration is invalid
5. **Document defaults** - Clear documentation of all options
6. **Use environment variables** - For deployment flexibility
7. **Rotate secrets regularly** - Especially in production
8. **Monitor configuration** - Track configuration changes

---
