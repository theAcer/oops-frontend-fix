from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    
    # Customer Identity (from M-Pesa transactions)
    phone = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Customer Segmentation
    customer_segment = Column(String(50), default="new")  # new, regular, vip, at_risk, churned
    total_spent = Column(Float, default=0.0)
    total_transactions = Column(Integer, default=0)
    average_order_value = Column(Float, default=0.0)
    
    # Behavioral Data
    first_purchase_date = Column(DateTime(timezone=True), nullable=True)
    last_purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_frequency_days = Column(Float, nullable=True)  # Average days between purchases
    
    # Loyalty Status
    loyalty_points = Column(Integer, default=0)
    loyalty_tier = Column(String(50), default="bronze")  # bronze, silver, gold, platinum
    
    # Preferences
    preferred_contact_method = Column(String(20), default="sms")  # sms, email, whatsapp
    marketing_consent = Column(Boolean, default=True)
    
    # AI/ML Features
    churn_risk_score = Column(Float, default=0.0)  # 0-1 probability of churning
    lifetime_value_prediction = Column(Float, default=0.0)
    next_purchase_prediction = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
    loyalty_records = relationship("CustomerLoyalty", back_populates="customer")
    rewards = relationship("Reward", back_populates="customer")
