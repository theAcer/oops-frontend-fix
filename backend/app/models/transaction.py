from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"

class TransactionType(str, enum.Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    REVERSAL = "reversal"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    mpesa_channel_id = Column(Integer, ForeignKey("mpesa_channels.id"), nullable=True) # Added foreign key to mpesa_channels
    
    # M-Pesa Transaction Details
    mpesa_receipt_number = Column(String(50), unique=True, index=True, nullable=False)
    mpesa_transaction_id = Column(String(100), nullable=True)
    till_number = Column(String(20), nullable=False)
    
    # Transaction Data
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), default=TransactionType.PAYMENT)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED)
    
    # Customer Information (from M-Pesa)
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(255), nullable=True)
    
    # Transaction Metadata
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    # Daraaa API Data
    daraaa_transaction_id = Column(String(100), nullable=True)
    raw_daraaa_data = Column(Text, nullable=True)  # JSON string of raw API response
    
    # Loyalty Processing
    loyalty_points_earned = Column(Integer, default=0)
    loyalty_processed = Column(Boolean, default=False)
    loyalty_processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
    rewards = relationship("Reward", back_populates="transaction")
    mpesa_channel = relationship("MpesaChannel", back_populates="transactions") # Added relationship