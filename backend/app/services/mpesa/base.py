"""
Base M-Pesa Service

Foundation class providing common functionality for all M-Pesa services.
"""

import asyncio
import base64
import json
import logging
import time
from typing import Dict, Any, Optional, Union
from uuid import uuid4

import httpx

from .config import MpesaConfig
from .exceptions import (
    MpesaAPIError,
    AuthenticationError,
    NetworkError,
    TimeoutError,
    RateLimitError,
    create_exception_from_response
)
from .protocols import TokenProvider, HTTPClient, CacheProvider, LoggerProtocol


class DefaultHTTPClient:
    """Default HTTP client implementation"""
    
    def __init__(self, config: MpesaConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
        return self._client
    
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
        """Make HTTP request with error handling"""
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                data=data,
                params=params,
                timeout=timeout or self.config.timeout
            )
            return response
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {url}") from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {url}") from e
        except Exception as e:
            raise NetworkError(f"Unexpected error: {url}") from e
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


class InMemoryCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self._cache: Dict[str, tuple[str, float]] = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        expires_at = time.time() + (ttl or 3600)
        self._cache[key] = (value, expires_at)
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.get(key) is not None


class BaseMpesaService:
    """
    Base service providing common M-Pesa functionality.
    
    This class implements:
    - OAuth token management with caching
    - HTTP client with retry logic
    - Request/response logging
    - Error handling and mapping
    - Metrics collection
    """
    
    def __init__(
        self,
        config: MpesaConfig,
        http_client: Optional[HTTPClient] = None,
        cache: Optional[CacheProvider] = None,
        logger: Optional[LoggerProtocol] = None
    ):
        self.config = config
        self.http_client = http_client or DefaultHTTPClient(config)
        self.cache = cache or InMemoryCache()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        # OAuth credentials
        self._auth_header = self._create_auth_header()
        
        # Request tracking
        self._request_id: Optional[str] = None
    
    def _create_auth_header(self) -> str:
        """Create base64 encoded auth header"""
        credentials = f"{self.config.consumer_key}:{self.config.consumer_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    async def get_access_token(self) -> str:
        """
        Get OAuth access token with caching.
        
        Returns:
            Valid access token
            
        Raises:
            AuthenticationError: If token acquisition fails
        """
        cache_key = f"mpesa_token_{hash(self.config.consumer_key)}"
        
        # Try to get cached token
        cached_token = await self.cache.get(cache_key)
        if cached_token:
            self.logger.debug("Using cached access token")
            return cached_token
        
        # Request new token
        self.logger.info("Requesting new access token")
        
        headers = {
            "Authorization": f"Basic {self._auth_header}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.http_client.request(
                method="GET",
                url=self.config.oauth_url,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                if not token:
                    raise AuthenticationError("No access token in response")
                
                # Cache token with TTL
                await self.cache.set(cache_key, token, self.config.token_cache_ttl)
                
                self.logger.info("Successfully obtained access token")
                return token
            else:
                error_data = response.json() if response.content else {}
                raise create_exception_from_response(
                    response.status_code,
                    error_data,
                    "Failed to get access token"
                )
                
        except httpx.HTTPError as e:
            raise NetworkError(f"Failed to get access token: {e}") from e
    
    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make authenticated request to M-Pesa API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base URL)
            json_data: Request JSON data
            params: Query parameters
            retry_count: Current retry attempt
            
        Returns:
            Response JSON data
            
        Raises:
            MpesaAPIError: For API errors
            NetworkError: For network issues
        """
        # Generate request ID for tracking
        self._request_id = str(uuid4())
        
        # Get access token
        try:
            token = await self.get_access_token()
        except AuthenticationError:
            if retry_count < self.config.max_retries:
                # Clear cached token and retry
                cache_key = f"mpesa_token_{hash(self.config.consumer_key)}"
                await self.cache.delete(cache_key)
                return await self.make_authenticated_request(
                    method, endpoint, json_data=json_data, params=params, retry_count=retry_count + 1
                )
            raise
        
        # Prepare request
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Request-ID": self._request_id
        }
        
        # Log request (be careful with sensitive data)
        if self.config.enable_request_logging:
            self.logger.info(
                f"Making {method} request to {endpoint}",
                extra={
                    "request_id": self._request_id,
                    "method": method,
                    "endpoint": endpoint,
                    "has_json": json_data is not None
                }
            )
        
        try:
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            
            # Log response
            if self.config.enable_response_logging:
                self.logger.info(
                    f"Received response: {response.status_code}",
                    extra={
                        "request_id": self._request_id,
                        "status_code": response.status_code,
                        "response_size": len(response.content)
                    }
                )
            
            # Handle response
            if response.status_code in (200, 201):
                return response.json()
            else:
                # Handle error response
                error_data = response.json() if response.content else {}
                
                # Retry on authentication errors
                if response.status_code == 401 and retry_count < self.config.max_retries:
                    self.logger.warning("Authentication failed, retrying with new token")
                    cache_key = f"mpesa_token_{hash(self.config.consumer_key)}"
                    await self.cache.delete(cache_key)
                    await asyncio.sleep(self.config.retry_delay)
                    return await self.make_authenticated_request(
                        method, endpoint, json_data=json_data, params=params, retry_count=retry_count + 1
                    )
                
                # Retry on rate limit
                if response.status_code == 429 and retry_count < self.config.max_retries:
                    retry_after = int(response.headers.get("Retry-After", self.config.retry_delay))
                    self.logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self.make_authenticated_request(
                        method, endpoint, json_data=json_data, params=params, retry_count=retry_count + 1
                    )
                
                # Create appropriate exception
                raise create_exception_from_response(
                    response.status_code,
                    error_data,
                    f"API request failed: {method} {endpoint}"
                )
                
        except httpx.HTTPError as e:
            if retry_count < self.config.max_retries:
                delay = self.config.retry_delay * (self.config.retry_backoff_factor ** retry_count)
                self.logger.warning(f"Network error, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
                return await self.make_authenticated_request(
                    method, endpoint, json_data=json_data, params=params, retry_count=retry_count + 1
                )
            raise NetworkError(f"Network error after {retry_count} retries: {e}") from e
    
    async def close(self) -> None:
        """Close service and cleanup resources"""
        await self.http_client.close()
        self.logger.info("M-Pesa service closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
