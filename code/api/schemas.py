"""
Enhanced Pydantic schemas for Quantis API
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr


# Base schemas
class PredictionRequest(BaseModel):
    features: List[float]
    model_id: Optional[int] = 1  # Default to model 1


class PredictionResponse(BaseModel):
    prediction: List[float]
    confidence: float


class ModelHealthResponse(BaseModel):
    status: str
    version: str


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "user"


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True


# Dataset schemas
class DatasetBase(BaseModel):
    name: str
    description: str


class DatasetCreate(DatasetBase):
    pass


class Dataset(DatasetBase):
    id: int
    owner_id: int
    file_path: Optional[str]
    file_size: Optional[int]
    row_count: Optional[int]
    columns_info: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# Model schemas
class ModelBase(BaseModel):
    name: str
    description: str
    model_type: str


class ModelCreate(ModelBase):
    dataset_id: int
    hyperparameters: Optional[Dict[str, Any]] = {}


class Model(ModelBase):
    id: int
    owner_id: int
    dataset_id: int
    hyperparameters: Dict[str, Any]
    metrics: Optional[Dict[str, Any]]
    status: str
    file_path: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    trained_at: Optional[datetime]

    class Config:
        orm_mode = True


# Prediction schemas
class PredictionBase(BaseModel):
    input_data: List[float]
    prediction_result: List[float]
    confidence_score: Optional[float]


class Prediction(PredictionBase):
    id: int
    user_id: int
    model_id: int
    execution_time_ms: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


# Feature importance schema
class FeatureImportance(BaseModel):
    feature_name: str
    importance: float


# Model metrics schema
class ModelMetrics(BaseModel):
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    mse: Optional[float]
    mae: Optional[float]
    rmse: Optional[float]
    r2_score: Optional[float]
    feature_importance: Optional[List[FeatureImportance]]


# API Key schemas
class ApiKeyBase(BaseModel):
    name: str
    expires_days: int = 30


class ApiKeyCreate(ApiKeyBase):
    user_id: int


class ApiKey(ApiKeyBase):
    id: int
    user_id: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    last_used: Optional[datetime]

    class Config:
        orm_mode = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


# System monitoring schemas
class SystemHealth(BaseModel):
    status: str
    timestamp: str
    database_status: str
    api_status: str
    disk_usage: Dict[str, Any]
    memory_usage: Dict[str, Any]
    cpu_usage: float


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_datasets: int
    total_models: int
    trained_models: int
    total_predictions: int
    predictions_last_24h: int


# Audit log schemas
class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]


class AuditLog(AuditLogBase):
    id: int
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# Error response schemas
class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: str


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]
    status_code: int
    timestamp: str


# Batch operation schemas
class BatchPredictionRequest(BaseModel):
    model_id: int
    input_data_list: List[List[float]]


class BatchPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    total_predictions: int
    successful_predictions: int
    failed_predictions: int


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_size: int
    upload_timestamp: str
    file_path: str


# Pagination schemas
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool


# Search and filter schemas
class SearchParams(BaseModel):
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"


# Configuration schemas
class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class APIConfig(BaseModel):
    title: str = "Quantis API"
    description: str = "API for Quantis time series forecasting platform"
    version: str = "2.0.0"
    debug: bool = False


# Response wrapper schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: str


class ErrorResponseWrapper(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str

