"""
M-Pesa/Daraja API Integration Services

Best Practices Applied:
1. Single Responsibility: Separate concerns into focused classes
2. Composition over Inheritance: Use composition for shared functionality
3. Interface Segregation: Clear interfaces for different operations
4. Dependency Injection: Easy to test and configure
5. Configuration Management: Centralized environment configs
6. Error Handling: Consistent patterns with custom exceptions
7. Caching: Token caching for performance
8. Rate Limiting: Built-in retry and rate limit handling
9. Logging: Structured logging throughout
10. Testing: Easy to mock and unit test
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, Protocol, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import logging
import base64
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Custom Exceptions
class MpesaAPIError(Exception):
    """Base exception for M-Pesa API errors"""
    pass

class AuthenticationError(MpesaAPIError):
    """Authentication related errors"""
    pass

class RateLimitError(MpesaAPIError):
    """Rate limiting errors"""
    pass

class ValidationError(MpesaAPIError):
    """Data validation errors"""
    pass

# Configuration
@dataclass
class MpesaConfig:
    """Configuration for M-Pesa API integration"""
    consumer_key: str
    consumer_secret: str
    environment: str = "sandbox"  # sandbox | production
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    token_cache_ttl: int = 3500  # seconds (slightly less than 1 hour)

    @property
    def api_base_url(self) -> str:
        if self.base_url:
            return self.base_url

        urls = {
            "sandbox": "https://sandbox.safaricom.co.ke",
            "production": "https://api.safaricom.co.ke"
        }
        return urls.get(self.environment, urls["sandbox"])

# Interfaces
class TokenProvider(Protocol):
    """Interface for OAuth token providers"""
    async def get_token(self) -> str: ...
    async def refresh_token(self) -> str: ...

class HTTPClient(Protocol):
    """Interface for HTTP clients"""
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response: ...

# Base Service Class
class BaseMpesaService(ABC):
    """Base class with common functionality for all M-Pesa services"""

    def __init__(self, config: MpesaConfig):
        self.config = config
        self._token_cache: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self._http_client

    async def close(self):
        """Cleanup resources"""
        if self._http_client:
            await self._http_client.aclose()

    def _encode_credentials(self) -> str:
        """Encode consumer credentials for Basic Auth"""
        credentials = f"{self.config.consumer_key}:{self.config.consumer_secret}"
        return base64.b64encode(credentials.encode()).decode()

    async def _get_oauth_token(self) -> str:
        """Get OAuth access token with caching"""
        now = datetime.utcnow()

        # Return cached token if still valid
        if (self._token_cache and self._token_expires_at and
            now < self._token_expires_at):
            return self._token_cache

        # Fetch new token
        token = await self._fetch_oauth_token()
        self._token_cache = token
        self._token_expires_at = now + timedelta(seconds=self.config.token_cache_ttl)

        return token

    async def _fetch_oauth_token(self) -> str:
        """Fetch new OAuth token from M-Pesa"""
        url = f"{self.config.api_base_url}/oauth/v1/generate?grant_type=client_credentials"

        headers = {
            "Authorization": f"Basic {self._encode_credentials()}",
            "Content-Type": "application/json"
        }

        for attempt in range(self.config.max_retries):
            try:
                response = await self.http_client.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    return data["access_token"]
                elif response.status_code == 429:
                    # Rate limited
                    if attempt < self.config.max_retries - 1:
                        delay = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded")
                else:
                    raise AuthenticationError(f"OAuth failed: {response.status_code} - {response.text}")

            except httpx.RequestError as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise MpesaAPIError(f"Request failed after {self.config.max_retries} attempts: {e}")

        raise MpesaAPIError("Failed to get OAuth token")

    async def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request to M-Pesa API"""
        token = await self._get_oauth_token()

        url = f"{self.config.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        headers.update(kwargs.get("headers", {}))

        for attempt in range(self.config.max_retries):
            try:
                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **{k: v for k, v in kwargs.items() if k != "headers"}
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    if attempt < self.config.max_retries - 1:
                        delay = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"Rate limited, retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise RateLimitError("Rate limit exceeded")
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                    logger.error(f"API request failed: {response.status_code} - {error_data}")
                    raise MpesaAPIError(f"API request failed: {response.status_code}")

            except httpx.RequestError as e:
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"Request failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise MpesaAPIError(f"Request failed after {self.config.max_retries} attempts: {e}")

        raise MpesaAPIError("Request failed after all retries")

