from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.merchant import Merchant
from app.models.user import User # Import User model
from app.schemas.merchant import MerchantCreate, MerchantUpdate

class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merchant(self, merchant_data: MerchantCreate) -> Merchant:
        """Create a new merchant (idempotent by email)."""
        # Check existing by email
        if merchant_data.email:
            existing = await self.db.execute(select(Merchant).where(Merchant.email == merchant_data.email))
            existing_merchant = existing.scalar_one_or_none()
            if existing_merchant:
                return existing_merchant
        merchant = Merchant(**merchant_data.model_dump())
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

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

    async def link_merchant_to_user(self, merchant_id: int, user_id: int) -> bool:
        """Link an existing merchant to a user."""
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return False
        
        user.merchant_id = merchant_id
        await self.db.commit()
        await self.db.refresh(user)
        return True