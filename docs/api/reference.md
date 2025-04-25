# API Documentation

This document provides comprehensive documentation for the Quantis API, including endpoints, request/response formats, authentication, and usage examples.

## Overview

The Quantis API is built using FastAPI, a modern, high-performance web framework for building APIs with Python. The API provides endpoints for user management, data processing, model training, and prediction generation.

## Base URL

When running locally, the API is available at:
```
http://localhost:8000
```

In production environments, the API URL will depend on your deployment configuration.

## Authentication

Most API endpoints require authentication. Quantis uses JWT (JSON Web Tokens) for authentication.

### Obtaining a Token

To obtain an authentication token, send a POST request to the `/users/token` endpoint:

```
POST /users/token
```

Request body:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header of your requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

### User Management

#### Create User

```
POST /users/
```

Request body:
```json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

Response:
```json
{
  "username": "new_user",
  "email": "user@example.com",
  "full_name": "John Doe",
  "id": "user_uuid"
}
```

#### Get Current User

```
GET /users/me
```

Response:
```json
{
  "username": "current_user",
  "email": "user@example.com",
  "full_name": "John Doe",
  "id": "user_uuid"
}
```

### Predictions

#### Generate Prediction

```
POST /predictions/
```

Request body:
```json
{
  "time_series_data": [
    {"timestamp": "2023-01-01T00:00:00Z", "value": 10.5},
    {"timestamp": "2023-01-02T00:00:00Z", "value": 11.2},
    {"timestamp": "2023-01-03T00:00:00Z", "value": 10.8}
  ],
  "forecast_horizon": 7,
  "model_id": "default"
}
```

Response:
```json
{
  "prediction_id": "pred_uuid",
  "forecast": [
    {"timestamp": "2023-01-04T00:00:00Z", "value": 11.1, "lower_bound": 10.5, "upper_bound": 11.7},
    {"timestamp": "2023-01-05T00:00:00Z", "value": 11.3, "lower_bound": 10.6, "upper_bound": 12.0},
    {"timestamp": "2023-01-06T00:00:00Z", "value": 11.5, "lower_bound": 10.7, "upper_bound": 12.3},
    {"timestamp": "2023-01-07T00:00:00Z", "value": 11.7, "lower_bound": 10.8, "upper_bound": 12.6},
    {"timestamp": "2023-01-08T00:00:00Z", "value": 11.9, "lower_bound": 10.9, "upper_bound": 12.9},
    {"timestamp": "2023-01-09T00:00:00Z", "value": 12.1, "lower_bound": 11.0, "upper_bound": 13.2},
    {"timestamp": "2023-01-10T00:00:00Z", "value": 12.3, "lower_bound": 11.1, "upper_bound": 13.5}
  ],
  "model_version": "1.0.0",
  "created_at": "2023-01-03T12:34:56Z"
}
```

#### Get Prediction by ID

```
GET /predictions/{prediction_id}
```

Response:
```json
{
  "prediction_id": "pred_uuid",
  "forecast": [
    {"timestamp": "2023-01-04T00:00:00Z", "value": 11.1, "lower_bound": 10.5, "upper_bound": 11.7},
    {"timestamp": "2023-01-05T00:00:00Z", "value": 11.3, "lower_bound": 10.6, "upper_bound": 12.0},
    {"timestamp": "2023-01-06T00:00:00Z", "value": 11.5, "lower_bound": 10.7, "upper_bound": 12.3},
    {"timestamp": "2023-01-07T00:00:00Z", "value": 11.7, "lower_bound": 10.8, "upper_bound": 12.6},
    {"timestamp": "2023-01-08T00:00:00Z", "value": 11.9, "lower_bound": 10.9, "upper_bound": 12.9},
    {"timestamp": "2023-01-09T00:00:00Z", "value": 12.1, "lower_bound": 11.0, "upper_bound": 13.2},
    {"timestamp": "2023-01-10T00:00:00Z", "value": 12.3, "lower_bound": 11.1, "upper_bound": 13.5}
  ],
  "model_version": "1.0.0",
  "created_at": "2023-01-03T12:34:56Z"
}
```

#### List User Predictions

```
GET /predictions/
```

Response:
```json
{
  "predictions": [
    {
      "prediction_id": "pred_uuid1",
      "model_version": "1.0.0",
      "created_at": "2023-01-03T12:34:56Z"
    },
    {
      "prediction_id": "pred_uuid2",
      "model_version": "1.0.0",
      "created_at": "2023-01-02T10:22:33Z"
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- 200: OK - The request was successful
- 201: Created - A new resource was successfully created
- 400: Bad Request - The request was invalid or cannot be served
- 401: Unauthorized - Authentication is required or failed
- 403: Forbidden - The authenticated user doesn't have permission
- 404: Not Found - The requested resource doesn't exist
- 422: Unprocessable Entity - Validation error
- 500: Internal Server Error - An error occurred on the server

Error responses include a JSON body with details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Limits are as follows:

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

When rate limits are exceeded, the API returns a 429 Too Many Requests status code.

## Pagination

List endpoints support pagination using `skip` and `limit` query parameters:

```
GET /predictions/?skip=0&limit=10
```

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 1000)

## API Versioning

The API version is included in the URL path:

```
/api/v1/users/
```

This ensures backward compatibility as the API evolves.

## Interactive Documentation

When the API is running, interactive documentation is available at:

```
/docs
```

This Swagger UI allows you to explore and test the API endpoints directly from your browser.

## OpenAPI Specification

The OpenAPI specification for the API is available at:

```
/openapi.json
```

This can be used with various tools to generate client libraries or documentation.

## Client Libraries

Official client libraries for the Quantis API:

- Python: `pip install quantis-client`
- JavaScript: `npm install quantis-client`

## Example Usage (Python)

```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8000/users/token",
    data={"username": "user", "password": "password"}
)
token = response.json()["access_token"]

# Set up headers
headers = {"Authorization": f"Bearer {token}"}

# Get predictions
response = requests.get(
    "http://localhost:8000/predictions/",
    headers=headers
)
predictions = response.json()["predictions"]

# Generate a new prediction
new_prediction = requests.post(
    "http://localhost:8000/predictions/",
    headers=headers,
    json={
        "time_series_data": [
            {"timestamp": "2023-01-01T00:00:00Z", "value": 10.5},
            {"timestamp": "2023-01-02T00:00:00Z", "value": 11.2},
            {"timestamp": "2023-01-03T00:00:00Z", "value": 10.8}
        ],
        "forecast_horizon": 7,
        "model_id": "default"
    }
)
forecast = new_prediction.json()["forecast"]
```

## Webhooks

The API supports webhooks for asynchronous notifications:

```
POST /webhooks/
```

Request body:
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["prediction.completed", "model.trained"]
}
```

When registered events occur, the API will send a POST request to the specified URL with event details.

## Support

For API support, contact the Quantis team at api-support@quantis.example.com or open an issue in the GitHub repository.
