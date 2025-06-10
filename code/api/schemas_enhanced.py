"""
Enhanced Pydantic schemas for Quantis API with comprehensive validation
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, EmailStr, UUID4
from pydantic.types import constr, confloat, conint

from .models_enhanced import UserRole, ModelStatus, ModelType, DatasetStatus, NotificationType


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UUIDMixin(BaseModel):
    """Mixin for UUID fields"""
    uuid: Optional[UUID4] = None


# User schemas
class UserBase(BaseSchema):
    """Base user schema"""
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$') = Field(
        ..., description="Username (3-50 characters, alphanumeric and underscore only)"
    )
    email: EmailStr = Field(..., description="Valid email address")
    first_name: Optional[constr(max_length=50)] = Field(None, description="First name")
    last_name: Optional[constr(max_length=50)] = Field(None, description="Last name")
    phone_number: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = Field(None, description="Phone number")
    timezone: Optional[str] = Field("UTC", description="User timezone")
    role: Optional[UserRole] = Field(UserRole.USER, description="User role")


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: constr(min_length=8, max_length=128) = Field(
        ..., description="Password (minimum 8 characters)"
    )
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    first_name: Optional[constr(max_length=50)] = None
    last_name: Optional[constr(max_length=50)] = None
    phone_number: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase, TimestampMixin, UUIDMixin):
    """Schema for user response"""
    id: int
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    full_name: Optional[str] = None
    
    @validator('full_name', always=True)
    def compute_full_name(cls, v, values):
        if values.get('first_name') and values.get('last_name'):
            return f"{values['first_name']} {values['last_name']}"
        return values.get('username')


class UserLogin(BaseSchema):
    """Schema for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login session")


class PasswordChange(BaseSchema):
    """Schema for password change"""
    current_password: str = Field(..., description="Current password")
    new_password: constr(min_length=8, max_length=128) = Field(
        ..., description="New password (minimum 8 characters)"
    )
    confirm_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Authentication schemas
