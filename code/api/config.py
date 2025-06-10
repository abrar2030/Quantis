"""
Enhanced configuration management for Quantis API
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class DatabaseSettings(PydanticBaseSettings):
    """Database configuration settings"""
    url: str = "sqlite:///./quantis.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(PydanticBaseSettings):
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    class Config:
        env_prefix = "REDIS_"
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class SecuritySettings(PydanticBaseSettings):
    """Security configuration settings"""
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    class Config:
        env_prefix = "SECURITY_"


class CelerySettings(PydanticBaseSettings):
    """Celery configuration settings"""
    broker_url: str = "redis://localhost:6379/1"
    result_backend: str = "redis://localhost:6379/1"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: List[str] = ["json"]
    timezone: str = "UTC"
    enable_utc: bool = True
    
    # Task routing
    task_routes: dict = {
        "quantis.tasks.ml.*": {"queue": "ml_queue"},
        "quantis.tasks.data.*": {"queue": "data_queue"},
        "quantis.tasks.notifications.*": {"queue": "notifications_queue"},
    }
    
    class Config:
        env_prefix = "CELERY_"


class MonitoringSettings(PydanticBaseSettings):
    """Monitoring and observability settings"""
    enable_metrics: bool = True
    metrics_port: int = 8001
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Sentry configuration
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1
    
    # Health check settings
    health_check_interval: int = 30
    health_check_timeout: int = 5
    
    class Config:
        env_prefix = "MONITORING_"


class EmailSettings(PydanticBaseSettings):
    """Email configuration settings"""
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_tls: bool = True
    smtp_ssl: bool = False
    from_email: str = "noreply@quantis.com"
    from_name: str = "Quantis Platform"
    
    class Config:
        env_prefix = "EMAIL_"


class StorageSettings(PydanticBaseSettings):
    """File storage configuration settings"""
    storage_type: str = "local"  # local, s3, minio
    local_storage_path: str = "./storage"
    
    # S3/MinIO settings
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    
    # File upload limits
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_types: List[str] = [".csv", ".json", ".parquet", ".xlsx"]
    
    class Config:
        env_prefix = "STORAGE_"


class ExternalAPISettings(PydanticBaseSettings):
    """External API configuration settings"""
    alpha_vantage_api_key: Optional[str] = None
    yahoo_finance_enabled: bool = True
    bloomberg_api_key: Optional[str] = None
    
    # API rate limits
    alpha_vantage_requests_per_minute: int = 5
    yahoo_finance_requests_per_minute: int = 2000
    
    class Config:
        env_prefix = "EXTERNAL_API_"


class MLSettings(PydanticBaseSettings):
    """Machine Learning configuration settings"""
    model_storage_path: str = "./models"
    max_training_time_minutes: int = 60
    default_test_size: float = 0.2
    default_validation_size: float = 0.1
    
    # MLflow settings
    mlflow_tracking_uri: str = "sqlite:///./mlflow.db"
    mlflow_experiment_name: str = "quantis_experiments"
    
    # Model serving
    model_cache_size: int = 10
    prediction_timeout_seconds: int = 30
    
    class Config:
        env_prefix = "ML_"


class Settings(PydanticBaseSettings):
    """Main application settings"""
    app_name: str = "Quantis API"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Feature flags
    enable_websockets: bool = True
    enable_background_tasks: bool = True
    enable_real_time_data: bool = True
    enable_ml_training: bool = True
    
    # Nested settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    celery: CelerySettings = CelerySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    email: EmailSettings = EmailSettings()
    storage: StorageSettings = StorageSettings()
    external_api: ExternalAPISettings = ExternalAPISettings()
    ml: MLSettings = MLSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed_environments = ["development", "testing", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v
    
    @validator("debug")
    def validate_debug_in_production(cls, v, values):
        if values.get("environment") == "production" and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def reload_settings():
    """Reload settings from environment"""
    global settings
    settings = Settings()
    return settings

