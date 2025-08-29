from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    customer_segment: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    marketing_consent: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    merchant_id: int
    customer_segment: str
    total_spent: float
    total_transactions: int
    average_order_value: float
    first_purchase_date: Optional[datetime]
    last_purchase_date: Optional[datetime]
    purchase_frequency_days: Optional[float]
    loyalty_points: int
    loyalty_tier: str
    churn_risk_score: float
    lifetime_value_prediction: float
    next_purchase_prediction: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CustomerLoyaltyStatus(BaseModel):
    customer_id: int
    loyalty_points: int
    loyalty_tier: str
    points_to_next_tier: int
    tier_progress_percentage: float
    current_visits: int
    rewards_available: int
    churn_risk_score: float
