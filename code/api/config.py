"""
Configuration management for the Quantis API
"""

from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class SecuritySettings(BaseSettings):
    """Security-specific settings"""

    secret_key: str = Field(
        ...,
        env="SECRET_KEY",
        description="Main secret key for the application. MUST be a strong, randomly generated string.",
    )
    jwt_secret: str = Field(
        ...,
        env="JWT_SECRET",
        description="Secret key for JWT signing. MUST be a strong, randomly generated string.",
    )
    algorithm: str = Field("HS256", description="JWT algorithm.")
    access_token_expire_minutes: int = Field(
        30, description="Access token expiration time in minutes."
    )
    refresh_token_expire_days: int = Field(
        7, description="Refresh token expiration time in days."
    )
    api_secret: Optional[str] = Field(
        None,
        env="API_SECRET",
        description="Optional API secret for external service authentication.",
    )
    max_login_attempts: int = Field(
        5, description="Maximum number of failed login attempts before account lockout."
    )
    lockout_duration_minutes: int = Field(
        15,
        description="Duration of account lockout in minutes after too many failed login attempts.",
    )
    max_concurrent_sessions: int = Field(
        5, description="Maximum number of concurrent active sessions per user."
    )

    class Config:
        env_file = ".env"
        env_prefix = "SECURITY_"


