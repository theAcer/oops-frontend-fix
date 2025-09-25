"""
M-Pesa Channel Management - Integration Tests

Integration tests for API endpoints and service interactions,
testing the complete request/response cycle with mocked external dependencies.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.services.merchant_service import MerchantService
from app.models.mpesa_channel import MpesaChannel
from app.schemas.mpesa_channel import MpesaChannelResponse, MpesaChannelCreate


# Test Fixtures
@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_channel():
    """Mock M-Pesa channel"""
    channel = Mock(spec=MpesaChannel)
    channel.id = 1
    channel.merchant_id = 1
    channel.shortcode = "174379"
    channel.channel_type = "paybill"
    channel.environment = "sandbox"
    channel.status = "unverified"
    channel.consumer_key = "test_key"
    channel.consumer_secret = "test_secret"
    return channel


# API Integration Tests
class TestChannelAPIIntegration:
    """Integration tests for channel API endpoints"""

    def test_create_channel_success(self, test_client, mock_db_session):
        """Test successful channel creation"""
        # Mock authentication
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            # Mock merchant service
            with patch("app.services.merchant_service.MerchantService") as mock_service_class:
                mock_service = AsyncMock()
                mock_channel = Mock()
                mock_channel.id = 1
                mock_channel.shortcode = "174379"
                mock_channel.channel_type = "paybill"
                mock_channel.environment = "sandbox"
                mock_channel.status = "unverified"
                mock_service.create_mpesa_channel.return_value = mock_channel
                mock_service_class.return_value = mock_service

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels",
                    json={
                        "shortcode": "174379",
                        "channel_type": "paybill",
                        "environment": "sandbox",
                        "consumer_key": "test_key",
                        "consumer_secret": "test_secret"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 201
                data = response.json()
                assert data["shortcode"] == "174379"
                assert data["channel_type"] == "paybill"
                assert data["status"] == "unverified"

    def test_create_channel_unauthorized(self, test_client):
        """Test channel creation without authentication"""
        response = test_client.post(
            "/api/v1/merchants/1/mpesa/channels",
            json={
                "shortcode": "174379",
                "channel_type": "paybill",
                "environment": "sandbox"
            }
        )

        assert response.status_code == 401

    def test_create_channel_invalid_data(self, test_client):
        """Test channel creation with invalid data"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            response = test_client.post(
                "/api/v1/merchants/1/mpesa/channels",
                json={
                    "shortcode": "123",  # Invalid length
                    "channel_type": "invalid_type",  # Invalid type
                    "environment": "sandbox"
                },
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_verify_channel_success(self, test_client, mock_db_session):
        """Test successful channel verification"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_service = AsyncMock()
                mock_service.verify_channel.return_value = {
                    "status": "verified",
                    "message": "Channel credentials are valid"
                }
                mock_factory.create_channel_service.return_value = mock_service

                with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                    mock_merchant_service_instance = AsyncMock()
                    mock_channel = Mock()
                    mock_channel.id = 1
                    mock_channel.status = "verified"
                    mock_merchant_service_instance.verify_mpesa_channel.return_value = mock_channel
                    mock_merchant_service.return_value = mock_merchant_service_instance

                    response = test_client.post(
                        "/api/v1/merchants/1/mpesa/channels/1/verify",
                        headers={"Authorization": "Bearer test_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "verified"

    @pytest.mark.asyncio
    async def test_verify_channel_not_found(self, test_client):
        """Test channel verification for non-existent channel"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_merchant_service_instance.verify_mpesa_channel.return_value = None
                mock_merchant_service.return_value = mock_merchant_service_instance

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/999/verify",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 404
                assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_urls_success(self, test_client):
        """Test successful URL registration"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_channel = Mock()
                mock_channel.id = 1
                mock_channel.status = "urls_registered"
                mock_merchant_service_instance.register_mpesa_urls.return_value = mock_channel
                mock_merchant_service.return_value = mock_merchant_service_instance

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/register-urls",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "urls_registered"

    @pytest.mark.asyncio
    async def test_simulate_transaction_success(self, test_client):
        """Test successful transaction simulation"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_merchant_service_instance.simulate_mpesa_transaction.return_value = {
                    "ResponseCode": "0",
                    "ResponseDescription": "Success",
                    "TransactionId": "TEST123"
                }
                mock_merchant_service.return_value = mock_merchant_service_instance

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/simulate",
                    json={
                        "amount": 100.0,
                        "customer_phone": "254712345678",
                        "bill_ref": "TEST-001"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["ResponseCode"] == "0"
                assert data["TransactionId"] == "TEST123"

    @pytest.mark.asyncio
    async def test_simulate_transaction_production_error(self, test_client):
        """Test simulation error in production environment"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_merchant_service_instance.simulate_mpesa_transaction.side_effect = ValueError(
                    "Simulation only available in sandbox environment"
                )
                mock_merchant_service.return_value = mock_merchant_service_instance

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/simulate",
                    json={
                        "amount": 100.0,
                        "customer_phone": "254712345678"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 400
                assert "sandbox" in response.json()["detail"].lower()

    def test_list_channels_unauthorized(self, test_client):
        """Test listing channels without authentication"""
        response = test_client.get("/api/v1/merchants/1/mpesa/channels")
        assert response.status_code == 401

    def test_get_channel_not_found(self, test_client):
        """Test getting non-existent channel"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_merchant_service_instance.get_mpesa_channel.return_value = None
                mock_merchant_service.return_value = mock_merchant_service_instance

                response = test_client.get(
                    "/api/v1/mpesa/channels/999",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 404


# Database Integration Tests
class TestDatabaseIntegration:
    """Database integration tests"""

    @pytest.mark.asyncio
    async def test_channel_creation_persistence(self, mock_db_session):
        """Test that created channels are properly persisted"""
        service = MerchantService(mock_db_session)

        channel_data = MpesaChannelCreate(
            shortcode="174379",
            channel_type="paybill",
            environment="sandbox",
            consumer_key="test_key",
            consumer_secret="test_secret"
        )

        mock_channel = Mock()
        mock_channel.id = 1
        mock_channel.shortcode = "174379"
        mock_channel.channel_type = "paybill"
        mock_channel.environment = "sandbox"
        mock_channel.status = "unverified"

        with patch.object(service, 'get_mpesa_channel') as mock_get:
            mock_get.return_value = None

            with patch('app.models.mpesa_channel.MpesaChannel') as mock_model:
                mock_model.return_value = mock_channel

                result = await service.create_mpesa_channel(1, channel_data)

                # Verify channel was created with correct data
                assert result.id == 1
                assert result.shortcode == "174379"
                assert result.status == "unverified"

                # Verify database operations
                mock_db_session.add.assert_called_once_with(mock_channel)
                mock_db_session.commit.assert_called_once()
                mock_db_session.refresh.assert_called_once_with(mock_channel)

    @pytest.mark.asyncio
    async def test_channel_status_transition(self, mock_db_session):
        """Test channel status transitions in database"""
        service = MerchantService(mock_db_session)

        # Mock existing channel
        mock_channel = Mock()
        mock_channel.id = 1
        mock_channel.status = "unverified"
        mock_channel.consumer_key = "test_key"
        mock_channel.consumer_secret = "test_secret"
        mock_channel.shortcode = "174379"
        mock_channel.environment = "sandbox"

        with patch.object(service, 'get_mpesa_channel') as mock_get:
            mock_get.return_value = mock_channel

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_mpesa_service = AsyncMock()
                mock_mpesa_service.verify_channel.return_value = {
                    "status": "verified",
                    "message": "Channel verified successfully"
                }
                mock_factory.create_channel_service.return_value = mock_mpesa_service

                result = await service.verify_mpesa_channel(1)

                # Verify status transition
                assert result.status == "verified"
                assert mock_db_session.commit.called
                assert mock_db_session.refresh.called

    @pytest.mark.asyncio
    async def test_transaction_idempotency(self, mock_db_session):
        """Test idempotent transaction handling"""
        service = MerchantService(mock_db_session)

        # Mock existing transaction
        mock_transaction = Mock()
        mock_transaction.id = 1
        mock_transaction.mpesa_receipt_number = "TEST123"
        mock_transaction.amount = 100.0

        with patch.object(service, 'db') as mock_db:
            mock_db.execute.return_value = Mock(scalar_one_or_none=Mock(return_value=mock_transaction))

            # This would be called when processing a duplicate transaction
            # The service should handle it idempotently
            pass  # Implementation would depend on specific business logic


# External Service Integration Tests
class TestExternalServiceIntegration:
    """Integration tests with external services"""

    @pytest.mark.asyncio
    async def test_mpesa_api_connectivity(self, test_client):
        """Test connectivity to M-Pesa API"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_service = AsyncMock()
                mock_service.verify_channel.return_value = {
                    "status": "verified",
                    "message": "API connectivity successful"
                }
                mock_factory.create_channel_service.return_value = mock_service

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/verify",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_mpesa_api_failure_handling(self, test_client):
        """Test handling of M-Pesa API failures"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_service = AsyncMock()
                mock_service.verify_channel.side_effect = Exception("API unavailable")
                mock_factory.create_channel_service.return_value = mock_service

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/verify",
                    headers={"Authorization": "Bearer test_token"}
                )

                # Should return proper error response
                assert response.status_code in [500, 400]

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, test_client):
        """Test rate limit handling from M-Pesa API"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_service = AsyncMock()
                mock_service.verify_channel.side_effect = Exception("Rate limit exceeded")
                mock_factory.create_channel_service.return_value = mock_service

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels/1/verify",
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 429 or response.status_code == 500


# Error Handling Integration Tests
class TestErrorHandlingIntegration:
    """Integration tests for error handling"""

    def test_invalid_json_payload(self, test_client):
        """Test handling of invalid JSON payload"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            response = test_client.post(
                "/api/v1/merchants/1/mpesa/channels",
                data="invalid json",
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 422

    def test_missing_required_fields(self, test_client):
        """Test handling of missing required fields"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            response = test_client.post(
                "/api/v1/merchants/1/mpesa/channels",
                json={
                    "shortcode": "174379"
                    # Missing required fields
                },
                headers={"Authorization": "Bearer test_token"}
            )

            assert response.status_code == 422

    def test_database_connection_error(self, test_client):
        """Test handling of database connection errors"""
        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_service_class:
                mock_service = AsyncMock()
                mock_service.create_mpesa_channel.side_effect = Exception("Database connection failed")
                mock_service_class.return_value = mock_service

                response = test_client.post(
                    "/api/v1/merchants/1/mpesa/channels",
                    json={
                        "shortcode": "174379",
                        "channel_type": "paybill",
                        "environment": "sandbox"
                    },
                    headers={"Authorization": "Bearer test_token"}
                )

                assert response.status_code == 500


# Performance Integration Tests
class TestPerformanceIntegration:
    """Performance-related integration tests"""

    @pytest.mark.asyncio
    async def test_concurrent_channel_verification(self, test_client):
        """Test concurrent channel verification requests"""
        import asyncio

        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.mpesa_service_refactored.MpesaServiceFactory") as mock_factory:
                mock_service = AsyncMock()
                mock_service.verify_channel.return_value = {
                    "status": "verified",
                    "message": "Channel verified"
                }
                mock_factory.create_channel_service.return_value = mock_service

                with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                    mock_merchant_service_instance = AsyncMock()
                    mock_channel = Mock()
                    mock_channel.status = "verified"
                    mock_merchant_service_instance.verify_mpesa_channel.return_value = mock_channel
                    mock_merchant_service.return_value = mock_merchant_service_instance

                    # Make concurrent requests
                    async def make_request():
                        return test_client.post(
                            "/api/v1/merchants/1/mpesa/channels/1/verify",
                            headers={"Authorization": "Bearer test_token"}
                        )

                    tasks = [make_request() for _ in range(10)]
                    responses = await asyncio.gather(*[task for task in tasks])

                    # All should succeed
                    assert all(r.status_code == 200 for r in responses)

    def test_response_time_requirements(self, test_client):
        """Test that API responses meet performance requirements"""
        import time

        with patch("app.api.v1.endpoints.auth.oauth2_scheme") as mock_auth:
            mock_auth.return_value = "test_token"

            with patch("app.services.merchant_service.MerchantService") as mock_merchant_service:
                mock_merchant_service_instance = AsyncMock()
                mock_channel = Mock()
                mock_channel.id = 1
                mock_channel.shortcode = "174379"
                mock_channel.channel_type = "paybill"
                mock_channel.environment = "sandbox"
                mock_channel.status = "unverified"
                mock_merchant_service_instance.get_mpesa_channel.return_value = mock_channel
                mock_merchant_service.return_value = mock_merchant_service_instance

                start_time = time.time()
                response = test_client.get(
                    "/api/v1/mpesa/channels/1",
                    headers={"Authorization": "Bearer test_token"}
                )
                end_time = time.time()

                # Response should be fast (under 500ms for simple operations)
                assert (end_time - start_time) < 0.5
                assert response.status_code == 200


# Run integration tests
if __name__ == "__main__":
    pytest.main([
        __file__,
        "--cov=app.api.v1.endpoints.merchants",
        "--cov=app.services.merchant_service",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
        "-k integration"
    ])
