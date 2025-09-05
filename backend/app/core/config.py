from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@db:5432/zidisha_db"
    REDIS_URL: str = "redis://redis:6379"

    # Security settings
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_ME" # IMPORTANT: Generate a strong, random key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    CORS_ORIGINS: str = "" # Comma-separated list of allowed origins (e.g., "http://localhost:3000,https://your-frontend.com")

    # Debugging
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
    
    # Port for the application to listen on
    PORT: int = 8000 # Default to 8000, can be overridden by env var

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parses the comma-separated CORS_ORIGINS string into a list."""
        return [host.strip() for host in self.CORS_ORIGINS.split(",") if host.strip()]

settings = Settings()