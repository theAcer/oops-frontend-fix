from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class BusinessType(str, enum.Enum):
    RESTAURANT = "restaurant"
    SALON = "salon"
    RETAIL = "retail"
    SERVICE = "service"
    OTHER = "other"

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), nullable=False, index=True)
    owner_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    business_type = Column(Enum(BusinessType), nullable=False)
    
    # M-Pesa Integration
    mpesa_till_number = Column(String(20), unique=True, index=True, nullable=False)
    mpesa_store_number = Column(String(20), nullable=True)
    
    # Daraja API Credentials (for merchant-specific integration)
    daraja_consumer_key = Column(String(255), nullable=True)
    daraja_consumer_secret = Column(String(255), nullable=True)
    daraja_shortcode = Column(String(20), nullable=True)
    daraja_passkey = Column(String(255), nullable=True)
    
    # Business Details
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Kenya")
    
    # Platform Settings
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="basic")  # basic, premium, enterprise
    
    # Daraaa API Integration
    daraaa_merchant_id = Column(String(100), nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customers = relationship("Customer", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")
    loyalty_programs = relationship("LoyaltyProgram", back_populates="merchant")
    campaigns = relationship("Campaign", back_populates="merchant")
    users = relationship("User", back_populates="merchant") # Added this line