class Token(BaseSchema):
    """Schema for authentication token"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefresh(BaseSchema):
    """Schema for token refresh"""
    refresh_token: str = Field(..., description="Refresh token")


# API Key schemas
class ApiKeyBase(BaseSchema):
    """Base API key schema"""
    name: constr(min_length=1, max_length=100) = Field(..., description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    rate_limit: Optional[conint(ge=1, le=10000)] = Field(1000, description="Rate limit per hour")
    scopes: Optional[List[str]] = Field([], description="API key scopes")


class ApiKeyCreate(ApiKeyBase):
    """Schema for creating an API key"""
    pass


class ApiKeyResponse(ApiKeyBase, TimestampMixin):
    """Schema for API key response"""
    id: int
    key_preview: str = Field(..., description="First 8 characters of the key")
    is_active: bool
    last_used: Optional[datetime] = None
    usage_count: int


class ApiKeyWithSecret(ApiKeyResponse):
    """Schema for API key response with secret (only shown once)"""
    key: str = Field(..., description="Full API key (shown only once)")


# Dataset schemas
class DatasetBase(BaseSchema):
    """Base dataset schema"""
    name: constr(min_length=1, max_length=100) = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    tags: Optional[List[str]] = Field([], description="Dataset tags")
    source: Optional[str] = Field(None, description="Data source")
    frequency: Optional[str] = Field(None, description="Data frequency")


class DatasetCreate(DatasetBase):
    """Schema for creating a dataset"""
    pass


class DatasetUpdate(BaseSchema):
    """Schema for updating a dataset"""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    frequency: Optional[str] = None


class DatasetResponse(DatasetBase, TimestampMixin, UUIDMixin):
    """Schema for dataset response"""
    id: int
    owner_id: int
    file_size: Optional[int] = None
    row_count: Optional[int] = None
    columns_info: Optional[Dict[str, Any]] = None
    status: DatasetStatus
    is_active: bool
    quality_score: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DatasetUpload(BaseSchema):
    """Schema for dataset upload"""
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    tags: Optional[List[str]] = Field([], description="Dataset tags")
    source: Optional[str] = Field(None, description="Data source")
    frequency: Optional[str] = Field(None, description="Data frequency")


# Model schemas
class ModelBase(BaseSchema):
    """Base model schema"""
    name: constr(min_length=1, max_length=100) = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    model_type: ModelType = Field(..., description="Model type")
    version: Optional[str] = Field("1.0.0", description="Model version")
    tags: Optional[List[str]] = Field([], description="Model tags")
    notes: Optional[str] = Field(None, description="Model notes")


class ModelCreate(ModelBase):
    """Schema for creating a model"""
    dataset_id: int = Field(..., description="Dataset ID")
    hyperparameters: Optional[Dict[str, Any]] = Field({}, description="Model hyperparameters")
    feature_columns: Optional[List[str]] = Field([], description="Feature columns")
    target_column: Optional[str] = Field(None, description="Target column")
    training_config: Optional[Dict[str, Any]] = Field({}, description="Training configuration")


class ModelUpdate(BaseSchema):
    """Schema for updating a model"""
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    training_config: Optional[Dict[str, Any]] = None


class ModelResponse(ModelBase, TimestampMixin, UUIDMixin):
    """Schema for model response"""
    id: int
    owner_id: int
    dataset_id: int
    parent_model_id: Optional[int] = None
    file_size: Optional[int] = None
    hyperparameters: Dict[str, Any]
    feature_columns: List[str]
    target_column: Optional[str] = None
    training_config: Dict[str, Any]
    training_duration_seconds: Optional[int] = None
    training_samples: Optional[int] = None
    validation_samples: Optional[int] = None
    test_samples: Optional[int] = None
    metrics: Dict[str, Any]
    validation_score: Optional[float] = None
    test_score: Optional[float] = None
    status: ModelStatus
    is_active: bool
    is_deployed: bool
    deployment_url: Optional[str] = None
    trained_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None


class ModelTraining(BaseSchema):
    """Schema for model training request"""
    hyperparameters: Optional[Dict[str, Any]] = Field({}, description="Training hyperparameters")
    training_config: Optional[Dict[str, Any]] = Field({}, description="Training configuration")
    test_size: Optional[confloat(gt=0, lt=1)] = Field(0.2, description="Test set size")
    validation_size: Optional[confloat(gt=0, lt=1)] = Field(0.1, description="Validation set size")
    random_state: Optional[int] = Field(42, description="Random state for reproducibility")


# Prediction schemas
class PredictionBase(BaseSchema):
    """Base prediction schema"""
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    tags: Optional[List[str]] = Field([], description="Prediction tags")
    notes: Optional[str] = Field(None, description="Prediction notes")


class PredictionCreate(PredictionBase):
    """Schema for creating a prediction"""
    model_id: int = Field(..., description="Model ID")


class PredictionBatch(BaseSchema):
    """Schema for batch predictions"""
    model_id: int = Field(..., description="Model ID")
    input_data: List[Dict[str, Any]] = Field(..., description="List of input data for predictions")
    tags: Optional[List[str]] = Field([], description="Prediction tags")


class PredictionResponse(PredictionBase, TimestampMixin, UUIDMixin):
    """Schema for prediction response"""
    id: int
    user_id: int
    model_id: int
    prediction_result: Dict[str, Any]
    confidence_score: Optional[float] = None
    prediction_interval: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    execution_time_ms: Optional[int] = None
    model_version: Optional[str] = None
    api_version: Optional[str] = None
    actual_value: Optional[float] = None
    feedback_score: Optional[float] = None
    is_validated: bool


class PredictionFeedback(BaseSchema):
    """Schema for prediction feedback"""
    actual_value: Optional[float] = Field(None, description="Actual value for validation")
    feedback_score: Optional[confloat(ge=1, le=5)] = Field(None, description="Feedback score (1-5)")
    notes: Optional[str] = Field(None, description="Feedback notes")


# Notification schemas
class NotificationBase(BaseSchema):
    """Base notification schema"""
    title: constr(min_length=1, max_length=200) = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(..., description="Notification type")
    priority: Optional[str] = Field("normal", description="Notification priority")
    category: Optional[str] = Field(None, description="Notification category")
    data: Optional[Dict[str, Any]] = Field({}, description="Additional notification data")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    user_id: int = Field(..., description="User ID")


class NotificationResponse(NotificationBase, TimestampMixin):
    """Schema for notification response"""
    id: int
    user_id: int
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    delivery_status: Optional[str] = None
    delivery_error: Optional[str] = None
    retry_count: int


# Data Quality schemas
class DataQualityReportResponse(BaseSchema, TimestampMixin):
    """Schema for data quality report response"""
    id: int
    dataset_id: int
    completeness_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    consistency_score: Optional[float] = None
    validity_score: Optional[float] = None
    overall_score: Optional[float] = None
    column_analysis: Dict[str, Any]
    outliers_analysis: Dict[str, Any]
    duplicates_analysis: Dict[str, Any]
    missing_values_analysis: Dict[str, Any]
    recommendations: List[str]
    issues_found: List[str]


# Market Data schemas
class MarketDataBase(BaseSchema):
    """Base market data schema"""
    symbol: constr(min_length=1, max_length=20) = Field(..., description="Stock symbol")
    exchange: Optional[str] = Field(None, description="Exchange")
    open_price: Optional[float] = Field(None, description="Opening price")
    high_price: Optional[float] = Field(None, description="High price")
    low_price: Optional[float] = Field(None, description="Low price")
    close_price: Optional[float] = Field(None, description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    adjusted_close: Optional[float] = Field(None, description="Adjusted closing price")
    dividend_amount: Optional[float] = Field(None, description="Dividend amount")
    split_coefficient: Optional[float] = Field(None, description="Split coefficient")
    data_date: datetime = Field(..., description="Data date")
    source: str = Field(..., description="Data source")


class MarketDataCreate(MarketDataBase):
    """Schema for creating market data"""
    pass


class MarketDataResponse(MarketDataBase, TimestampMixin):
    """Schema for market data response"""
    id: int
    source_id: Optional[str] = None
    is_validated: bool
    quality_score: Optional[float] = None


# System schemas
class HealthCheck(BaseSchema):
    """Schema for health check response"""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    database: bool = Field(..., description="Database status")
    redis: bool = Field(..., description="Redis status")
    external_apis: Dict[str, bool] = Field({}, description="External API status")
    version: str = Field(..., description="API version")
    uptime_seconds: int = Field(..., description="System uptime in seconds")


class SystemMetricsResponse(BaseSchema):
    """Schema for system metrics response"""
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    active_connections: int = Field(..., description="Active database connections")
    request_count: int = Field(..., description="Total request count")
    error_rate: float = Field(..., description="Error rate percentage")
    average_response_time: float = Field(..., description="Average response time in ms")


# Pagination schemas
class PaginationParams(BaseSchema):
    """Schema for pagination parameters"""
    page: conint(ge=1) = Field(1, description="Page number (starts from 1)")
    size: conint(ge=1, le=100) = Field(20, description="Page size (max 100)")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("asc", description="Sort order (asc/desc)")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class PaginatedResponse(BaseSchema):
    """Schema for paginated response"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


# Error schemas
class ErrorDetail(BaseSchema):
    """Schema for error detail"""
    field: Optional[str] = Field(None, description="Field name (for validation errors)")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseSchema):
    """Schema for error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


# File upload schemas
class FileUploadResponse(BaseSchema):
    """Schema for file upload response"""
    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    file_hash: str = Field(..., description="File hash for integrity")
    upload_id: str = Field(..., description="Upload ID for tracking")
    status: str = Field(..., description="Upload status")


# Bulk operation schemas
class BulkOperationResponse(BaseSchema):
    """Schema for bulk operation response"""
    total: int = Field(..., description="Total number of items")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[ErrorDetail] = Field([], description="List of errors")
    operation_id: str = Field(..., description="Operation ID for tracking")

