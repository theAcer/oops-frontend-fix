"""
M-Pesa Test Fixtures

Centralized fixtures for M-Pesa service testing.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional
import httpx

from app.services.mpesa import (
    MpesaConfig,
    MpesaEnvironment,
    MpesaServiceFactory,
    MpesaChannelService,
    MpesaTransactionService
)
from app.services.mpesa.protocols import HTTPClient, CacheProvider


class MockHTTPClient:
    """Mock HTTP client for testing"""
    
    def __init__(self):
        self.requests = []
        self.responses = {}
        self.default_response = None
    
    def set_response(self, url_pattern: str, response_data: Dict[str, Any], status_code: int = 200):
        """Set mock response for URL pattern"""
        self.responses[url_pattern] = {
            "json": response_data,
            "status_code": status_code,
            "content": b"test content"
        }
    
    def set_default_response(self, response_data: Dict[str, Any], status_code: int = 200):
        """Set default response for all requests"""
        self.default_response = {
            "json": response_data,
            "status_code": status_code,
            "content": b"test content"
        }
    
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
    ) -> Mock:
        """Mock HTTP request"""
        # Record request
        request_info = {
            "method": method,
            "url": url,
            "headers": headers,
            "json": json,
            "data": data,
            "params": params,
            "timeout": timeout
        }
        self.requests.append(request_info)
        
        # Find matching response
        response_data = None
        for pattern, resp in self.responses.items():
            if pattern in url:
                response_data = resp
                break
        
        if not response_data and self.default_response:
            response_data = self.default_response
        
        if not response_data:
            response_data = {
                "json": {"ResponseCode": "0", "ResponseDescription": "Success"},
                "status_code": 200,
                "content": b"test content"
            }
        
        # Create mock response
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = response_data["status_code"]
        mock_response.content = response_data["content"]
        mock_response.json.return_value = response_data["json"]
        mock_response.headers = {}
        
        return mock_response
    
    async def close(self):
        """Mock close method"""
        pass


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self.data = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from mock cache"""
        return self.data.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in mock cache"""
        self.data[key] = value
    
    async def delete(self, key: str) -> None:
        """Delete value from mock cache"""
        self.data.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in mock cache"""
        return key in self.data


@pytest.fixture
def mpesa_config():
    """Test M-Pesa configuration"""
    return MpesaConfig.for_testing()


@pytest.fixture
def mock_http_client():
    """Mock HTTP client fixture"""
    return MockHTTPClient()


@pytest.fixture
def mock_cache():
    """Mock cache fixture"""
    return MockCache()


@pytest.fixture
def mock_logger():
    """Mock logger fixture"""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
async def channel_service(mpesa_config, mock_http_client, mock_cache, mock_logger):
    """M-Pesa channel service fixture"""
    service = MpesaChannelService(
        config=mpesa_config,
        http_client=mock_http_client,
        cache=mock_cache,
        logger=mock_logger
    )
    yield service
    await service.close()


@pytest.fixture
async def transaction_service(mpesa_config, mock_http_client, mock_cache, mock_logger):
    """M-Pesa transaction service fixture"""
    service = MpesaTransactionService(
        config=mpesa_config,
        http_client=mock_http_client,
        cache=mock_cache,
        logger=mock_logger
    )
    yield service
    await service.close()


@pytest.fixture
def oauth_token_response():
    """Mock OAuth token response"""
    return {
        "access_token": "test_access_token_12345",
        "expires_in": "3599"
    }


@pytest.fixture
def channel_verification_response():
    """Mock channel verification response"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "The service request has been accepted successfully.",
        "ConversationID": "AG_20231201_12345678901234567890",
        "OriginatorConversationID": "12345-67890-12345"
    }


@pytest.fixture
def url_registration_response():
    """Mock URL registration response"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "The service request has been accepted successfully."
    }


@pytest.fixture
def c2b_simulation_response():
    """Mock C2B simulation response"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "The service request has been accepted successfully.",
        "ConversationID": "AG_20231201_12345678901234567890",
        "OriginatorConversationID": "12345-67890-12345"
    }


@pytest.fixture
def stk_push_response():
    """Mock STK Push response"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "Success. Request accepted for processing",
        "MerchantRequestID": "12345-67890-12345",
        "CheckoutRequestID": "ws_CO_12345678901234567890",
        "CustomerMessage": "Success. Request accepted for processing"
    }


@pytest.fixture
def stk_query_response():
    """Mock STK Push query response"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "The service request has been accepted successfully.",
        "MerchantRequestID": "12345-67890-12345",
        "CheckoutRequestID": "ws_CO_12345678901234567890",
        "ResultCode": "0",
        "ResultDesc": "The service request is processed successfully.",
        "MpesaReceiptNumber": "ABC123DEF456",
        "TransactionDate": "20231201120000",
        "Amount": "100.00",
        "PhoneNumber": "254712345678"
    }


@pytest.fixture
def sample_merchant_config():
    """Sample merchant configuration for testing"""
    return {
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret",
        "shortcode": "174379",
        "passkey": "test_passkey",
        "environment": "sandbox"
    }


@pytest.fixture
def sample_channel_data():
    """Sample channel data for testing"""
    return {
        "shortcode": "174379",
        "channel_type": "paybill",
        "environment": "sandbox",
        "consumer_key": "test_key",
        "consumer_secret": "test_secret"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        "amount": 100.0,
        "customer_phone": "254712345678",
        "bill_ref": "TEST-001",
        "account_reference": "TEST-ACCOUNT",
        "transaction_desc": "Test transaction"
    }


# Integration test fixtures
@pytest.fixture
async def services_with_shared_deps(mpesa_config):
    """Create services with shared dependencies for integration testing"""
    http_client = MockHTTPClient()
    cache = MockCache()
    logger = Mock()
    
    services = MpesaServiceFactory.create_services(
        consumer_key=mpesa_config.consumer_key,
        consumer_secret=mpesa_config.consumer_secret,
        environment=mpesa_config.environment.value,
        shared_dependencies={
            "http_client": http_client,
            "cache": cache,
            "logger": logger
        }
    )
    
    yield services, http_client, cache, logger
    
    # Cleanup
    for service in services.values():
        await service.close()


# Error response fixtures
@pytest.fixture
def auth_error_response():
    """Mock authentication error response"""
    return {
        "errorCode": "401.002.01",
        "errorMessage": "Error Occurred - Invalid Access Token - BJGFGOXv5ykcWvOgwjzNXTfJGvQA"
    }


@pytest.fixture
def validation_error_response():
    """Mock validation error response"""
    return {
        "ResponseCode": "400.002.02",
        "ResponseDescription": "Bad Request - Invalid ShortCode"
    }


@pytest.fixture
def rate_limit_error_response():
    """Mock rate limit error response"""
    return {
        "errorCode": "429.001.01",
        "errorMessage": "Request rate limit exceeded"
    }
