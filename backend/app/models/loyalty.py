from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class LoyaltyProgramType(str, enum.Enum):
    POINTS = "points"  # Earn points per purchase
    VISITS = "visits"  # Visit-based (buy 5 get 1 free)
    SPEND = "spend"    # Spend-based tiers
    HYBRID = "hybrid"  # Combination

class LoyaltyProgram(Base):
    __tablename__ = "loyalty_programs"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Program Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    program_type = Column(Enum(LoyaltyProgramType), nullable=False)
    
    # Program Rules
    points_per_currency = Column(Float, default=1.0)  # Points earned per currency unit
    minimum_spend = Column(Float, default=0.0)  # Minimum spend to earn points
    
    # Visit-based rules
    visits_required = Column(Integer, nullable=True)  # For visit-based programs
    reward_visits = Column(Integer, nullable=True)    # Free visits earned
    
    # Tier Configuration
    bronze_threshold = Column(Float, default=0.0)
    silver_threshold = Column(Float, default=1000.0)
    gold_threshold = Column(Float, default=5000.0)
    platinum_threshold = Column(Float, default=10000.0)
    
    # Tier Multipliers
    bronze_multiplier = Column(Float, default=1.0)
    silver_multiplier = Column(Float, default=1.2)
    gold_multiplier = Column(Float, default=1.5)
    platinum_multiplier = Column(Float, default=2.0)
    
    # Program Status
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="loyalty_programs")
    customer_loyalty = relationship("CustomerLoyalty", back_populates="loyalty_program")

class CustomerLoyalty(Base):
    __tablename__ = "customer_loyalty"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey("loyalty_programs.id"), nullable=False)
    
    # Current Status
    current_points = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    current_tier = Column(String(50), default="bronze")
    
    # Visit Tracking (for visit-based programs)
    current_visits = Column(Integer, default=0)
    total_visits = Column(Integer, default=0)
    
    # Progress Tracking
    points_to_next_tier = Column(Integer, default=0)
    tier_progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)
    tier_achieved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="loyalty_records")
    loyalty_program = relationship("LoyaltyProgram", back_populates="customer_loyalty")
