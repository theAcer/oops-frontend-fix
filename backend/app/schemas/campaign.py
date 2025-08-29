from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.campaign import CampaignType, CampaignStatus, TargetAudience

class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: CampaignType
    target_audience: TargetAudience
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    points_multiplier: Optional[float] = Field(None, ge=1)
    minimum_spend: float = Field(default=0.0, ge=0)
    sms_message: Optional[str] = None
    send_sms: bool = True

class CampaignCreate(CampaignBase):
    merchant_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    minimum_spend: Optional[float] = None
    sms_message: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignResponse(CampaignBase):
    id: int
    merchant_id: int
    status: CampaignStatus
    custom_segment_criteria: Optional[str]
    maximum_discount: Optional[float]
    usage_limit_per_customer: Optional[int]
    total_usage_limit: Optional[int]
    current_usage_count: int
    target_customers_count: int
    reached_customers_count: int
    conversion_count: int
    total_revenue_generated: float
    sms_sent_count: int
    created_at: datetime
    launched_at: Optional[datetime]

    class Config:
        from_attributes = True
