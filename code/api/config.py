"""
Configuration management for the Quantis API
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "Quantis API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./quantis.db"
    database_echo: bool = False
    
    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    jwt_secret: str = "your-jwt-secret-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    api_secret: Optional[str] = None
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = False
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_prediction_requests_per_minute: int = 30
    rate_limit_public_requests_per_minute: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # File upload settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".csv", ".json", ".xlsx", ".xls"]
    upload_directory: str = "./uploads"
    
    # Model settings
    model_directory: str = "./models"
    max_models_per_user: int = 10
    model_training_timeout: int = 3600  # 1 hour
    
    # Prediction settings
    max_batch_size: int = 1000
    prediction_timeout: int = 30  # 30 seconds
    
    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_endpoint: str = "/metrics"
    health_check_endpoint: str = "/health"
    
    # External services
    redis_url: Optional[str] = None
    celery_broker_url: Optional[str] = None
    
    # Email settings (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
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


class DatabaseSettings(BaseSettings):
    """Database-specific settings"""
    
    # PostgreSQL settings
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_db: Optional[str] = None
    
    # MySQL settings
    mysql_user: Optional[str] = None
    mysql_password: Optional[str] = None
    mysql_host: Optional[str] = None
    mysql_port: int = 3306
    mysql_db: Optional[str] = None
    
    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    class Config:
        env_file = ".env"
        env_prefix = "DB_"
    
    def get_database_url(self, db_type: str = "sqlite") -> str:
        """Get database URL based on type"""
        if db_type == "postgresql" and all([
            self.postgres_user, self.postgres_password, 
            self.postgres_host, self.postgres_db
        ]):
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        elif db_type == "mysql" and all([
            self.mysql_user, self.mysql_password,
            self.mysql_host, self.mysql_db
        ]):
            return (
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            )
        else:
            # Default to SQLite
            return "sqlite:///./quantis.db"


# Global settings instance
settings = Settings()
db_settings = DatabaseSettings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_db_settings() -> DatabaseSettings:
    """Get database settings"""
    return db_settings


def update_settings(**kwargs):
    """Update settings at runtime"""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def load_environment_config():
    """Load configuration based on environment"""
    env = settings.environment
    
    if env == "production":
        # Production-specific settings
        settings.debug = False
        settings.reload = False
        settings.cors_credentials = True
        settings.log_level = "WARNING"
        
        # Ensure security settings are set
        if settings.secret_key == "your-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be set in production")
        if settings.jwt_secret == "your-jwt-secret-change-this-in-production":
            raise ValueError("JWT_SECRET must be set in production")
    
    elif env == "staging":
        # Staging-specific settings
        settings.debug = False
        settings.reload = False
        settings.cors_credentials = True
        settings.log_level = "INFO"
    
    elif env == "development":
        # Development-specific settings
        settings.debug = True
        settings.reload = True
        settings.cors_credentials = False
        settings.log_level = "DEBUG"
    
    elif env == "testing":
        # Testing-specific settings
        settings.debug = True
        settings.database_url = "sqlite:///:memory:"
        settings.log_level = "ERROR"


# Load environment-specific configuration
load_environment_config()

