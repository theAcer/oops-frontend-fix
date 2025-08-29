from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.merchant import BusinessType

class MerchantBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    business_type: BusinessType
    mpesa_till_number: str = Field(..., min_length=5, max_length=20)
    mpesa_store_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Kenya"

class MerchantCreate(MerchantBase):
    pass

class MerchantUpdate(BaseModel):
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    business_type: Optional[BusinessType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None

class MerchantResponse(MerchantBase):
    id: int
    is_active: bool
    subscription_tier: str
    daraaa_merchant_id: Optional[str]
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
