"""
M-Pesa Service Protocols

Protocol definitions for dependency injection and testing.
"""

from typing import Protocol, Dict, Any, Optional
from abc import abstractmethod
import httpx


class TokenProvider(Protocol):
    """Protocol for OAuth token providers"""
    
    @abstractmethod
    async def get_token(self) -> str:
        """Get a valid OAuth access token"""
        ...
    
    @abstractmethod
    async def refresh_token(self) -> str:
        """Force refresh and get new token"""
        ...
    
    @abstractmethod
    async def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        ...


class HTTPClient(Protocol):
    """Protocol for HTTP client implementations"""
    
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Make HTTP request"""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close HTTP client and cleanup resources"""
        ...


class CacheProvider(Protocol):
    """Protocol for caching implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        ...
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        ...
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        ...
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        ...


class DatabaseSession(Protocol):
    """Protocol for database session implementations"""
    
    @abstractmethod
    async def execute(self, statement: Any) -> Any:
        """Execute database statement"""
        ...
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction"""
        ...
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction"""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close session"""
        ...


class LoggerProtocol(Protocol):
    """Protocol for logger implementations"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        ...
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        ...
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        ...
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        ...


class MetricsCollector(Protocol):
    """Protocol for metrics collection"""
    
    @abstractmethod
    async def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment counter metric"""
        ...
    
    @abstractmethod
    async def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record histogram metric"""
        ...
    
    @abstractmethod
    async def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record gauge metric"""
        ...


class EventPublisher(Protocol):
    """Protocol for event publishing"""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish event"""
        ...


# Type aliases for common protocol combinations
MpesaDependencies = Dict[str, Any]  # Flexible dependency container
