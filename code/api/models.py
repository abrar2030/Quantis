"""
Enhanced database models for Quantis API with comprehensive features
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from passlib.context import CryptContext
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

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


# Association table for Role-Permission many-to-many relationship
role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class Permission(Base, AuditMixin):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")


class Role(Base, AuditMixin):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")


class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False) # Changed from role to role_id
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_mfa_enabled = Column(Boolean, default=False, nullable=False) # Added for MFA
    mfa_secret = Column(String(255), nullable=True) # Added for MFA
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
    role = relationship("Role", back_populates="users") # Added relationship to Role
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    models = relationship("Model", back_populates="owner", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_username_active", "username", "is_active"),
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
    ip_address = Column(String(45)) # Already exists
    user_agent = Column(String(500)) # Already exists
    last_activity = Column(DateTime(timezone=True), server_default=func.now()) # Already exists

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
    ip_whitelist = Column(JSON, default=list) # Added for API Key IP whitelisting

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
        Index("idx_dataset_owner_status", "owner_id", "status"),
        Index("idx_dataset_name_owner", "name", "owner_id"),
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
        Index("idx_model_owner_status", "owner_id", "status"),
        Index("idx_model_type_status", "model_type", "status"),
        UniqueConstraint("name", "version", "owner_id", name="uq_model_name_version_owner"),
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
        Index("idx_prediction_user_model", "user_id", "model_id"),
        Index("idx_prediction_created_at", "created_at"),
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
        Index("idx_notification_user_read", "user_id", "is_read"),
        Index("idx_notification_type_sent", "notification_type", "is_sent"),
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for system events or unauthenticated actions
    action = Column(String(100), nullable=False) # e.g., "user_login", "model_deploy", "data_access"
    resource_type = Column(String(50)) # e.g., "user", "model", "dataset", "api_key"
    resource_id = Column(String(255)) # ID of the resource affected
    resource_name = Column(String(255)) # Name of the resource affected
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45)) # IPv4 or IPv6
    user_agent = Column(String(500))
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    details = Column(JSON) # Additional details in JSON format

    user = relationship("User")

    __table_args__ = (
        Index("idx_audit_log_user_id", "user_id"),
        Index("idx_audit_log_action", "action"),
        Index("idx_audit_log_timestamp", "timestamp"),
    )


class DataRetentionPolicy(Base, AuditMixin):
    __tablename__ = "data_retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), unique=True, nullable=False) # e.g., \'audit_logs\', \'predictions\'
    retention_period_days = Column(Integer, nullable=False) # 0 for indefinite
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)


class ConsentRecord(Base, AuditMixin):
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(String(100), nullable=False) # e.g., \'data_processing\', \'marketing_emails\'
    given_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    details = Column(JSON) # Additional details about the consent

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint(\'user_id\', \'consent_type\', name=\'uq_user_consent_type\'),
        Index("idx_consent_user_id", "user_id"),
        Index("idx_consent_type", "consent_type"),
    )


class DataMaskingConfig(Base, AuditMixin):
    __tablename__ = "data_masking_configs"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(100), unique=True, nullable=False) # e.g., \'credit_card_number\', \'ssn\'
    masking_method = Column(String(50), nullable=False) # e.g., \'hash\', \'redact\', \'partial\'
    is_active = Column(Boolean, default=True, nullable=False)
    config_details = Column(JSON) # Method-specific configuration details


class EncryptionKey(Base, AuditMixin):
    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), unique=True, nullable=False)
    key_value = Column(String(255), nullable=False) # Store encrypted key or key identifier
    key_type = Column(String(50), nullable=False) # e.g., 'AES', 'RSA', 'Fernet'
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    # For key rotation
    previous_key_id = Column(Integer, ForeignKey("encryption_keys.id"), nullable=True)
    next_key_id = Column(Integer, ForeignKey("encryption_keys.id"), nullable=True)

    previous_key = relationship("EncryptionKey", remote_side=[id], uselist=False, post_update=True)
    next_key = relationship("EncryptionKey", remote_side=[id], uselist=False, post_update=True)


# Event listener for updated_at column
@event.listens_for(Base, \'before_update\', propagate=True)
def receive_before_update(mapper, connection, target):
    if hasattr(target, \'updated_at\'):
        target.updated_at = datetime.utcnow()




class Transaction(Base):
    """Transaction model for financial operations"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    transaction_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    description = Column(Text)
    counterparty_info = Column(JSON)
    risk_level = Column(String(20), default="low")
    risk_score = Column(Integer, default=0)
    compliance_flags = Column(JSON)

    # Approval fields
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])

    # Indexes
    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'created_at'),
        Index('idx_transaction_status_date', 'status', 'created_at'),
        Index('idx_transaction_type_date', 'transaction_type', 'created_at'),
        Index('idx_transaction_amount', 'amount'),
    )


# Add transactions relationship to User model
User.transactions = relationship("Transaction", foreign_keys="Transaction.user_id", back_populates="user")
