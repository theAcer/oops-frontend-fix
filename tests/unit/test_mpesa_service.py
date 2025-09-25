"""
M-Pesa Channel Management - Unit Tests

Comprehensive unit tests for the M-Pesa service layer,
demonstrating testing best practices for scalable applications.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from app.services.mpesa_service_refactored import (
    MpesaServiceFactory,
    MpesaConfig,
    MpesaChannelService,
    MpesaAPIError,
    AuthenticationError,
    RateLimitError
)
from app.schemas.mpesa_channel import MpesaChannelCreate


# Test Fixtures
@pytest.fixture
def mpesa_config():
    """Test configuration for M-Pesa service"""
    return MpesaConfig(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        environment="sandbox",
        timeout=30,
        max_retries=3,
        retry_delay=0.1
    )


@pytest.fixture
def channel_service(mpesa_config):
    """M-Pesa channel service instance"""
    return MpesaServiceFactory.create_channel_service(
        consumer_key=mpesa_config.consumer_key,
        consumer_secret=mpesa_config.consumer_secret,
        environment=mpesa_config.environment
    )


# Unit Tests for MpesaChannelService
class TestMpesaChannelService:
    """Unit tests for M-Pesa channel service"""

    @pytest.mark.asyncio
    async def test_verify_channel_success(self, channel_service):
        """Test successful channel verification"""
        shortcode = "174379"

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ResponseCode": "0",
            "ResponseDescription": "Success"
        }

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            result = await channel_service.verify_channel(shortcode)

            assert result["status"] == "verified"
            assert result["message"] == "Channel credentials are valid"
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_verify_channel_auth_failure(self, channel_service):
        """Test channel verification with authentication failure"""
        shortcode = "174379"

        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "errorCode": "401.001.03",
            "message": "Invalid credentials"
        }

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await channel_service.verify_channel(shortcode)

    @pytest.mark.asyncio
    async def test_verify_channel_rate_limit(self, channel_service):
        """Test channel verification with rate limiting"""
        shortcode = "174379"

        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                await channel_service.verify_channel(shortcode)

    @pytest.mark.asyncio
    async def test_register_urls_success(self, channel_service):
        """Test successful URL registration"""
        shortcode = "174379"
        confirmation_url = "https://example.com/confirm"
        validation_url = "https://example.com/validate"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ResponseCode": "0",
            "ResponseDescription": "Success"
        }

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.post.return_value = mock_response

            result = await channel_service.register_urls(
                shortcode=shortcode,
                confirmation_url=confirmation_url,
                validation_url=validation_url
            )

            assert result["ResponseCode"] == "0"
            assert result["ResponseDescription"] == "Success"

            # Verify request payload
            call_args = mock_http.post.call_args
            payload = call_args[1]['json']
            assert payload["ShortCode"] == shortcode
            assert payload["ConfirmationURL"] == confirmation_url
            assert payload["ValidationURL"] == validation_url

    @pytest.mark.asyncio
    async def test_simulate_transaction_sandbox_only(self, mpesa_config):
        """Test that simulation only works in sandbox environment"""
        mpesa_config.environment = "production"
        service = MpesaServiceFactory.create_channel_service(
            consumer_key=mpesa_config.consumer_key,
            consumer_secret=mpesa_config.consumer_secret,
            environment=mpesa_config.environment
        )

        with pytest.raises(MpesaAPIError, match="Simulation only available in sandbox"):
            await service.simulate_transaction(
                shortcode="174379",
                amount=100.0,
                msisdn="254712345678"
            )

    @pytest.mark.asyncio
    async def test_simulate_transaction_success(self, channel_service):
        """Test successful transaction simulation"""
        shortcode = "174379"
        amount = 100.0
        msisdn = "254712345678"
        bill_ref = "TEST-001"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ResponseCode": "0",
            "ResponseDescription": "Success",
            "TransactionId": "TEST123"
        }

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.post.return_value = mock_response

            result = await channel_service.simulate_transaction(
                shortcode=shortcode,
                amount=amount,
                msisdn=msisdn,
                bill_ref_number=bill_ref
            )

            assert result["ResponseCode"] == "0"
            assert result["TransactionId"] == "TEST123"

            # Verify request payload
            call_args = mock_http.post.call_args
            payload = call_args[1]['json']
            assert payload["ShortCode"] == shortcode
            assert payload["Amount"] == amount
            assert payload["Msisdn"] == msisdn
            assert payload["BillRefNumber"] == bill_ref

    @pytest.mark.asyncio
    async def test_token_caching(self, channel_service):
        """Test OAuth token caching behavior"""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "cached_token_123"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            # First call - should fetch token
            token1 = await channel_service._get_oauth_token()
            assert token1 == "cached_token_123"
            assert mock_http.get.call_count == 1

            # Second call - should use cached token
            token2 = await channel_service._get_oauth_token()
            assert token2 == "cached_token_123"
            assert mock_http.get.call_count == 1  # Still 1, cache hit

    @pytest.mark.asyncio
    async def test_token_cache_expiry(self, channel_service):
        """Test token cache expiry and refresh"""
        import time
        from datetime import datetime, timedelta

        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "fresh_token_456"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            # First call
            token1 = await channel_service._get_oauth_token()
            assert token1 == "fresh_token_456"
            first_call_count = mock_http.get.call_count

            # Manually expire the cache
            channel_service._token_expires_at = datetime.utcnow() - timedelta(seconds=1)

            # Second call should fetch new token
            token2 = await channel_service._get_oauth_token()
            assert token2 == "fresh_token_456"
            assert mock_http.get.call_count == first_call_count + 1

    def test_credential_encoding(self, channel_service):
        """Test credential encoding for Basic Auth"""
        import base64

        expected_credentials = f"{channel_service.config.consumer_key}:{channel_service.config.consumer_secret}"
        expected_encoded = base64.b64encode(expected_credentials.encode()).decode()

        encoded = channel_service._encode_credentials()
        assert encoded == expected_encoded

    def test_phone_number_normalization(self, channel_service):
        """Test phone number normalization utility"""
        # Test Kenyan phone numbers
        test_cases = [
            ("254712345678", "254712345678"),
            ("0712345678", "254712345678"),
            ("712345678", "254712345678"),
            ("+254712345678", "254712345678"),
            ("254-712-345-678", "254712345678"),
        ]

        for input_phone, expected in test_cases:
            result = channel_service._normalize_phone_number(input_phone)
            assert result == expected, f"Failed for input: {input_phone}"


# Unit Tests for MpesaConfig
class TestMpesaConfig:
    """Unit tests for M-Pesa configuration"""

    def test_config_creation(self):
        """Test configuration object creation"""
        config = MpesaConfig(
            consumer_key="test_key",
            consumer_secret="test_secret",
            environment="sandbox"
        )

        assert config.consumer_key == "test_key"
        assert config.consumer_secret == "test_secret"
        assert config.environment == "sandbox"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_api_base_url_sandbox(self):
        """Test API base URL for sandbox"""
        config = MpesaConfig(
            consumer_key="key",
            consumer_secret="secret",
            environment="sandbox"
        )
        assert config.api_base_url == "https://sandbox.safaricom.co.ke"

    def test_api_base_url_production(self):
        """Test API base URL for production"""
        config = MpesaConfig(
            consumer_key="key",
            consumer_secret="secret",
            environment="production"
        )
        assert config.api_base_url == "https://api.safaricom.co.ke"

    def test_custom_base_url(self):
        """Test custom base URL configuration"""
        custom_url = "https://custom.api.example.com"
        config = MpesaConfig(
            consumer_key="key",
            consumer_secret="secret",
            base_url=custom_url
        )
        assert config.api_base_url == custom_url


# Unit Tests for Error Handling
class TestErrorHandling:
    """Unit tests for error handling"""

    @pytest.mark.asyncio
    async def test_retry_logic_success(self, channel_service):
        """Test retry logic with eventual success"""
        shortcode = "174379"

        # Mock responses: first two fail, third succeeds
        mock_responses = [
            Mock(status_code=500, json=lambda: {"error": "Server error"}),
            Mock(status_code=500, json=lambda: {"error": "Server error"}),
            Mock(status_code=200, json=lambda: {"ResponseCode": "0", "ResponseDescription": "Success"})
        ]

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.side_effect = mock_responses

            result = await channel_service.verify_channel(shortcode)

            assert result["status"] == "verified"
            assert mock_http.get.call_count == 3  # All retries used

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, channel_service):
        """Test behavior when max retries are exceeded"""
        shortcode = "174379"

        # Mock persistent failure
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Persistent failure"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            with pytest.raises(MpesaAPIError, match="Request failed after 3 attempts"):
                await channel_service.verify_channel(shortcode)

    @pytest.mark.asyncio
    async def test_network_error_handling(self, channel_service):
        """Test handling of network errors"""
        shortcode = "174379"

        with patch.object(channel_service, 'http_client') as mock_http:
            # Mock network error
            mock_http.get.side_effect = httpx.RequestError("Network unreachable")

            with pytest.raises(MpesaAPIError, match="Request failed after 3 attempts"):
                await channel_service.verify_channel(shortcode)


# Unit Tests for Schema Validation
class TestChannelValidation:
    """Unit tests for channel validation schemas"""

    def test_valid_channel_creation(self):
        """Test valid channel creation data"""
        from app.schemas.mpesa_channel import MpesaChannelCreate

        valid_data = {
            "shortcode": "174379",
            "channel_type": "paybill",
            "environment": "sandbox",
            "consumer_key": "test_key",
            "consumer_secret": "test_secret"
        }

        channel = MpesaChannelCreate(**valid_data)
        assert channel.shortcode == "174379"
        assert channel.channel_type == "paybill"
        assert channel.environment == "sandbox"

    def test_invalid_shortcode_length(self):
        """Test shortcode length validation"""
        from pydantic import ValidationError
        from app.schemas.mpesa_channel import MpesaChannelCreate

        invalid_data = {
            "shortcode": "123",  # Too short
            "channel_type": "paybill",
            "environment": "sandbox",
            "consumer_key": "test_key",
            "consumer_secret": "test_secret"
        }

        with pytest.raises(ValidationError):
            MpesaChannelCreate(**invalid_data)

    def test_invalid_channel_type(self):
        """Test channel type validation"""
        from pydantic import ValidationError
        from app.schemas.mpesa_channel import MpesaChannelCreate

        invalid_data = {
            "shortcode": "174379",
            "channel_type": "invalid_type",  # Invalid type
            "environment": "sandbox",
            "consumer_key": "test_key",
            "consumer_secret": "test_secret"
        }

        with pytest.raises(ValidationError):
            MpesaChannelCreate(**invalid_data)

    def test_invalid_environment(self):
        """Test environment validation"""
        from pydantic import ValidationError
        from app.schemas.mpesa_channel import MpesaChannelCreate

        invalid_data = {
            "shortcode": "174379",
            "channel_type": "paybill",
            "environment": "invalid_env",  # Invalid environment
            "consumer_key": "test_key",
            "consumer_secret": "test_secret"
        }

        with pytest.raises(ValidationError):
            MpesaChannelCreate(**invalid_data)


# Performance Tests
class TestPerformance:
    """Performance-related tests"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, channel_service):
        """Test handling of concurrent requests"""
        import asyncio

        shortcode = "174379"

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ResponseCode": "0", "ResponseDescription": "Success"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            # Run multiple concurrent requests
            tasks = [
                channel_service.verify_channel(shortcode)
                for _ in range(10)
            ]

            results = await asyncio.gather(*tasks)

            # All should succeed
            assert len(results) == 10
            assert all(r["status"] == "verified" for r in results)

            # HTTP client should be called once due to caching
            assert mock_http.get.call_count == 1

    @pytest.mark.asyncio
    async def test_token_cache_concurrent_access(self, channel_service):
        """Test token cache behavior under concurrent access"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "concurrent_token"}

        with patch.object(channel_service, 'http_client') as mock_http:
            mock_http.get.return_value = mock_response

            # Multiple concurrent token requests
            tasks = [
                channel_service._get_oauth_token()
                for _ in range(5)
            ]

            tokens = await asyncio.gather(*tasks)

            # All should get the same token
            assert len(set(tokens)) == 1
            # HTTP client should be called only once
            assert mock_http.get.call_count == 1


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([
        __file__,
        "--cov=app.services.mpesa_service_refactored",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    ])
