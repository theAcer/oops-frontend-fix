"""
M-Pesa specific test fixtures for channel management testing.
"""
import pytest
from unittest.mock import Mock, patch
from app.models.merchant import Merchant
from app.schemas.mpesa import MpesaChannelCreate, MpesaChannelResponse

@pytest.fixture
def mock_mpesa_config():
    """Mock M-Pesa configuration for testing"""
    return {
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret",
        "environment": "sandbox",
        "shortcode": "174379"
    }

@pytest.fixture
def sample_channel_data():
    """Sample M-Pesa channel data for testing"""
    return {
        "shortcode": "174379",
        "channel_type": "paybill",
        "environment": "sandbox",
        "consumer_key": "test_key",
        "consumer_secret": "test_secret"
    }

@pytest.fixture
def mock_daraja_api():
    """Mock Daraja API responses"""
    with patch('app.services.daraja_service.DarajaService') as mock_service:
        mock_instance = Mock()
        mock_instance.get_access_token.return_value = {"access_token": "mock_token"}
        mock_instance.register_urls.return_value = {"ResponseCode": "0"}
        mock_instance.simulate_transaction.return_value = {
            "ResponseCode": "0",
            "ResponseDescription": "Success"
        }
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
async def create_test_mpesa_channel(db, create_test_merchant: Merchant):
    """Create a test M-Pesa channel"""
    from app.models.mpesa_channel import MpesaChannel
    
    channel = MpesaChannel(
        merchant_id=create_test_merchant.id,
        shortcode="174379",
        channel_type="paybill",
        environment="sandbox",
        consumer_key="test_key",
        consumer_secret="test_secret",
        status="active"
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel
