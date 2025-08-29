from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class NotificationType(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    PROMOTIONAL = "promotional"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Notification Details
    notification_type = Column(Enum(NotificationType), nullable=False)
    recipient = Column(String(255), nullable=False)  # phone, email, etc.
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    
    # Status Tracking
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Provider Details
    provider = Column(String(50), nullable=True)  # africastalking, twilio, etc.
    provider_message_id = Column(String(255), nullable=True)
    provider_response = Column(Text, nullable=True)
    
    # Cost Tracking
    cost = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer")
    campaign = relationship("Campaign")
