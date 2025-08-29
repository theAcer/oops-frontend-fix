from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantUpdate

class MerchantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merchant(self, merchant_data: MerchantCreate) -> Merchant:
        """Create a new merchant"""
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
