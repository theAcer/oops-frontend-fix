from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MpesaChannel(Base):
    __tablename__ = "mpesa_channels"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    shortcode = Column(String(20), nullable=False, index=True)
    channel_type = Column(String(20), nullable=False)  # paybill | till
    environment = Column(String(20), nullable=False, default="sandbox")  # sandbox | production

    consumer_key = Column(String(255), nullable=True)
    consumer_secret = Column(String(255), nullable=True)

    validation_url = Column(String(512), nullable=True)
    confirmation_url = Column(String(512), nullable=True)
    response_type = Column(String(20), nullable=False, default="Completed")  # Completed | Cancelled

    status = Column(String(50), nullable=False, default="unverified")  # unverified | verified | urls_registered | receiving
    last_registration_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    merchant = relationship("Merchant", back_populates="mpesa_channels")


