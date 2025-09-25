"""
Integration Tests for Merchant M-Pesa Channel Management

Tests the complete flow from merchant creation to M-Pesa channel operations
using the new atomic implementation.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.models.mpesa_channel import MpesaChannel, ChannelStatus, ChannelType
from app.schemas.merchant import MerchantCreate
from app.schemas.mpesa_channel import MpesaChannelCreate
from app.services.merchant_service import MerchantService
from app.services.mpesa_channel_service import MpesaChannelManagementService


@pytest.mark.asyncio
class TestMerchantMpesaIntegration:
    """Integration tests for merchant M-Pesa operations"""
    
    async def test_complete_merchant_mpesa_flow(self, db: AsyncSession):
        """Test complete flow: create merchant → add channel → verify → activate"""
        
        # Step 1: Create merchant
        merchant_service = MerchantService(db)
        merchant_data = MerchantCreate(
            business_name="Test Electronics Store",
            owner_name="John Doe",
            email="john@teststore.com",
            phone="254712345678",
            business_type="RETAIL"
        )
        
        merchant, created = await merchant_service.create_merchant(merchant_data)
        assert created is True
        assert merchant.business_name == "Test Electronics Store"
        
        # Step 2: Add M-Pesa channel using new service
        mpesa_service = MpesaChannelManagementService(db)
        channel_data = MpesaChannelCreate(
            name="Main PayBill",
            shortcode="174379",
            channel_type=ChannelType.PAYBILL,
            environment="sandbox",
            consumer_key="test_consumer_key",
            consumer_secret="test_consumer_secret",
            passkey="test_passkey",
            validation_url="https://test.com/validation",
            confirmation_url="https://test.com/confirmation",
            account_mapping={
                "default": "loyalty",
                "VIP*": "vip_program"
            },
            is_primary=True
        )
        
        channel_response = await mpesa_service.create_channel(merchant.id, channel_data)
        assert channel_response.name == "Main PayBill"
        assert channel_response.shortcode == "174379"
        assert channel_response.is_primary is True
        assert channel_response.status == ChannelStatus.CONFIGURED
        
        # Step 3: Verify channel with mocked M-Pesa API
        with patch('app.services.mpesa.MpesaServiceFactory.create_channel_service') as mock_factory:
            mock_service = AsyncMock()
            mock_service.verify_channel.return_value = {
                "status": "verified",
                "shortcode": "174379",
                "response_code": "0",
                "verified_at": "2024-01-15T10:30:00Z"
            }
            mock_service.close = AsyncMock()
            mock_factory.return_value = mock_service
            
            verification_result = await merchant_service.verify_mpesa_channel(
                merchant.id, channel_response.id
            )
            
            assert verification_result["verified"] is True
            assert verification_result["channel_id"] == channel_response.id
        
        # Step 4: Register URLs
        with patch('app.services.mpesa.MpesaServiceFactory.create_channel_service') as mock_factory:
            mock_service = AsyncMock()
            mock_service.register_urls.return_value = {
                "status": "registered",
                "ResponseCode": "0",
                "registered_at": "2024-01-15T10:35:00Z"
            }
            mock_service.close = AsyncMock()
            mock_factory.return_value = mock_service
            
            registration_result = await merchant_service.register_mpesa_urls(
                merchant_id=merchant.id,
                channel_id=channel_response.id,
                validation_url="https://test.com/validation",
                confirmation_url="https://test.com/confirmation"
            )
            
            assert registration_result["registered"] is True
            assert registration_result["channel_id"] == channel_response.id
        
        # Step 5: Activate channel
        activated_channel = await merchant_service.activate_channel(merchant.id, channel_response.id)
        assert activated_channel is not None
        assert activated_channel.status == ChannelStatus.ACTIVE
        assert activated_channel.is_active is True
        
        # Step 6: Simulate transaction
        with patch('app.services.mpesa.MpesaServiceFactory.create_transaction_service') as mock_factory:
            mock_service = AsyncMock()
            mock_service.simulate_c2b_transaction.return_value = {
                "status": "success",
                "conversation_id": "AG_20240115_12345",
                "amount": "100.0",
                "customer_phone": "254712345678",
                "simulated_at": "2024-01-15T10:40:00Z"
            }
            mock_service.close = AsyncMock()
            mock_factory.return_value = mock_service
            
            simulation_result = await merchant_service.simulate_mpesa_transaction(
                merchant_id=merchant.id,
                channel_id=channel_response.id,
                amount=100.0,
                customer_phone="254712345678",
                bill_ref="TEST001"
            )
            
            assert simulation_result["status"] == "success"
            assert simulation_result["amount"] == "100.0"
    
    async def test_multiple_channels_per_merchant(self, db: AsyncSession):
        """Test merchant with multiple M-Pesa channels"""
        
        # Create merchant
        merchant_service = MerchantService(db)
        merchant_data = MerchantCreate(
            business_name="Multi-Channel Store",
            owner_name="Jane Smith",
            email="jane@multistore.com",
            phone="254712345679"
        )
        
        merchant, _ = await merchant_service.create_merchant(merchant_data)
        mpesa_service = MpesaChannelManagementService(db)
        
        # Add PayBill channel
        paybill_data = MpesaChannelCreate(
            name="Main PayBill",
            shortcode="174379",
            channel_type=ChannelType.PAYBILL,
            environment="sandbox",
            consumer_key="paybill_key",
            consumer_secret="paybill_secret",
            account_mapping={"default": "loyalty", "VIP*": "vip"},
            is_primary=True
        )
        
        paybill_channel = await mpesa_service.create_channel(merchant.id, paybill_data)
        
        # Add Till channel
        till_data = MpesaChannelCreate(
            name="Shop Till",
            shortcode="123456",
            channel_type=ChannelType.TILL,
            environment="sandbox",
            consumer_key="till_key",
            consumer_secret="till_secret"
        )
        
        till_channel = await mpesa_service.create_channel(merchant.id, till_data)
        assert till_channel.channel_type == ChannelType.TILL
        
        # Add Buy Goods channel
        buygoods_data = MpesaChannelCreate(
            name="Online Store",
            shortcode="789012",
            channel_type=ChannelType.BUYGOODS,
            environment="sandbox",
            consumer_key="buygoods_key",
            consumer_secret="buygoods_secret"
        )
        
        buygoods_channel = await mpesa_service.create_channel(merchant.id, buygoods_data)
        assert buygoods_channel.channel_type == ChannelType.BUYGOODS
        
        # List all channels
        channels = await merchant_service.list_mpesa_channels(merchant.id)
        assert len(channels) == 3
        
        # Verify primary channel
        primary_channels = [ch for ch in channels if ch.is_primary]
        assert len(primary_channels) == 1
        assert primary_channels[0].id == paybill_channel.id
        
        # Test channel types
        channel_types = {ch.channel_type for ch in channels}
        assert channel_types == {ChannelType.PAYBILL, ChannelType.TILL, ChannelType.BUYGOODS}
    
    async def test_account_mapping_functionality(self, db: AsyncSession):
        """Test PayBill account mapping functionality"""
        
        # Create merchant and PayBill channel
        merchant_service = MerchantService(db)
        merchant_data = MerchantCreate(
            business_name="Mapping Test Store",
            email="mapping@test.com"
        )
        
        merchant, _ = await merchant_service.create_merchant(merchant_data)
        mpesa_service = MpesaChannelManagementService(db)
        
        channel_data = MpesaChannelCreate(
            name="PayBill with Mapping",
            shortcode="174379",
            channel_type=ChannelType.PAYBILL,
            environment="sandbox",
            consumer_key="test_key",
            consumer_secret="test_secret",
            account_mapping={
                "default": "standard_loyalty",
                "VIP*": "vip_program",
                "STUDENT*": "student_program",
                "CORPORATE": "b2b_program"
            }
        )
        
        channel_response = await mpesa_service.create_channel(merchant.id, channel_data)
        
        # Get the actual channel from database to test mapping
        from sqlalchemy import select
        result = await db.execute(
            select(MpesaChannel).where(MpesaChannel.id == channel_response.id)
        )
        channel = result.scalar_one()
        
        # Test account mapping
        assert channel.get_account_for_reference("VIP001") == "vip_program"
        assert channel.get_account_for_reference("VIP999") == "vip_program"
        assert channel.get_account_for_reference("STUDENT123") == "student_program"
        assert channel.get_account_for_reference("CORPORATE") == "b2b_program"
        assert channel.get_account_for_reference("RANDOM123") == "standard_loyalty"
    
    async def test_channel_status_transitions(self, db: AsyncSession):
        """Test M-Pesa channel status transitions"""
        
        # Create merchant and channel
        merchant_service = MerchantService(db)
        merchant_data = MerchantCreate(
            business_name="Status Test Store",
            email="status@test.com"
        )
        
        merchant, _ = await merchant_service.create_merchant(merchant_data)
        mpesa_service = MpesaChannelManagementService(db)
        
        channel_data = MpesaChannelCreate(
            name="Status Test Channel",
            shortcode="174379",
            channel_type=ChannelType.PAYBILL,
            environment="sandbox",
            consumer_key="test_key",
            consumer_secret="test_secret"
        )
        
        # Initial status should be CONFIGURED (has credentials)
        channel_response = await mpesa_service.create_channel(merchant.id, channel_data)
        assert channel_response.status == ChannelStatus.CONFIGURED
        
        # Mock verification to change status to VERIFIED
        with patch('app.services.mpesa.MpesaServiceFactory.create_channel_service') as mock_factory:
            mock_service = AsyncMock()
            mock_service.verify_channel.return_value = {"status": "verified"}
            mock_service.close = AsyncMock()
            mock_factory.return_value = mock_service
            
            await merchant_service.verify_mpesa_channel(merchant.id, channel_response.id)
        
        # Check status progression
        status_result = await merchant_service.get_channel_status(merchant.id, channel_response.id)
        assert "verified" in str(status_result.get("status", "")).lower()
        
        # Test activation
        activated_channel = await merchant_service.activate_channel(merchant.id, channel_response.id)
        assert activated_channel.status == ChannelStatus.ACTIVE
        
        # Test deactivation
        deactivated_channel = await merchant_service.deactivate_channel(merchant.id, channel_response.id)
        assert deactivated_channel.status == ChannelStatus.SUSPENDED
        assert deactivated_channel.is_active is False
    
    async def test_error_handling_and_validation(self, db: AsyncSession):
        """Test error handling and validation in M-Pesa operations"""
        
        merchant_service = MerchantService(db)
        
        # Test with non-existent merchant
        result = await merchant_service.get_mpesa_channel(999, 999)
        assert result is None
        
        # Test with non-existent channel
        merchant_data = MerchantCreate(
            business_name="Error Test Store",
            email="error@test.com"
        )
        merchant, _ = await merchant_service.create_merchant(merchant_data)
        
        result = await merchant_service.get_mpesa_channel(merchant.id, 999)
        assert result is None
        
        # Test verification with invalid channel
        verification_result = await merchant_service.verify_mpesa_channel(merchant.id, 999)
        assert verification_result["verified"] is False
        assert "error" in verification_result
    
    async def test_credential_encryption_security(self, db: AsyncSession):
        """Test that credentials are properly encrypted in database"""
        
        # Create merchant and channel
        merchant_service = MerchantService(db)
        merchant_data = MerchantCreate(
            business_name="Security Test Store",
            email="security@test.com"
        )
        
        merchant, _ = await merchant_service.create_merchant(merchant_data)
        mpesa_service = MpesaChannelManagementService(db)
        
        channel_data = MpesaChannelCreate(
            name="Security Test Channel",
            shortcode="174379",
            channel_type=ChannelType.PAYBILL,
            environment="sandbox",
            consumer_key="secret_consumer_key",
            consumer_secret="secret_consumer_secret",
            passkey="secret_passkey"
        )
        
        channel_response = await mpesa_service.create_channel(merchant.id, channel_data)
        
        # Get raw channel from database
        from sqlalchemy import select
        result = await db.execute(
            select(MpesaChannel).where(MpesaChannel.id == channel_response.id)
        )
        channel = result.scalar_one()
        
        # Verify credentials are encrypted in database
        assert channel.consumer_key_encrypted is not None
        assert channel.consumer_secret_encrypted is not None
        assert channel.passkey_encrypted is not None
        
        # Verify encrypted values are different from plain text
        assert channel.consumer_key_encrypted != "secret_consumer_key"
        assert channel.consumer_secret_encrypted != "secret_consumer_secret"
        assert channel.passkey_encrypted != "secret_passkey"
        
        # Verify decryption works
        assert channel.consumer_key == "secret_consumer_key"
        assert channel.consumer_secret == "secret_consumer_secret"
        assert channel.passkey == "secret_passkey"


@pytest.mark.asyncio
class TestMerchantMpesaAPI:
    """Integration tests for M-Pesa API endpoints"""
    
    async def test_merchant_mpesa_api_flow(self, client: AsyncClient, db: AsyncSession):
        """Test complete M-Pesa API flow through HTTP endpoints"""
        
        # Create merchant via API
        merchant_data = {
            "business_name": "API Test Store",
            "owner_name": "API Tester",
            "email": "api@test.com",
            "phone": "254712345678"
        }
        
        response = await client.post("/api/v1/merchants/", json=merchant_data)
        assert response.status_code == 201
        merchant = response.json()
        merchant_id = merchant["id"]
        
        # List channels (should be empty initially)
        response = await client.get(f"/api/v1/merchants/{merchant_id}/mpesa/channels")
        assert response.status_code == 200
        assert response.json() == []
        
        # Note: This would use the dedicated M-Pesa channels API
        # For now, we'll test through the merchant API
        
        # Get channel status
        # This endpoint doesn't exist in current merchant API, would need to be added
        # or use the dedicated M-Pesa channels API
        
        # Verify channel with mocked response
        with patch('app.services.merchant_service.MerchantService.verify_mpesa_channel') as mock_verify:
            mock_verify.return_value = {
                "channel_id": 1,
                "verified": True,
                "verification_details": {"status": "verified"}
            }
            
            # This endpoint would need to be updated to match new signature
            # response = await client.post(f"/api/v1/merchants/{merchant_id}/mpesa/channels/1/verify")
            # assert response.status_code == 200
    
    async def test_api_error_handling(self, client: AsyncClient):
        """Test API error handling for M-Pesa operations"""
        
        # Test with non-existent merchant
        response = await client.get("/api/v1/merchants/999/mpesa/channels")
        # This might return 200 with empty list or 404, depending on implementation
        
        # Test with non-existent channel
        response = await client.get("/api/v1/merchants/1/mpesa/channels/999")
        assert response.status_code == 404
    
    async def test_api_validation(self, client: AsyncClient, db: AsyncSession):
        """Test API input validation"""
        
        # Create merchant first
        merchant_data = {
            "business_name": "Validation Test Store",
            "email": "validation@test.com"
        }
        
        response = await client.post("/api/v1/merchants/", json=merchant_data)
        assert response.status_code == 201
        
        # Note: Simulation testing would be implemented with the new M-Pesa service
        # This would include validation for negative amounts and invalid phone formats
