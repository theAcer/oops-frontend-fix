from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import List, Optional
from app.models.merchant import Merchant
from app.models.mpesa_channel import MpesaChannel
from app.schemas.mpesa_channel import MpesaChannelCreate, MpesaChannelUpdate
from app.models.user import User # Import User model
from app.schemas.merchant import MerchantCreate, MerchantUpdate

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

    # ---- Mpesa Channels (Phase 1) ----
    async def create_mpesa_channel(self, merchant_id: int, data: MpesaChannelCreate) -> MpesaChannel:
        channel = MpesaChannel(merchant_id=merchant_id, **data.model_dump())
        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel

    async def get_mpesa_channel(self, channel_id: int) -> Optional[MpesaChannel]:
        res = await self.db.execute(select(MpesaChannel).where(MpesaChannel.id == channel_id))
        return res.scalar_one_or_none()

    async def update_mpesa_channel(self, channel_id: int, data: MpesaChannelUpdate) -> Optional[MpesaChannel]:
        res = await self.db.execute(select(MpesaChannel).where(MpesaChannel.id == channel_id))
        channel = res.scalar_one_or_none()
        if not channel:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(channel, k, v)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel

    async def list_mpesa_channels(self, merchant_id: int) -> list[MpesaChannel]:
        res = await self.db.execute(select(MpesaChannel).where(MpesaChannel.merchant_id == merchant_id))
        return res.scalars().all()

    # ---- Mpesa Channels (Phase 2) ----
    async def verify_mpesa_channel(self, channel_id: int) -> Optional[MpesaChannel]:
        """Verify M-Pesa channel by testing OAuth token generation"""
        from app.services.mpesa_service_refactored import MpesaServiceFactory

        channel = await self.get_mpesa_channel(channel_id)
        if not channel:
            return None

        if not channel.consumer_key or not channel.consumer_secret:
            return None

        try:
            # Use refactored service
            mpesa_service = MpesaServiceFactory.create_channel_service(
                consumer_key=channel.consumer_key,
                consumer_secret=channel.consumer_secret,
                environment=channel.environment
            )

            # Test OAuth token generation and basic connectivity
            result = await mpesa_service.verify_channel(channel.shortcode)

            if result.get("status") == "verified":
                # Update channel status to verified
                channel.status = "verified"
                await self.db.commit()
                await self.db.refresh(channel)
                return channel
            else:
                return None

        except Exception as e:
            print(f"Error verifying channel {channel_id}: {e}")
            return None
        finally:
            await mpesa_service.close()

    async def register_mpesa_urls(self, channel_id: int) -> Optional[MpesaChannel]:
        """Register validation and confirmation URLs with M-Pesa"""
        from app.services.mpesa_service_refactored import MpesaServiceFactory

        channel = await self.get_mpesa_channel(channel_id)
        if not channel:
            return None

        if channel.status != "verified":
            return None

        try:
            mpesa_service = MpesaServiceFactory.create_channel_service(
                consumer_key=channel.consumer_key,
                consumer_secret=channel.consumer_secret,
                environment=channel.environment
            )

            # Register URLs
            result = await mpesa_service.register_urls(
                shortcode=channel.shortcode,
                response_type=channel.response_type,
                confirmation_url=channel.confirmation_url,
                validation_url=channel.validation_url
            )

            if result and result.get("ResponseCode") == "0":
                # Update channel status to urls_registered
                channel.status = "urls_registered"
                channel.last_registration_at = func.now()
                await self.db.commit()
                await self.db.refresh(channel)
                return channel
            else:
                return None

        except Exception as e:
            print(f"Error registering URLs for channel {channel_id}: {e}")
            return None
        finally:
            await mpesa_service.close()

    async def simulate_mpesa_transaction(self, channel_id: int, amount: float, customer_phone: str, bill_ref: str = None) -> dict:
        """Simulate an M-Pesa transaction for testing"""
        from app.services.mpesa_service_refactored import MpesaServiceFactory

        channel = await self.get_mpesa_channel(channel_id)
        if not channel:
            raise ValueError("Channel not found")

        if channel.environment != "sandbox":
            raise ValueError("Simulation only available in sandbox environment")

        try:
            mpesa_service = MpesaServiceFactory.create_channel_service(
                consumer_key=channel.consumer_key,
                consumer_secret=channel.consumer_secret,
                environment=channel.environment
            )

            # Simulate transaction
            result = await mpesa_service.simulate_transaction(
                shortcode=channel.shortcode,
                amount=amount,
                msisdn=customer_phone,
                bill_ref_number=bill_ref
            )

            return result

        except Exception as e:
            print(f"Error simulating transaction for channel {channel_id}: {e}")
            raise
        finally:
            await mpesa_service.close()