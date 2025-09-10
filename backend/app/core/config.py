from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS_ORIGINS environment variable will be parsed into a list for ALLOWED_HOSTS
    CORS_ORIGINS: str = "http://localhost:3000, https://zidisha-frontend.onrender.com, https://oops-frontend-fix.vercel.app, https://oops-frontend-fix.vercel.app/"
    
    DEBUG: bool = False

    # AI Service settings
    OPENAI_API_KEY: Optional[str] = None # Set this in your environment variables

    # SMS Service settings (Africa's Talking)
    AFRICAS_TALKING_API_KEY: Optional[str] = None # Set this in your environment variables
    AFRICAS_TALKING_USERNAME: Optional[str] = None # Set this in your environment variables
    SMS_SENDER_ID: str = "LOYALTY" # Your registered SMS sender ID

    # Daraja API settings
    DARAJA_API_URL: str = "https://sandbox.safaricom.co.ke" # Default to Daraja sandbox URL
    DARAJA_API_KEY: Optional[str] = None # Set this in your environment variables

    # Environment setting (e.g., development, production)
    ENVIRONMENT: str = "development"

    # AI Service
    OPENAI_API_KEY: Optional[str] = None

    # SMS Service (Africa's Talking)
    AFRICAS_TALKING_API_KEY: Optional[str] = None
    AFRICAS_TALKING_USERNAME: Optional[str] = None
    SMS_SENDER_ID: str = "LOYALTY"

    # Daraja API (M-Pesa)
    DARAJA_API_URL: str = "https://sandbox.safaricom.co.ke" # Default to sandbox
    DARAAA_API_KEY: Optional[str] = None # Used for the mock Daraja service

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parses the comma-separated CORS_ORIGINS string into a list of allowed hosts."""
        return [host.strip() for host in self.CORS_ORIGINS.split(',') if host.strip()]

settings = Settings()