class DatabaseSettings(BaseSettings):
    """Database-specific settings"""

    # PostgreSQL settings
    postgres_user: Optional[str] = Field(None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    postgres_host: Optional[str] = Field(None, env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: Optional[str] = Field(None, env="POSTGRES_DB")

    # MySQL settings
    mysql_user: Optional[str] = Field(None, env="MYSQL_USER")
    mysql_password: Optional[str] = Field(None, env="MYSQL_PASSWORD")
    mysql_host: Optional[str] = Field(None, env="MYSQL_HOST")
    mysql_port: int = Field(3306, env="MYSQL_PORT")
    mysql_db: Optional[str] = Field(None, env="MYSQL_DB")

    # Connection pool settings
    pool_size: int = Field(5, description="Database connection pool size.")
    max_overflow: int = Field(
        10, description="Maximum overflow connections in the pool."
    )
    pool_timeout: int = Field(30, description="Connection timeout in seconds.")
    pool_recycle: int = Field(
        3600, description="Recycle connections after this many seconds."
    )

    class Config:
        env_file = ".env"
        env_prefix = "DB_"

    def get_database_url(self, db_type: str = "sqlite") -> str:
        """Get database URL based on type"""
        if db_type == "postgresql" and all(
            [
                self.postgres_user,
                self.postgres_password,
                self.postgres_host,
                self.postgres_db,
            ]
        ):
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        elif db_type == "mysql" and all(
            [self.mysql_user, self.mysql_password, self.mysql_host, self.mysql_db]
        ):
            return (
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            )
        else:
            # Default to SQLite
            return "sqlite:///./quantis.db"


class EncryptionSettings(BaseSettings):
    """Settings for data encryption and key management"""

    data_encryption_key_name: str = Field(
        "default_data_key",
        description="Name of the primary key used for data encryption.",
    )
    key_rotation_interval_days: int = Field(
        365, description="Interval in days for key rotation."
    )
    use_kms: bool = Field(
        False,
        description="Whether to use a Key Management System (KMS) for key storage.",
    )
    kms_endpoint: Optional[str] = Field(
        None, description="KMS endpoint if use_kms is true."
    )
    kms_key_id: Optional[str] = Field(
        None, description="KMS key ID if use_kms is true."
    )

    class Config:
        env_file = ".env"
        env_prefix = "ENCRYPTION_"


class LoggingSettings(BaseSettings):
    """Settings for logging and audit trails"""

    log_level: str = Field(
        "INFO",
        description="Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format string.",
    )
    log_file: Optional[str] = Field(
        None, description="Path to log file. If None, logs to stdout."
    )
    enable_audit_logging: bool = Field(
        True, description="Enable comprehensive audit logging for security events."
    )
    centralized_log_system_enabled: bool = Field(
        False,
        description="Whether to send logs to a centralized log management system.",
    )
    centralized_log_system_endpoint: Optional[str] = Field(
        None, description="Endpoint for centralized log management system."
    )
    secure_log_transmission: bool = Field(
        False,
        description="Whether to use secure protocols (e.g., TLS) for log transmission.",
    )

    class Config:
        env_file = ".env"
        env_prefix = "LOGGING_"


class ComplianceSettings(BaseSettings):
    """Settings for data compliance (GDPR, CCPA, etc.)"""

    enable_data_retention_policies: bool = Field(
        True, description="Enable enforcement of data retention policies."
    )
    default_retention_days: int = Field(
        365 * 7, description="Default data retention period in days (e.g., 7 years)."
    )
    enable_consent_management: bool = Field(
        True, description="Enable consent management for user data processing."
    )
    enable_data_masking: bool = Field(
        True, description="Enable data masking for sensitive data."
    )

    class Config:
        env_file = ".env"
        env_prefix = "COMPLIANCE_"


class Settings(BaseSettings):
    """Main application settings"""

    # Application settings
    app_name: str = "Quantis API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS settings
    cors_origins: List[str] = Field(["*"], description="Allowed CORS origins.")
    cors_credentials: bool = Field(False, description="Allow CORS credentials.")
    cors_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="Allowed CORS methods.",
    )
    cors_headers: List[str] = Field(["*"], description="Allowed CORS headers.")

    # Rate limiting
    rate_limit_requests_per_minute: int = Field(
        60, description="Default rate limit for general requests."
    )
    rate_limit_prediction_requests_per_minute: int = Field(
        30, description="Rate limit for prediction requests."
    )
    rate_limit_public_requests_per_minute: int = Field(
        30, description="Rate limit for public endpoints."
    )

    # File upload settings
    max_upload_size: int = Field(
        10 * 1024 * 1024, description="Maximum file upload size in bytes (e.g., 10MB)."
    )
    allowed_file_types: List[str] = Field(
        [".csv", ".json", ".xlsx", ".xls"],
        description="Allowed file extensions for uploads.",
    )
    upload_directory: str = Field(
        "./uploads", description="Directory for file uploads."
    )

    # Model settings
    model_directory: str = Field(
        "./models", description="Directory for storing ML models."
    )
    max_models_per_user: int = Field(
        10, description="Maximum number of models a user can create."
    )
    model_training_timeout: int = Field(
        3600, description="Timeout for model training in seconds (1 hour)."
    )

    # Prediction settings
    max_batch_size: int = Field(1000, description="Maximum batch size for predictions.")
    prediction_timeout: int = Field(
        30, description="Timeout for single prediction requests in seconds."
    )

    # Monitoring and metrics
    enable_metrics: bool = Field(True, description="Enable metrics exposure.")
    metrics_endpoint: str = Field("/metrics", description="Endpoint for metrics.")
    health_check_endpoint: str = Field(
        "/health", description="Endpoint for health checks."
    )

    # External services
    redis_url: Optional[str] = Field(
        None, env="REDIS_URL", description="Redis connection URL."
    )
    celery_broker_url: Optional[str] = Field(
        None,
        env="CELERY_BROKER_URL",
        description="Celery broker URL for background tasks.",
    )

    # Email settings (for notifications)
    smtp_server: Optional[str] = Field(None, env="SMTP_SERVER")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, env="SMTP_USE_TLS")

    # Nested settings
    security: SecuritySettings = Field(
        default_factory=SecuritySettings
    )  # Nested security settings
    database: DatabaseSettings = Field(
        default_factory=DatabaseSettings
    )  # Nested database settings
    encryption: EncryptionSettings = Field(
        default_factory=EncryptionSettings
    )  # Nested encryption settings
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings
    )  # Nested logging settings
    compliance: ComplianceSettings = Field(
        default_factory=ComplianceSettings
    )  # Nested compliance settings

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Allow nested settings to be loaded from environment variables with their prefixes
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

    @validator("environment")
    def validate_environment(cls, v):
        allowed_envs = ["development", "staging", "production", "testing"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("cors_methods", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip().upper() for method in v.split(",")]
        return v

    @validator("cors_headers", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.security = SecuritySettings()  # Initialize nested settings explicitly
        _settings.database = DatabaseSettings()
        _settings.encryption = EncryptionSettings()
        _settings.logging = LoggingSettings()
        _settings.compliance = ComplianceSettings()
        load_environment_config(_settings)  # Pass the settings object
    return _settings


def update_settings(settings_obj: Settings, **kwargs):
    """Update settings at runtime"""
    for key, value in kwargs.items():
        if hasattr(settings_obj, key):
            setattr(settings_obj, key, value)


def load_environment_config(settings_obj: Settings):
    """Load configuration based on environment"""
    env = settings_obj.environment

    if env == "production":
        # Production-specific settings
        settings_obj.debug = False
        settings_obj.reload = False
        settings_obj.cors_credentials = True
        settings_obj.logging.log_level = "WARNING"

        # Ensure security settings are set
        if (
            settings_obj.security.secret_key
            == "your-secret-key-change-this-in-production"
        ):
            raise ValueError("SECRET_KEY must be set in production")
        if settings_obj.security.jwt_secret == "your-jwt-key-change-this-in-production":
            raise ValueError("JWT_SECRET must be set in production")

    elif env == "staging":
        # Staging-specific settings
        settings_obj.debug = False
        settings_obj.reload = False
        settings_obj.cors_credentials = True
        settings_obj.logging.log_level = "INFO"

    elif env == "development":
        # Development-specific settings
        settings_obj.debug = True
        settings_obj.reload = True
        settings_obj.cors_credentials = False
        settings_obj.logging.log_level = "DEBUG"

    elif env == "testing":
        # Testing-specific settings
        settings_obj.debug = True
        settings_obj.database.database_url = "sqlite:///:memory:"
        settings_obj.logging.log_level = "ERROR"


# Initialize settings on import
get_settings()
