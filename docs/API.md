# API Reference

Complete REST API documentation for the Quantis platform. All endpoints use JSON for request and response payloads.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Users](#users-endpoints)
  - [Datasets](#datasets-endpoints)
  - [Models](#models-endpoints)
  - [Predictions](#predictions-endpoints)
  - [Financial](#financial-endpoints)
  - [Monitoring](#monitoring-endpoints)
  - [Notifications](#notifications-endpoints)

---

## Base URL

| Environment           | Base URL                          |
| --------------------- | --------------------------------- |
| **Local Development** | `http://localhost:8000`           |
| **Docker Compose**    | `http://localhost:8000`           |
| **Production**        | `https://api.quantis.example.com` |

**API Version**: v1 (prefix `/api/v1` is included in production deployments)

---

## Authentication

Quantis API uses **JWT (JSON Web Tokens)** for authentication.

### Authentication Methods

| Method        | Header Format                   | Use Case                         |
| ------------- | ------------------------------- | -------------------------------- |
| **JWT Token** | `Authorization: Bearer <token>` | General API access               |
| **API Key**   | `X-API-Key: <api_key>`          | Service-to-service communication |

### Obtaining a Token

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token

```bash
GET /api/resource
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Rate Limiting

Rate limits prevent API abuse and ensure fair usage.

| Endpoint Type      | Rate Limit    | Window   |
| ------------------ | ------------- | -------- |
| **Authentication** | 10 requests   | 1 minute |
| **Predictions**    | 100 requests  | 1 minute |
| **General API**    | 1000 requests | 1 hour   |
| **WebSocket**      | 5 connections | per user |

**Rate Limit Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Response Format

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "timestamp": "2025-12-30T10:30:00Z"
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "error": "Invalid email format"
    }
  },
  "timestamp": "2025-12-30T10:30:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code    | Meaning               | Description                              |
| ------- | --------------------- | ---------------------------------------- |
| **200** | OK                    | Request successful                       |
| **201** | Created               | Resource created successfully            |
| **204** | No Content            | Request successful, no content to return |
| **400** | Bad Request           | Invalid request parameters               |
| **401** | Unauthorized          | Authentication required or failed        |
| **403** | Forbidden             | Insufficient permissions                 |
| **404** | Not Found             | Resource not found                       |
| **422** | Unprocessable Entity  | Validation error                         |
| **429** | Too Many Requests     | Rate limit exceeded                      |
| **500** | Internal Server Error | Server error occurred                    |

### Error Codes

| Error Code             | Description              |
| ---------------------- | ------------------------ |
| `VALIDATION_ERROR`     | Input validation failed  |
| `AUTHENTICATION_ERROR` | Authentication failed    |
| `AUTHORIZATION_ERROR`  | Insufficient permissions |
| `NOT_FOUND`            | Resource not found       |
| `RATE_LIMIT_EXCEEDED`  | Too many requests        |
| `INTERNAL_ERROR`       | Server error             |

---

## Endpoints

### Authentication Endpoints

Authentication and user session management.

#### POST /auth/register

Register a new user account.

| Parameter          | Type   | Required | Default | Description                      | Example            |
| ------------------ | ------ | -------- | ------- | -------------------------------- | ------------------ |
| `username`         | string | Yes      | -       | Unique username (3-50 chars)     | "john_doe"         |
| `email`            | string | Yes      | -       | Valid email address              | "john@example.com" |
| `password`         | string | Yes      | -       | Password (min 12 chars, complex) | "MyP@ssw0rd!2025"  |
| `confirm_password` | string | Yes      | -       | Password confirmation            | "MyP@ssw0rd!2025"  |
| `first_name`       | string | No       | null    | User's first name                | "John"             |
| `last_name`        | string | No       | null    | User's last name                 | "Doe"              |

**Example Request:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "MyP@ssw0rd!2025",
    "confirm_password": "MyP@ssw0rd!2025",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Example Response (201):**

```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-30T10:30:00Z"
}
```

#### POST /auth/login

Authenticate and obtain access tokens.

| Parameter     | Type    | Required | Default | Description          | Example           |
| ------------- | ------- | -------- | ------- | -------------------- | ----------------- |
| `username`    | string  | Yes      | -       | Username or email    | "john_doe"        |
| `password`    | string  | Yes      | -       | User password        | "MyP@ssw0rd!2025" |
| `remember_me` | boolean | No       | false   | Extended session     | true              |
| `mfa_code`    | string  | No       | null    | Two-factor auth code | "123456"          |

**Example Request:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "MyP@ssw0rd!2025"
  }'
```

**Example Response (200):**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

#### POST /auth/refresh

Refresh an expired access token.

| Parameter       | Type   | Required | Default | Description         | Example                      |
| --------------- | ------ | -------- | ------- | ------------------- | ---------------------------- |
| `refresh_token` | string | Yes      | -       | Valid refresh token | "eyJ0eXAiOiJKV1QiLCJhbGc..." |

**Example Request:**

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

### Users Endpoints

User management and profile operations.

#### GET /users

Get all users (admin only).

**Query Parameters:**

| Parameter   | Type    | Required | Default | Description               | Example |
| ----------- | ------- | -------- | ------- | ------------------------- | ------- |
| `skip`      | integer | No       | 0       | Number of records to skip | 0       |
| `limit`     | integer | No       | 100     | Maximum records to return | 50      |
| `is_active` | boolean | No       | -       | Filter by active status   | true    |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/users?skip=0&limit=10" \
  -H "Authorization: Bearer <token>"
```

**Example Response (200):**

```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "role": "user",
    "created_at": "2025-12-30T10:30:00Z"
  }
]
```

#### GET /users/{user_id}

Get specific user details.

**Example Request:**

```bash
curl -X GET http://localhost:8000/users/1 \
  -H "Authorization: Bearer <token>"
```

#### PUT /users/{user_id}

Update user information.

| Parameter      | Type   | Required | Default | Description        | Example            |
| -------------- | ------ | -------- | ------- | ------------------ | ------------------ |
| `first_name`   | string | No       | -       | Updated first name | "John"             |
| `last_name`    | string | No       | -       | Updated last name  | "Smith"            |
| `phone_number` | string | No       | -       | Phone number       | "+1234567890"      |
| `timezone`     | string | No       | "UTC"   | User timezone      | "America/New_York" |

---

### Datasets Endpoints

Dataset management for training and analysis.

#### POST /datasets

Create a new dataset.

| Parameter      | Type   | Required | Default | Description         | Example              |
| -------------- | ------ | -------- | ------- | ------------------- | -------------------- |
| `name`         | string | Yes      | -       | Dataset name        | "Stock Prices 2024"  |
| `description`  | string | No       | null    | Dataset description | "Daily stock prices" |
| `dataset_type` | string | Yes      | -       | Type of dataset     | "time_series"        |
| `source`       | string | No       | null    | Data source         | "Yahoo Finance"      |

**Example Request:**

```bash
curl -X POST http://localhost:8000/datasets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Stock Prices 2024",
    "description": "Daily stock prices for FAANG stocks",
    "dataset_type": "time_series",
    "source": "Yahoo Finance"
  }'
```

#### POST /datasets/upload

Upload dataset file.

| Parameter | Type   | Required | Default | Description                       | Example        |
| --------- | ------ | -------- | ------- | --------------------------------- | -------------- |
| `file`    | file   | Yes      | -       | Dataset file (CSV, JSON, Parquet) | stock_data.csv |
| `name`    | string | Yes      | -       | Dataset name                      | "Market Data"  |

**Example Request:**

```bash
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/data.csv" \
  -F "name=Market Data"
```

#### GET /datasets

List all datasets.

**Query Parameters:**

| Parameter      | Type    | Required | Default | Description       | Example       |
| -------------- | ------- | -------- | ------- | ----------------- | ------------- |
| `skip`         | integer | No       | 0       | Pagination offset | 0             |
| `limit`        | integer | No       | 100     | Max results       | 20            |
| `dataset_type` | string  | No       | -       | Filter by type    | "time_series" |

#### GET /datasets/{dataset_id}

Get dataset details.

**Example Request:**

```bash
curl -X GET http://localhost:8000/datasets/1 \
  -H "Authorization: Bearer <token>"
```

#### GET /datasets/{dataset_id}/stats

Get dataset statistics.

**Example Response (200):**

```json
{
  "total_rows": 10000,
  "total_columns": 15,
  "numeric_columns": 12,
  "categorical_columns": 3,
  "missing_values": 25,
  "memory_usage_mb": 1.5
}
```

#### GET /datasets/{dataset_id}/preview

Preview dataset rows.

**Query Parameters:**

| Parameter | Type    | Required | Default | Description    | Example |
| --------- | ------- | -------- | ------- | -------------- | ------- |
| `limit`   | integer | No       | 10      | Number of rows | 20      |

---

### Models Endpoints

ML model management and training.

#### POST /models

Create a new model.

| Parameter         | Type   | Required | Default | Description       | Example             |
| ----------------- | ------ | -------- | ------- | ----------------- | ------------------- |
| `name`            | string | Yes      | -       | Model name        | "LSTM Forecaster"   |
| `model_type`      | string | Yes      | -       | Model type        | "lstm"              |
| `description`     | string | No       | null    | Model description | "Time series LSTM"  |
| `hyperparameters` | object | No       | {}      | Model config      | {"hidden_size": 64} |

**Example Request:**

```bash
curl -X POST http://localhost:8000/models \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LSTM Stock Forecaster",
    "model_type": "lstm",
    "description": "LSTM model for stock price prediction",
    "hyperparameters": {
      "hidden_size": 64,
      "num_layers": 2,
      "dropout": 0.2
    }
  }'
```

#### POST /models/{model_id}/train

Train a model.

| Parameter       | Type    | Required | Default | Description         | Example |
| --------------- | ------- | -------- | ------- | ------------------- | ------- |
| `dataset_id`    | integer | Yes      | -       | Training dataset ID | 1       |
| `epochs`        | integer | No       | 100     | Training epochs     | 50      |
| `batch_size`    | integer | No       | 32      | Batch size          | 64      |
| `learning_rate` | float   | No       | 0.001   | Learning rate       | 0.0001  |

**Example Request:**

```bash
curl -X POST http://localhost:8000/models/1/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
  }'
```

#### GET /models

List all models.

#### GET /models/{model_id}/metrics

Get model performance metrics.

**Example Response (200):**

```json
{
  "accuracy": 0.95,
  "precision": 0.94,
  "recall": 0.93,
  "f1_score": 0.935,
  "mse": 0.025,
  "mae": 0.015,
  "r2_score": 0.92
}
```

#### GET /models/compare

Compare multiple models.

**Query Parameters:**

| Parameter   | Type   | Required | Default | Description               | Example |
| ----------- | ------ | -------- | ------- | ------------------------- | ------- |
| `model_ids` | string | Yes      | -       | Comma-separated model IDs | "1,2,3" |

---

### Predictions Endpoints

Generate predictions using trained models.

#### POST /predict

Generate prediction.

| Parameter    | Type    | Required | Default | Description     | Example         |
| ------------ | ------- | -------- | ------- | --------------- | --------------- |
| `model_id`   | integer | Yes      | -       | Model ID to use | 1               |
| `input_data` | array   | Yes      | -       | Input features  | [0.1, 0.2, 0.3] |

**Example Request:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "input_data": [0.15, 0.25, 0.35, 0.45]
  }'
```

**Example Response (200):**

```json
{
  "prediction_id": 12345,
  "model_id": 1,
  "prediction_result": [0.72, 0.28],
  "confidence_score": 0.85,
  "execution_time_ms": 45,
  "timestamp": "2025-12-30T10:30:00Z"
}
```

#### POST /predict/batch

Batch prediction.

| Parameter         | Type    | Required | Default | Description          | Example                  |
| ----------------- | ------- | -------- | ------- | -------------------- | ------------------------ |
| `model_id`        | integer | Yes      | -       | Model ID             | 1                        |
| `input_data_list` | array   | Yes      | -       | List of input arrays | [[0.1, 0.2], [0.3, 0.4]] |

#### GET /predictions/history

Get prediction history.

**Query Parameters:**

| Parameter  | Type    | Required | Default | Description       | Example |
| ---------- | ------- | -------- | ------- | ----------------- | ------- |
| `skip`     | integer | No       | 0       | Pagination offset | 0       |
| `limit`    | integer | No       | 100     | Max results       | 50      |
| `model_id` | integer | No       | -       | Filter by model   | 1       |

#### GET /predictions/stats

Get prediction statistics.

**Example Response (200):**

```json
{
  "total_predictions": 5000,
  "avg_confidence": 0.87,
  "avg_execution_time_ms": 42,
  "predictions_by_model": {
    "1": 3000,
    "2": 2000
  }
}
```

---

### Financial Endpoints

Financial transaction and calculation endpoints.

#### POST /financial/transactions

Create financial transaction.

| Parameter          | Type   | Required | Default | Description             | Example           |
| ------------------ | ------ | -------- | ------- | ----------------------- | ----------------- |
| `amount`           | number | Yes      | -       | Transaction amount      | 1000.00           |
| `currency`         | string | Yes      | -       | Currency code           | "USD"             |
| `transaction_type` | string | Yes      | -       | Transaction type        | "deposit"         |
| `description`      | string | No       | null    | Transaction description | "Initial deposit" |

**Example Request:**

```bash
curl -X POST http://localhost:8000/financial/transactions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.00,
    "currency": "USD",
    "transaction_type": "deposit",
    "description": "Initial deposit"
  }'
```

#### GET /financial/financial-summary

Get financial summary.

**Example Response (200):**

```json
{
  "total_balance": 10000.0,
  "total_deposits": 15000.0,
  "total_withdrawals": 5000.0,
  "pending_transactions": 3,
  "last_updated": "2025-12-30T10:30:00Z"
}
```

#### POST /financial/calculate-npv

Calculate Net Present Value.

| Parameter    | Type   | Required | Default | Description      | Example         |
| ------------ | ------ | -------- | ------- | ---------------- | --------------- |
| `rate`       | number | Yes      | -       | Discount rate    | 0.1             |
| `cash_flows` | array  | Yes      | -       | Cash flow values | [100, 200, 300] |

---

### Monitoring Endpoints

System health and monitoring.

#### GET /monitoring/health

Check system health.

**Example Response (200):**

```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T10:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  },
  "uptime_seconds": 86400
}
```

#### GET /monitoring/stats

Get system statistics.

**Example Response (200):**

```json
{
  "cpu_percent": 45.2,
  "memory_percent": 62.8,
  "disk_percent": 35.5,
  "active_users": 150,
  "total_requests_today": 10000
}
```

#### GET /monitoring/audit-logs

Get audit logs (admin only).

**Query Parameters:**

| Parameter     | Type    | Required | Default | Description       | Example      |
| ------------- | ------- | -------- | ------- | ----------------- | ------------ |
| `skip`        | integer | No       | 0       | Pagination offset | 0            |
| `limit`       | integer | No       | 100     | Max results       | 50           |
| `action_type` | string  | No       | -       | Filter by action  | "user.login" |

---

### Notifications Endpoints

User notification management.

#### GET /notifications

Get user notifications.

**Example Response (200):**

```json
[
  {
    "id": 1,
    "type": "info",
    "title": "Model Training Complete",
    "message": "Your LSTM model has finished training",
    "is_read": false,
    "created_at": "2025-12-30T10:30:00Z"
  }
]
```

#### PATCH /notifications/{notification_id}/read

Mark notification as read.

#### POST /notifications/mark-all-read

Mark all notifications as read.

---

## WebSocket Endpoints

Real-time data streaming via WebSocket.

### WS /ws/notifications

Real-time notification stream.

**Example (JavaScript):**

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/notifications?token=<jwt_token>'
);

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};
```

---

## API Versioning

The API uses URL versioning:

| Version | Base Path | Status  |
| ------- | --------- | ------- |
| **v1**  | `/api/v1` | Current |

Breaking changes will result in a new version. Non-breaking changes will be added to the current version.

---

## Best Practices

1. **Always use HTTPS** in production
2. **Store tokens securely** - never in localStorage for sensitive apps
3. **Handle rate limits gracefully** - implement exponential backoff
4. **Validate inputs** on client side before API calls
5. **Use batch endpoints** when making multiple similar requests
6. **Monitor your API usage** through the dashboard

---

## Code Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "john_doe",
    "password": "MyP@ssw0rd!2025"
})
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/models", headers=headers)
models = response.json()
print(f"Found {len(models)} models")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8000';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'MyP@ssw0rd!2025',
  }),
});
const { access_token } = await loginResponse.json();

// Make authenticated request
const modelsResponse = await fetch(`${BASE_URL}/models`, {
  headers: { Authorization: `Bearer ${access_token}` },
});
const models = await modelsResponse.json();
console.log(`Found ${models.length} models`);
```

---
