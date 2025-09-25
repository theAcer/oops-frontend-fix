"""
Unified M-Pesa Service Package

This package provides a consolidated, scalable M-Pesa integration following best practices:
- Atomic business logic
- Dependency injection
- Comprehensive error handling
- Easy testing and mocking
"""

from .config import MpesaConfig, MpesaEnvironment
from .exceptions import (
    MpesaAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError
)
from .protocols import TokenProvider, HTTPClient
from .base import BaseMpesaService
from .channel import MpesaChannelService
from .transaction import MpesaTransactionService
from .factory import MpesaServiceFactory

# Legacy compatibility imports
from .legacy import LegacyMpesaService, LegacyDarajaService

__all__ = [
    # Core components
    "MpesaConfig",
    "MpesaEnvironment", 
    "MpesaServiceFactory",
    
    # Services
    "BaseMpesaService",
    "MpesaChannelService", 
    "MpesaTransactionService",
    
    # Protocols
    "TokenProvider",
    "HTTPClient",
    
    # Exceptions
    "MpesaAPIError",
    "AuthenticationError",
    "ValidationError", 
    "RateLimitError",
    "NetworkError",
    
    # Legacy compatibility
    "LegacyMpesaService",
    "LegacyDarajaService"
]
