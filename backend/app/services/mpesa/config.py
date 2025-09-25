"""
M-Pesa Configuration Management

Centralized configuration for all M-Pesa services with environment-specific settings.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import os


class MpesaEnvironment(str, Enum):
    """M-Pesa API environments"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


@dataclass(frozen=True)
class MpesaConfig:
    """
    Immutable configuration for M-Pesa services.
    
    This configuration class follows best practices:
    - Immutable (frozen=True) for thread safety
    - Environment-specific defaults
    - Validation on creation
    - Easy to test and mock
    """
    
    # Required credentials
    consumer_key: str
    consumer_secret: str
    
    # Environment settings
    environment: MpesaEnvironment = MpesaEnvironment.SANDBOX
    
    # API settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0
    
    # Token management
    token_cache_ttl: int = 3500  # Safaricom tokens expire in 3600s
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    enable_request_logging: bool = True
    enable_response_logging: bool = False  # Be careful with sensitive data
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("consumer_key and consumer_secret are required")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        if self.token_cache_ttl <= 0:
            raise ValueError("token_cache_ttl must be positive")
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the configured environment"""
        urls = {
            MpesaEnvironment.SANDBOX: "https://sandbox.safaricom.co.ke",
            MpesaEnvironment.PRODUCTION: "https://api.safaricom.co.ke"
        }
        return urls[self.environment]
    
    @property
    def oauth_url(self) -> str:
        """Get the OAuth token URL"""
        return f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
    
    @classmethod
    def from_env(cls, prefix: str = "MPESA_") -> "MpesaConfig":
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix (default: "MPESA_")
            
        Returns:
            MpesaConfig instance
            
        Environment variables:
            MPESA_CONSUMER_KEY: Required
            MPESA_CONSUMER_SECRET: Required  
            MPESA_ENVIRONMENT: sandbox|production (default: sandbox)
            MPESA_TIMEOUT: Request timeout in seconds (default: 30)
            MPESA_MAX_RETRIES: Maximum retry attempts (default: 3)
        """
        return cls(
            consumer_key=os.environ[f"{prefix}CONSUMER_KEY"],
            consumer_secret=os.environ[f"{prefix}CONSUMER_SECRET"],
            environment=MpesaEnvironment(
                os.environ.get(f"{prefix}ENVIRONMENT", "sandbox")
            ),
            timeout=int(os.environ.get(f"{prefix}TIMEOUT", "30")),
            max_retries=int(os.environ.get(f"{prefix}MAX_RETRIES", "3")),
            retry_delay=float(os.environ.get(f"{prefix}RETRY_DELAY", "1.0")),
            token_cache_ttl=int(os.environ.get(f"{prefix}TOKEN_CACHE_TTL", "3500")),
        )
    
    @classmethod
    def for_testing(cls) -> "MpesaConfig":
        """Create a configuration suitable for testing"""
        return cls(
            consumer_key="test_consumer_key",
            consumer_secret="test_consumer_secret",
            environment=MpesaEnvironment.SANDBOX,
            timeout=5,  # Shorter timeout for tests
            max_retries=1,  # Fewer retries for faster tests
            retry_delay=0.1,  # Faster retries
            token_cache_ttl=60,  # Shorter cache for tests
            enable_request_logging=False,  # Reduce test noise
        )
