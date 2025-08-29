from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Zidisha Loyalty Platform"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/zidisha_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Daraaa API settings
    DARAAA_API_URL: str = "https://api.daraaa.com"
    DARAAA_API_KEY: Optional[str] = None
    
    SMS_PROVIDER: str = "africastalking"  # or "twilio"
    SMS_API_KEY: Optional[str] = None
    SMS_USERNAME: Optional[str] = None
    AFRICAS_TALKING_API_KEY: Optional[str] = None
    AFRICAS_TALKING_USERNAME: Optional[str] = None
    SMS_SENDER_ID: Optional[str] = "LOYALTY"
    
    # AI/ML settings
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