# Specific Service Implementations
class MpesaChannelService(BaseMpesaService):
    """Service for M-Pesa channel operations (Phase 2 & 3)"""

    async def verify_channel(self, shortcode: str) -> Dict[str, Any]:
        """Verify M-Pesa channel credentials"""
        try:
            # Test OAuth token generation
            token = await self._get_oauth_token()

            if not token:
                raise AuthenticationError("Invalid credentials")

            # Test basic API connectivity
            result = await self._make_authenticated_request(
                "GET",
                f"/mpesa/c2b/v1/registerurl?ShortCode={shortcode}&CommandID=RegisterURL"
            )

            return {
                "status": "verified",
                "message": "Channel credentials are valid",
                "timestamp": datetime.utcnow().isoformat()
            }

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Channel verification failed: {e}")
            raise MpesaAPIError(f"Channel verification failed: {e}")

    async def register_urls(
        self,
        shortcode: str,
        response_type: str = "Completed",
        confirmation_url: Optional[str] = None,
        validation_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register validation and confirmation URLs"""
        payload = {
            "ShortCode": shortcode,
            "ResponseType": response_type,
            "CommandID": "RegisterURL"
        }

        if confirmation_url:
            payload["ConfirmationURL"] = confirmation_url
        if validation_url:
            payload["ValidationURL"] = validation_url

        return await self._make_authenticated_request(
            "POST",
            "/mpesa/c2b/v1/registerurl",
            json=payload
        )

    async def simulate_transaction(
        self,
        shortcode: str,
        amount: float,
        msisdn: str,
        bill_ref_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simulate an M-Pesa C2B transaction (sandbox only)"""
        if self.config.environment != "sandbox":
            raise ValidationError("Simulation only available in sandbox environment")

        payload = {
            "ShortCode": shortcode,
            "CommandID": "CustomerPayBillOnline",
            "Amount": amount,
            "Msisdn": msisdn,
            "BillRefNumber": bill_ref_number or "TestPayment"
        }

        return await self._make_authenticated_request(
            "POST",
            "/mpesa/c2b/v1/simulate",
            json=payload
        )

    async def check_transaction_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """Check STK push transaction status"""
        payload = {
            "CheckoutRequestID": checkout_request_id,
            "CommandID": "TransactionStatusQuery"
        }

        return await self._make_authenticated_request(
            "POST",
            "/mpesa/stkpushquery/v1/query",
            json=payload
        )

class MpesaTransactionService(BaseMpesaService):
    """Service for M-Pesa transaction operations"""

    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        return await self._make_authenticated_request(
            "GET",
            f"/mpesa/transactionstatus/v1/query?TransactionID={transaction_id}"
        )

    async def get_merchant_transactions(
        self,
        shortcode: str,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get merchant transactions (if API supports it)"""
        params = {
            "ShortCode": shortcode,
            "StartDate": start_date.strftime("%Y%m%d"),
            "EndDate": end_date.strftime("%Y%m%d"),
            "Page": page,
            "Limit": limit
        }

        # Note: This endpoint may not exist in real M-Pesa API
        # This is a placeholder for potential future functionality
        return await self._make_authenticated_request(
            "GET",
            "/mpesa/transactions",
            params=params
        )

# Factory for creating services
class MpesaServiceFactory:
    """Factory for creating M-Pesa services with proper configuration"""

    @staticmethod
    def create_channel_service(
        consumer_key: str,
        consumer_secret: str,
        environment: str = "sandbox"
    ) -> MpesaChannelService:
        """Create a channel service instance"""
        config = MpesaConfig(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment
        )
        return MpesaChannelService(config)

    @staticmethod
    def create_transaction_service(
        consumer_key: str,
        consumer_secret: str,
        environment: str = "sandbox"
    ) -> MpesaTransactionService:
        """Create a transaction service instance"""
        config = MpesaConfig(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment
        )
        return MpesaTransactionService(config)

# Legacy compatibility - keep existing interface
class MpesaService(MpesaChannelService):
    """Legacy MpesaService class for backward compatibility"""

    def __init__(self, consumer_key: str, consumer_secret: str, environment: str = "sandbox"):
        config = MpesaConfig(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment=environment
        )
        super().__init__(config)

# Export public API
__all__ = [
    "MpesaService",
    "MpesaChannelService",
    "MpesaTransactionService",
    "MpesaServiceFactory",
    "MpesaConfig",
    "MpesaAPIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError"
]
