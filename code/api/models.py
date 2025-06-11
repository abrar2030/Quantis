"""
Enhanced database models for Quantis API with comprehensive features
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import secrets
import uuid
from enum import Enum as PyEnum
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON,
    Enum, Index, UniqueConstraint, CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(PyEnum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
    ANALYST = "analyst"
    TRADER = "trader"


class ModelStatus(PyEnum):
    """Model status enumeration"""
    CREATED = "created"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ModelType(PyEnum):
    """Model type enumeration"""
    TFT = "tft"
    LSTM = "lstm"
    ARIMA = "arima"
    PROPHET = "prophet"
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"


class DatasetStatus(PyEnum):
    """Dataset status enumeration"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"


class NotificationType(PyEnum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class AuditMixin:
    """Mixin for audit fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True))
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True))
    
    # Profile information
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSON, default=dict)
    
    # Relationships
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_username_active', 'username', 'is_active'),
    )

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    def is_locked(self) -> bool:
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def lock_account(self, duration_minutes: int = 15):
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.login_attempts = 0
    
    def unlock_account(self):
        self.locked_until = None
        self.login_attempts = 0
    
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class UserSession(Base, AuditMixin):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_sessions")
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class ApiKey(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0, nullable=False)
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests per hour
    scopes = Column(JSON, default=list)  # List of allowed scopes

    # Relationships
    user = relationship("User", back_populates="api_keys")

    @staticmethod
    def generate_key() -> str:
        return f"qk_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    def is_expired(self) -> bool:
        return self.expires_at and datetime.utcnow() > self.expires_at


class Dataset(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(64))  # SHA-256 hash for integrity
    columns_info = Column(JSON)  # Store column names and types
    row_count = Column(Integer)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.UPLOADING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Data quality metrics
    quality_score = Column(Float)
    missing_values_count = Column(Integer)
    duplicate_rows_count = Column(Integer)
    outliers_count = Column(Integer)
    
    # Metadata
    tags = Column(JSON, default=list)
    source = Column(String(100))  # Source of the data
    frequency = Column(String(20))  # Data frequency (daily, hourly, etc.)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Relationships
    owner = relationship("User", back_populates="datasets")
    models = relationship("Model", back_populates="dataset", cascade="all, delete-orphan")
    data_quality_reports = relationship("DataQualityReport", back_populates="dataset")
    
    # Constraints
    __table_args__ = (
        Index('idx_dataset_owner_status', 'owner_id', 'status'),
        Index('idx_dataset_name_owner', 'name', 'owner_id'),
    )


class Model(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    model_type = Column(Enum(ModelType), nullable=False)
    version = Column(String(20), default="1.0.0", nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    parent_model_id = Column(Integer, ForeignKey("models.id"), nullable=True)  # For model versioning
    
    # File storage
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(64))
    
    # Configuration
    hyperparameters = Column(JSON, default=dict)
    feature_columns = Column(JSON, default=list)
    target_column = Column(String(100))
    
    # Training information
    training_config = Column(JSON, default=dict)
    training_duration_seconds = Column(Integer)
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    test_samples = Column(Integer)
    
    # Performance metrics
    metrics = Column(JSON, default=dict)
    validation_score = Column(Float)
    test_score = Column(Float)
    
    # Status and deployment
    status = Column(Enum(ModelStatus), default=ModelStatus.CREATED, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deployed = Column(Boolean, default=False, nullable=False)
    deployment_url = Column(String(500))
    trained_at = Column(DateTime(timezone=True))
    deployed_at = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)

    # Relationships
    owner = relationship("User", back_populates="models")
    dataset = relationship("Dataset", back_populates="models")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")
    model_versions = relationship("Model", remote_side=[id])  # Self-referential for versioning
    experiments = relationship("Experiment", back_populates="model")
    
    # Constraints
    __table_args__ = (
        Index('idx_model_owner_status', 'owner_id', 'status'),
        Index('idx_model_type_status', 'model_type', 'status'),
        UniqueConstraint('name', 'version', 'owner_id', name='uq_model_name_version_owner'),
    )


class Prediction(Base, AuditMixin):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    
    # Input and output data
    input_data = Column(JSON, nullable=False)
    prediction_result = Column(JSON, nullable=False)
    
    # Prediction metadata
    confidence_score = Column(Float)
    prediction_interval = Column(JSON)  # Upper and lower bounds
    feature_importance = Column(JSON)
    
    # Performance tracking
    execution_time_ms = Column(Integer)
    model_version = Column(String(20))
    api_version = Column(String(20))
    
    # Feedback and validation
    actual_value = Column(Float)  # For backtesting
    feedback_score = Column(Float)  # User feedback
    is_validated = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="predictions")
    model = relationship("Model", back_populates="predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_prediction_user_model', 'user_id', 'model_id'),
        Index('idx_prediction_created_at', 'created_at'),
    )


class Experiment(Base, AuditMixin):
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    
    # Experiment configuration
    config = Column(JSON, default=dict)
    parameters = Column(JSON, default=dict)
    
    # Results
    results = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    artifacts = Column(JSON, default=list)  # File paths to artifacts
    
    # Status
    status = Column(String(20), default="created", nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    model = relationship("Model", back_populates="experiments")


class Notification(Base, AuditMixin):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Delivery information
    delivery_status = Column(String(50))
    delivery_error = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    category = Column(String(50))  # model_training, data_processing, system_alert, etc.
    data = Column(JSON, default=dict)  # Additional notification data
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_user_read', 'user_id', 'is_read'),
        Index('idx_notification_type_sent', 'notification_type', 'is_sent'),
    )


class DataQualityReport(Base, AuditMixin):
    __tablename__ = "data_quality_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    
    # Quality metrics
    completeness_score = Column(Float)  # Percentage of non-null values
    accuracy_score = Column(Float)  # Data accuracy assessment
    consistency_score = Column(Float)  # Data consistency assessment
    validity_score = Column(Float)  # Data validity assessment
    overall_score = Column(Float)  # Overall quality score
    
    # Detailed analysis
    column_analysis = Column(JSON, default=dict)  # Per-column quality metrics
    outliers_analysis = Column(JSON, default=dict)  # Outlier detection results
    duplicates_analysis = Column(JSON, default=dict)  # Duplicate detection results
    missing_values_analysis = Column(JSON, default=dict)  # Missing values analysis
    
    # Recommendations
    recommendations = Column(JSON, default=list)  # Data quality improvement recommendations
    issues_found = Column(JSON, default=list)  # List of issues found
    
    # Relationships
    dataset = relationship("Dataset", back_populates="data_quality_reports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255))
    
    # Action information
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50))
    resource_name = Column(String(200))
    
    # Request information
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    
    # Details
    details = Column(JSON, default=dict)
    changes = Column(JSON, default=dict)  # Before/after values for updates
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    request_id = Column(String(100))
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration_ms = Column(Integer)

    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created_at', 'created_at'),
    )


class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    
    # Metadata
    tags = Column(JSON, default=dict)  # Additional metadata
    source = Column(String(50))  # Source of the metric
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_metrics_source_timestamp', 'source', 'timestamp'),
    )


class MarketData(Base, AuditMixin):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20))
    
    # Price data
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    
    # Additional data
    adjusted_close = Column(Float)
    dividend_amount = Column(Float)
    split_coefficient = Column(Float)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False)
    data_date = Column(DateTime(timezone=True), nullable=False)
    
    # Data source
    source = Column(String(50), nullable=False)
    source_id = Column(String(100))
    
    # Quality indicators
    is_validated = Column(Boolean, default=False)
    quality_score = Column(Float)
    
    # Indexes
    __table_args__ = (
        Index('idx_market_data_symbol_date', 'symbol', 'data_date'),
        Index('idx_market_data_timestamp', 'timestamp'),
        UniqueConstraint('symbol', 'data_date', 'source', name='uq_market_data_symbol_date_source'),
    )


# Event listeners for automatic audit logging
@event.listens_for(User, 'after_insert')
@event.listens_for(User, 'after_update')
@event.listens_for(User, 'after_delete')
def log_user_changes(mapper, connection, target):
    """Log user changes to audit log"""
    # This would be implemented to automatically log changes
    pass


@event.listens_for(Model, 'after_update')
def update_model_timestamp(mapper, connection, target):
    """Update model timestamp when status changes"""
    if target.status == ModelStatus.TRAINED and not target.trained_at:
        target.trained_at = datetime.utcnow()
    elif target.status == ModelStatus.DEPLOYED and not target.deployed_at:
        target.deployed_at = datetime.utcnow()

