from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.loyalty import LoyaltyProgramType

class LoyaltyProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    program_type: LoyaltyProgramType
    points_per_currency: float = Field(default=1.0, ge=0)
    minimum_spend: float = Field(default=0.0, ge=0)
    visits_required: Optional[int] = Field(None, ge=1)
    reward_visits: Optional[int] = Field(None, ge=1)

class LoyaltyProgramCreate(LoyaltyProgramBase):
    merchant_id: int

class LoyaltyProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_per_currency: Optional[float] = None
    minimum_spend: Optional[float] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class LoyaltyProgramResponse(LoyaltyProgramBase):
    id: int
    merchant_id: int
    bronze_threshold: float
    silver_threshold: float
    gold_threshold: float
    platinum_threshold: float
    bronze_multiplier: float
    silver_multiplier: float
    gold_multiplier: float
    platinum_multiplier: float
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class RewardCalculationResult(BaseModel):
    points_earned: int
    tier_multiplier: float
    bonus_points: int
    total_points: int
    new_tier: Optional[str]
    tier_upgraded: bool
