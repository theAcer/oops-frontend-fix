"""
M-Pesa Channel Management Service

Handles CRUD operations and business logic for M-Pesa channels in the multi-tenant loyalty platform.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from app.models.mpesa_channel import MpesaChannel, ChannelStatus, ChannelType
from app.models.merchant import Merchant
from app.schemas.mpesa_channel import (
    MpesaChannelCreate,
    MpesaChannelUpdate,
    MpesaChannelResponse,
    MpesaChannelListResponse
)
from app.services.mpesa import MpesaServiceFactory, MpesaChannelService as UnifiedChannelService
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError

logger = logging.getLogger(__name__)


class MpesaChannelManagementService:
    """
    Service for managing M-Pesa channels for merchants.
    
    This service handles:
    - Channel CRUD operations
    - Credential encryption/decryption
    - Channel verification with Safaricom
    - URL registration
    - Transaction simulation
    - Multi-channel management per merchant
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_channel(
        self,
        merchant_id: int,
        channel_data: MpesaChannelCreate
    ) -> MpesaChannelResponse:
        """
        Create a new M-Pesa channel for a merchant.
        
        Args:
            merchant_id: ID of the merchant
            channel_data: Channel creation data
            
        Returns:
            Created channel response
            
        Raises:
            NotFoundError: If merchant not found
            ValidationError: If validation fails
            BusinessLogicError: If business rules violated
        """
        # Verify merchant exists
        merchant = await self._get_merchant(merchant_id)
        
        # Validate unique shortcode per merchant
        await self._validate_unique_shortcode(merchant_id, channel_data.shortcode)
        
        # Create channel instance
        channel = MpesaChannel(
            merchant_id=merchant_id,
            name=channel_data.name,
            shortcode=channel_data.shortcode,
            channel_type=channel_data.channel_type,
            environment=channel_data.environment,
            response_type=channel_data.response_type,
            validation_url=str(channel_data.validation_url) if channel_data.validation_url else None,
            confirmation_url=str(channel_data.confirmation_url) if channel_data.confirmation_url else None,
            callback_url=str(channel_data.callback_url) if channel_data.callback_url else None,
            account_mapping=channel_data.account_mapping,
            config_metadata=channel_data.config_metadata,
            is_primary=channel_data.is_primary,
            status=ChannelStatus.DRAFT
        )
        
        # Set encrypted credentials
        channel.consumer_key = channel_data.consumer_key
        channel.consumer_secret = channel_data.consumer_secret
        if channel_data.passkey:
            channel.passkey = channel_data.passkey
        
        # Update status based on configuration
        if channel.is_configured():
            channel.status = ChannelStatus.CONFIGURED
        
        # Handle primary channel logic
        if channel_data.is_primary:
            await self._ensure_single_primary_channel(merchant_id)
        
        # Save to database
        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)
        
        logger.info(f"Created M-Pesa channel {channel.id} for merchant {merchant_id}")
        
        return MpesaChannelResponse.from_orm(channel)
    
    async def get_channel(
        self,
        merchant_id: int,
        channel_id: int
    ) -> MpesaChannelResponse:
        """Get a specific M-Pesa channel"""
        channel = await self._get_channel(merchant_id, channel_id)
        return MpesaChannelResponse.from_orm(channel)
    
    async def list_channels(
        self,
        merchant_id: int,
        page: int = 1,
        per_page: int = 20,
        channel_type: Optional[ChannelType] = None,
        status: Optional[ChannelStatus] = None,
        is_active: Optional[bool] = None
    ) -> MpesaChannelListResponse:
        """List M-Pesa channels for a merchant with filtering"""
        # Verify merchant exists
        await self._get_merchant(merchant_id)
        
        # Build query
        query = select(MpesaChannel).where(MpesaChannel.merchant_id == merchant_id)
        
        # Apply filters
        if channel_type:
            query = query.where(MpesaChannel.channel_type == channel_type)
        if status:
            query = query.where(MpesaChannel.status == status)
        if is_active is not None:
            query = query.where(MpesaChannel.is_active == is_active)
        
        # Add ordering
        query = query.order_by(MpesaChannel.is_primary.desc(), MpesaChannel.created_at.desc())
        
        # Count total
        count_query = select(MpesaChannel.id).where(MpesaChannel.merchant_id == merchant_id)
        if channel_type:
            count_query = count_query.where(MpesaChannel.channel_type == channel_type)
        if status:
            count_query = count_query.where(MpesaChannel.status == status)
        if is_active is not None:
            count_query = count_query.where(MpesaChannel.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = len(total_result.all())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        result = await self.db.execute(query)
        channels = result.scalars().all()
        
        return MpesaChannelListResponse(
            channels=[MpesaChannelResponse.from_orm(channel) for channel in channels],
            total=total,
            page=page,
            per_page=per_page
        )
    
    async def update_channel(
        self,
        merchant_id: int,
        channel_id: int,
        update_data: MpesaChannelUpdate
    ) -> MpesaChannelResponse:
        """Update an M-Pesa channel"""
        channel = await self._get_channel(merchant_id, channel_id)
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        # Handle shortcode uniqueness
        if 'shortcode' in update_dict and update_dict['shortcode'] != channel.shortcode:
            await self._validate_unique_shortcode(merchant_id, update_dict['shortcode'], exclude_id=channel_id)
        
        # Handle primary channel logic
        if update_dict.get('is_primary') and not channel.is_primary:
            await self._ensure_single_primary_channel(merchant_id, exclude_id=channel_id)
        
        # Update credentials if provided
        if 'consumer_key' in update_dict:
            channel.consumer_key = update_dict.pop('consumer_key')
        if 'consumer_secret' in update_dict:
            channel.consumer_secret = update_dict.pop('consumer_secret')
        if 'passkey' in update_dict:
            channel.passkey = update_dict.pop('passkey')
        
        # Update other fields
        for field, value in update_dict.items():
            if hasattr(channel, field):
                setattr(channel, field, value)
        
        # Update status based on configuration
        if channel.is_configured() and channel.status == ChannelStatus.DRAFT:
            channel.status = ChannelStatus.CONFIGURED
        
        await self.db.commit()
        await self.db.refresh(channel)
        
        logger.info(f"Updated M-Pesa channel {channel_id} for merchant {merchant_id}")
        
        return MpesaChannelResponse.from_orm(channel)
    
    async def delete_channel(self, merchant_id: int, channel_id: int) -> bool:
        """Delete an M-Pesa channel"""
        channel = await self._get_channel(merchant_id, channel_id)
        
        # Check if channel has active transactions (business rule)
        # This would require checking the transactions table
        # For now, we'll allow deletion but log it
        
        await self.db.delete(channel)
        await self.db.commit()
        
        logger.info(f"Deleted M-Pesa channel {channel_id} for merchant {merchant_id}")
        
        return True
    
    async def verify_channel(
        self,
        merchant_id: int,
        channel_id: int
    ) -> Dict[str, Any]:
        """
        Verify M-Pesa channel with Safaricom API.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel to verify
            
        Returns:
            Verification result
        """
        channel = await self._get_channel(merchant_id, channel_id)
        
        if not channel.is_configured():
            raise ValidationError("Channel is not properly configured")
        
        try:
            # Create M-Pesa service with channel credentials
            credentials = channel.get_credentials_dict()
            mpesa_service = MpesaServiceFactory.create_channel_service(**credentials)
            
            # Verify channel
            verification_result = await mpesa_service.verify_channel(channel.shortcode)
            
            # Update channel status
            channel.status = ChannelStatus.VERIFIED
            channel.last_verified_at = datetime.utcnow()
            channel.verification_response = verification_result
            channel.error_details = None
            
            await self.db.commit()
            await mpesa_service.close()
            
            logger.info(f"Successfully verified M-Pesa channel {channel_id}")
            
            return {
                "channel_id": channel_id,
                "verified": True,
                "verification_details": verification_result,
                "verified_at": channel.last_verified_at
            }
            
        except Exception as e:
            # Update channel with error
            channel.status = ChannelStatus.ERROR
            channel.error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.db.commit()
            
            logger.error(f"Failed to verify M-Pesa channel {channel_id}: {e}")
            
            return {
                "channel_id": channel_id,
                "verified": False,
                "error": str(e),
                "error_details": channel.error_details
            }
    
    async def register_urls(
        self,
        merchant_id: int,
        channel_id: int,
        validation_url: str,
        confirmation_url: str,
        response_type: str = "Completed"
    ) -> Dict[str, Any]:
        """Register validation and confirmation URLs for a channel"""
        channel = await self._get_channel(merchant_id, channel_id)
        
        if channel.status != ChannelStatus.VERIFIED:
            raise BusinessLogicError("Channel must be verified before registering URLs")
        
        try:
            # Create M-Pesa service
            credentials = channel.get_credentials_dict()
            mpesa_service = MpesaServiceFactory.create_channel_service(**credentials)
            
            # Register URLs
            registration_result = await mpesa_service.register_urls(
                shortcode=channel.shortcode,
                validation_url=validation_url,
                confirmation_url=confirmation_url,
                response_type=response_type
            )
            
            # Update channel
            channel.status = ChannelStatus.URLS_REGISTERED
            channel.validation_url = validation_url
            channel.confirmation_url = confirmation_url
            channel.response_type = response_type
            channel.last_registration_at = datetime.utcnow()
            
            await self.db.commit()
            await mpesa_service.close()
            
            logger.info(f"Successfully registered URLs for M-Pesa channel {channel_id}")
            
            return {
                "channel_id": channel_id,
                "registered": True,
                "registration_details": registration_result,
                "registered_at": channel.last_registration_at
            }
            
        except Exception as e:
            channel.status = ChannelStatus.ERROR
            channel.error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.db.commit()
            
            logger.error(f"Failed to register URLs for M-Pesa channel {channel_id}: {e}")
            
            return {
                "channel_id": channel_id,
                "registered": False,
                "error": str(e)
            }
    
    async def simulate_transaction(
        self,
        merchant_id: int,
        channel_id: int,
        amount: float,
        customer_phone: str,
        bill_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simulate a C2B transaction for testing"""
        channel = await self._get_channel(merchant_id, channel_id)
        
        if not channel.is_ready_for_transactions():
            raise BusinessLogicError("Channel is not ready for transactions")
        
        try:
            # Create M-Pesa transaction service
            credentials = channel.get_credentials_dict()
            mpesa_service = MpesaServiceFactory.create_transaction_service(**credentials)
            
            # Generate bill reference if not provided
            if not bill_ref:
                bill_ref = f"SIM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Simulate transaction
            simulation_result = await mpesa_service.simulate_c2b_transaction(
                shortcode=channel.shortcode,
                amount=amount,
                customer_phone=customer_phone,
                bill_ref=bill_ref
            )
            
            await mpesa_service.close()
            
            logger.info(f"Successfully simulated transaction for channel {channel_id}")
            
            return {
                "channel_id": channel_id,
                "simulation_id": simulation_result.get("conversation_id"),
                "status": "success",
                "amount": amount,
                "customer_phone": customer_phone,
                "bill_ref": bill_ref,
                "response_details": simulation_result,
                "simulated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to simulate transaction for channel {channel_id}: {e}")
            
            return {
                "channel_id": channel_id,
                "status": "failed",
                "error": str(e),
                "simulated_at": datetime.utcnow()
            }
    
    async def get_channel_status(
        self,
        merchant_id: int,
        channel_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive status of a channel"""
        channel = await self._get_channel(merchant_id, channel_id)
        
        return {
            "channel_id": channel_id,
            "shortcode": channel.shortcode,
            "status": channel.status,
            "is_active": channel.is_active,
            "is_configured": channel.is_configured(),
            "is_ready_for_transactions": channel.is_ready_for_transactions(),
            "last_checked": datetime.utcnow(),
            "health_details": {
                "has_credentials": channel.consumer_key is not None,
                "has_urls": channel.validation_url is not None,
                "last_verified": channel.last_verified_at,
                "last_registration": channel.last_registration_at,
                "error_details": channel.error_details
            }
        }
    
    # Private helper methods
    
    async def _get_merchant(self, merchant_id: int) -> Merchant:
        """Get merchant by ID or raise NotFoundError"""
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = result.scalar_one_or_none()
        
        if not merchant:
            raise NotFoundError(f"Merchant {merchant_id} not found")
        
        return merchant
    
    async def _get_channel(self, merchant_id: int, channel_id: int) -> MpesaChannel:
        """Get channel by ID and merchant ID or raise NotFoundError"""
        result = await self.db.execute(
            select(MpesaChannel).where(
                and_(
                    MpesaChannel.id == channel_id,
                    MpesaChannel.merchant_id == merchant_id
                )
            )
        )
        channel = result.scalar_one_or_none()
        
        if not channel:
            raise NotFoundError(f"M-Pesa channel {channel_id} not found for merchant {merchant_id}")
        
        return channel
    
    async def _validate_unique_shortcode(
        self,
        merchant_id: int,
        shortcode: str,
        exclude_id: Optional[int] = None
    ):
        """Validate that shortcode is unique for merchant"""
        query = select(MpesaChannel).where(
            and_(
                MpesaChannel.merchant_id == merchant_id,
                MpesaChannel.shortcode == shortcode
            )
        )
        
        if exclude_id:
            query = query.where(MpesaChannel.id != exclude_id)
        
        result = await self.db.execute(query)
        existing_channel = result.scalar_one_or_none()
        
        if existing_channel:
            raise ValidationError(f"Shortcode {shortcode} already exists for this merchant")
    
    async def _ensure_single_primary_channel(
        self,
        merchant_id: int,
        exclude_id: Optional[int] = None
    ):
        """Ensure only one primary channel per merchant"""
        query = select(MpesaChannel).where(
            and_(
                MpesaChannel.merchant_id == merchant_id,
                MpesaChannel.is_primary == True
            )
        )
        
        if exclude_id:
            query = query.where(MpesaChannel.id != exclude_id)
        
        result = await self.db.execute(query)
        existing_primary = result.scalar_one_or_none()
        
        if existing_primary:
            existing_primary.is_primary = False
