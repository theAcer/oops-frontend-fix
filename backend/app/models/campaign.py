from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class CampaignType(str, enum.Enum):
    DISCOUNT = "discount"
    POINTS_BONUS = "points_bonus"
    FREE_ITEM = "free_item"
    CASHBACK = "cashback"
    REFERRAL = "referral"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TargetAudience(str, enum.Enum):
    ALL_CUSTOMERS = "all_customers"
    NEW_CUSTOMERS = "new_customers"
    REGULAR_CUSTOMERS = "regular_customers"
    VIP_CUSTOMERS = "vip_customers"
    AT_RISK_CUSTOMERS = "at_risk_customers"
    CHURNED_CUSTOMERS = "churned_customers"
    CUSTOM_SEGMENT = "custom_segment"

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Campaign Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Targeting
    target_audience = Column(Enum(TargetAudience), nullable=False)
    custom_segment_criteria = Column(Text, nullable=True)  # JSON string for custom targeting
    
    # Campaign Rules
    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    points_multiplier = Column(Float, nullable=True)
    minimum_spend = Column(Float, default=0.0)
    maximum_discount = Column(Float, nullable=True)
    
    # Usage Limits
    usage_limit_per_customer = Column(Integer, nullable=True)
    total_usage_limit = Column(Integer, nullable=True)
    current_usage_count = Column(Integer, default=0)
    
    # Scheduling
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # SMS/Communication
    sms_message = Column(Text, nullable=True)
    send_sms = Column(Boolean, default=True)
    sms_sent_count = Column(Integer, default=0)
    
    # Performance Tracking
    target_customers_count = Column(Integer, default=0)
    reached_customers_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    total_revenue_generated = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    launched_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    merchant = relationship("Merchant", back_populates="campaigns")
    rewards = relationship("Reward", back_populates="campaign")

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Reward Details
    reward_type = Column(String(50), nullable=False)  # points, discount, free_item, cashback
    points_awarded = Column(Integer, default=0)
    discount_amount = Column(Float, default=0.0)
    cashback_amount = Column(Float, default=0.0)
    
    # Status
    is_redeemed = Column(Boolean, default=False)
    redeemed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    reference_code = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="rewards")
    transaction = relationship("Transaction", back_populates="rewards")
    campaign = relationship("Campaign", back_populates="rewards")
