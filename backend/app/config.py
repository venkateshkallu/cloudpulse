"""
Configuration management for CloudPulse Monitor
Handles environment variables and application settings with development/production modes
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from enum import Enum


class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation"""
    
    # Environment Configuration
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "cloudpulse"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "CloudPulse Monitor API"
    API_VERSION: str = "1.0.0"
    DOCS_ENABLED: bool = True
    REDOC_ENABLED: bool = True
    
    # Security Configuration
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALLOWED_HOSTS: Union[str, List[str]] = Field(default=["localhost", "127.0.0.1", "cloudpulse-monitor"])
    
    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field(default=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://frontend:5173"
    ])
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: Optional[str] = None
    LOG_MAX_SIZE: str = "10MB"
    LOG_BACKUP_COUNT: int = 5
    
    # Background Tasks Configuration
    METRICS_UPDATE_INTERVAL: int = 5
    ENABLE_BACKGROUND_TASKS: bool = True
    
    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT: int = 5
    DATABASE_HEALTH_CHECK_TIMEOUT: int = 3
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        """Validate and normalize environment value"""
        if isinstance(v, str):
            return v.lower()
        return v
    
    @validator("DEBUG", pre=True)
    def validate_debug(cls, v):
        """Convert string boolean to actual boolean"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split comma-separated string and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def validate_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            # Split comma-separated string and strip whitespace
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.ENVIRONMENT == Environment.TESTING
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration based on environment"""
        if self.is_production:
            # More restrictive CORS in production
            return {
                "allow_origins": self.CORS_ORIGINS,
                "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
                "allow_methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            }
        else:
            # More permissive CORS in development
            return {
                "allow_origins": self.CORS_ORIGINS,
                "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }
    
    def get_docs_config(self) -> dict:
        """Get API documentation configuration based on environment"""
        if self.is_production:
            # Disable docs in production for security
            return {
                "docs_url": None,
                "redoc_url": None,
                "openapi_url": None
            }
        else:
            # Enable docs in development
            return {
                "docs_url": "/docs" if self.DOCS_ENABLED else None,
                "redoc_url": "/redoc" if self.REDOC_ENABLED else None,
                "openapi_url": "/openapi.json"
            }
    
    def get_logging_config(self) -> dict:
        """Get logging configuration based on environment"""
        base_config = {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT
        }
        
        if self.is_production and self.LOG_FILE_PATH:
            base_config.update({
                "file_path": self.LOG_FILE_PATH,
                "max_size": self.LOG_MAX_SIZE,
                "backup_count": self.LOG_BACKUP_COUNT
            })
        
        return base_config
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields for forward compatibility
        extra = "ignore"


# Create settings instance with environment-specific defaults
def create_settings() -> Settings:
    """Create settings instance with environment-specific configuration"""
    # Load base settings
    settings = Settings()
    
    # Apply environment-specific overrides
    if settings.is_production:
        # Production-specific settings
        settings.DEBUG = False
        settings.LOG_LEVEL = "WARNING"
        settings.DOCS_ENABLED = False
        settings.REDOC_ENABLED = False
        
        # Validate required production settings
        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production environment")
    
    elif settings.is_testing:
        # Testing-specific settings
        settings.DEBUG = True
        settings.LOG_LEVEL = "DEBUG"
        settings.DATABASE_NAME = "cloudpulse_test"
        settings.ENABLE_BACKGROUND_TASKS = False
    
    return settings


# Global settings instance
settings = create_settings()