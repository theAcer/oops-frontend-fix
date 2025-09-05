from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "" # Comma-separated list of allowed origins
    DEBUG: bool = False

    OPENAI_API_KEY: Optional[str] = None
    AFRICAS_TALKING_API_KEY: Optional[str] = None
    AFRICAS_TALKING_USERNAME: Optional[str] = None
    SMS_SENDER_ID: str = "LOYALTY"

    DARAAA_API_URL: str = "http://localhost:8001" # Default for local testing
    DARAAA_API_KEY: Optional[str] = None

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        return [host.strip() for host in self.CORS_ORIGINS.split(",") if host.strip()]

settings = Settings()