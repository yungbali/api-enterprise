"""
Application Configuration Management
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Enterprise Suite API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = []
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_TEST_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_TEST_URL: Optional[str] = None
    
    # AWS
    AWS_REGION: str = "us-west-2"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Authentication
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    API_KEY_NAME: str = "X-API-Key"
    
    # External Services
    MUSICBRAINZ_BASE_URL: str = "https://musicbrainz.org/ws/2"
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Background Tasks
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Webhooks
    WEBHOOK_SECRET: str = "dev-webhook-secret"
    WEBHOOK_TIMEOUT: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
