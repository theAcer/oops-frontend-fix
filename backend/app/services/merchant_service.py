from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.models.merchant import Merchant
from app.models.mpesa_channel import MpesaChannel, ChannelStatus
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantUpdate
from app.services.mpesa_channel_service import MpesaChannelManagementService
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merchant(self, merchant_data: MerchantCreate) -> tuple[Merchant, bool]:
        """Create a new merchant (idempotent by email)."""
        # Check existing by email
        if merchant_data.email:
            existing_by_email = await self.db.execute(select(Merchant).where(Merchant.email == merchant_data.email))
            existing_merchant_by_email = existing_by_email.scalar_one_or_none()
            if existing_merchant_by_email:
                return existing_merchant_by_email, False
        
        # Check existing by mpesa_till_number if provided
        if merchant_data.mpesa_till_number:
            existing_by_till_number = await self.db.execute(
                select(Merchant).where(Merchant.mpesa_till_number == merchant_data.mpesa_till_number)
            )
            existing_merchant_by_till_number = existing_by_till_number.scalar_one_or_none()
            if existing_merchant_by_till_number:
                print("DEBUG: Duplicate till number detected, raising 409 HTTPException.") # Debug print
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate M-Pesa till number")

        merchant = Merchant(**merchant_data.model_dump())
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant, True

    async def get_merchant(self, merchant_id: int) -> Optional[Merchant]:
        """Get merchant by ID"""
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        return result.scalar_one_or_none()

    async def get_merchants(self, skip: int = 0, limit: int = 100) -> List[Merchant]:
        """Get all merchants with pagination"""
        result = await self.db.execute(
            select(Merchant).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_merchant(self, merchant_id: int, merchant_data: MerchantUpdate) -> Optional[Merchant]:
        """Update merchant"""
        merchant = await self.get_merchant(merchant_id)
        if not merchant:
            return None
        
        update_data = merchant_data.model_dump(exclude_unset=True)
        
        # Check for duplicate till number if it's being updated
        if "mpesa_till_number" in update_data and update_data["mpesa_till_number"] != merchant.mpesa_till_number:
            existing_by_till_number = await self.db.execute(
                select(Merchant).where(
                    Merchant.mpesa_till_number == update_data["mpesa_till_number"],
                    Merchant.id != merchant_id
                )
            )
            if existing_by_till_number.scalar_one_or_none():
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate M-Pesa till number")

        for field, value in update_data.items():
            setattr(merchant, field, value)
        
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def delete_merchant(self, merchant_id: int) -> bool:
        """Delete merchant"""
        merchant = await self.get_merchant(merchant_id)
        if not merchant:
            return False
        
        await self.db.delete(merchant)
        await self.db.commit()
        return True

    async def get_merchant_by_till_number(self, till_number: str) -> Optional[Merchant]:
        """Get merchant by M-Pesa till number"""
        result = await self.db.execute(
            select(Merchant).where(Merchant.mpesa_till_number == till_number)
        )
        return result.scalar_one_or_none()

    async def link_merchant_to_user(self, merchant_id: int, user_id: int) -> Optional[User]:
        """Link an existing merchant to a user."""
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return None
        
        # Check if user is already linked to a merchant
        if user.merchant_id is not None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already linked to a merchant")

        user.merchant_id = merchant_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ---- M-Pesa Channel Management (New Atomic Implementation) ----
    
    def _get_mpesa_service(self) -> MpesaChannelManagementService:
        """Get M-Pesa channel management service instance"""
        return MpesaChannelManagementService(self.db)
    
    async def get_mpesa_channel(self, merchant_id: int, channel_id: int) -> Optional[MpesaChannel]:
        """
        Get M-Pesa channel by ID for a specific merchant.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            
        Returns:
            MpesaChannel if found, None otherwise
        """
        try:
            mpesa_service = self._get_mpesa_service()
            await mpesa_service.get_channel(merchant_id, channel_id)
            
            # Convert response back to model for backward compatibility
            result = await self.db.execute(
                select(MpesaChannel).where(MpesaChannel.id == channel_id)
            )
            return result.scalar_one_or_none()
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting M-Pesa channel {channel_id} for merchant {merchant_id}: {e}")
            return None
    
    async def list_mpesa_channels(self, merchant_id: int) -> List[MpesaChannel]:
        """
        List all M-Pesa channels for a merchant.
        
        Args:
            merchant_id: ID of the merchant
            
        Returns:
            List of MpesaChannel objects
        """
        try:
            result = await self.db.execute(
                select(MpesaChannel)
                .where(MpesaChannel.merchant_id == merchant_id)
                .order_by(MpesaChannel.is_primary.desc(), MpesaChannel.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error listing M-Pesa channels for merchant {merchant_id}: {e}")
            return []
    
    async def verify_mpesa_channel(self, merchant_id: int, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Verify M-Pesa channel credentials with Safaricom API.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel to verify
            
        Returns:
            Verification result dictionary or None if failed
        """
        try:
            mpesa_service = self._get_mpesa_service()
            result = await mpesa_service.verify_channel(merchant_id, channel_id)
            
            logger.info(f"Channel verification result for {channel_id}: {result.get('verified', False)}")
            return result
        except Exception as e:
            logger.error(f"Error verifying M-Pesa channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "verified": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def register_mpesa_urls(
        self, 
        merchant_id: int, 
        channel_id: int,
        validation_url: str,
        confirmation_url: str,
        response_type: str = "Completed"
    ) -> Optional[Dict[str, Any]]:
        """
        Register validation and confirmation URLs for M-Pesa channel.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            validation_url: URL for transaction validation
            confirmation_url: URL for transaction confirmation
            response_type: Response type (Completed or Cancelled)
            
        Returns:
            Registration result dictionary or None if failed
        """
        try:
            mpesa_service = self._get_mpesa_service()
            result = await mpesa_service.register_urls(
                merchant_id=merchant_id,
                channel_id=channel_id,
                validation_url=validation_url,
                confirmation_url=confirmation_url,
                response_type=response_type
            )
            
            logger.info(f"URL registration result for channel {channel_id}: {result.get('registered', False)}")
            return result
        except Exception as e:
            logger.error(f"Error registering URLs for M-Pesa channel {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "registered": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def simulate_mpesa_transaction(
        self, 
        merchant_id: int,
        channel_id: int, 
        amount: float, 
        customer_phone: str, 
        bill_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate M-Pesa transaction for testing.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            amount: Transaction amount
            customer_phone: Customer phone number
            bill_ref: Bill reference (optional)
            
        Returns:
            Simulation result dictionary
            
        Raises:
            ValueError: If channel not found or not in sandbox
            ValidationError: If parameters are invalid
        """
        try:
            mpesa_service = self._get_mpesa_service()
            result = await mpesa_service.simulate_transaction(
                merchant_id=merchant_id,
                channel_id=channel_id,
                amount=amount,
                customer_phone=customer_phone,
                bill_ref=bill_ref
            )
            
            logger.info(f"Transaction simulation result for channel {channel_id}: {result.get('status')}")
            return result
        except Exception as e:
            logger.error(f"Error simulating transaction for channel {channel_id}: {e}")
            raise
    
    async def get_channel_status(self, merchant_id: int, channel_id: int) -> Dict[str, Any]:
        """
        Get comprehensive status of M-Pesa channel.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            
        Returns:
            Channel status dictionary
        """
        try:
            mpesa_service = self._get_mpesa_service()
            return await mpesa_service.get_channel_status(merchant_id, channel_id)
        except Exception as e:
            logger.error(f"Error getting channel status for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "last_checked": datetime.utcnow()
            }
    
    async def activate_channel(self, merchant_id: int, channel_id: int) -> Optional[MpesaChannel]:
        """
        Activate M-Pesa channel for live transactions.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            
        Returns:
            Updated MpesaChannel or None if failed
        """
        try:
            from app.schemas.mpesa_channel import MpesaChannelUpdate
            
            mpesa_service = self._get_mpesa_service()
            update_data = MpesaChannelUpdate(status=ChannelStatus.ACTIVE, is_active=True)
            await mpesa_service.update_channel(merchant_id, channel_id, update_data)
            
            # Return updated channel
            result = await self.db.execute(
                select(MpesaChannel).where(MpesaChannel.id == channel_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error activating channel {channel_id}: {e}")
            return None
    
    async def deactivate_channel(self, merchant_id: int, channel_id: int) -> Optional[MpesaChannel]:
        """
        Deactivate M-Pesa channel.
        
        Args:
            merchant_id: ID of the merchant
            channel_id: ID of the channel
            
        Returns:
            Updated MpesaChannel or None if failed
        """
        try:
            from app.schemas.mpesa_channel import MpesaChannelUpdate
            
            mpesa_service = self._get_mpesa_service()
            update_data = MpesaChannelUpdate(status=ChannelStatus.SUSPENDED, is_active=False)
            await mpesa_service.update_channel(merchant_id, channel_id, update_data)
            
            # Return updated channel
            result = await self.db.execute(
                select(MpesaChannel).where(MpesaChannel.id == channel_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error deactivating channel {channel_id}: {e}")
            return None