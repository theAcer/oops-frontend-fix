from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.core.security import encrypt_data, decrypt_data
from enum import Enum
from typing import Optional, Dict, Any


class ChannelType(str, Enum):
    """M-Pesa channel types"""
    PAYBILL = "paybill"
    TILL = "till"
    BUYGOODS = "buygoods"


class ChannelEnvironment(str, Enum):
    """M-Pesa environments"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class ChannelStatus(str, Enum):
    """M-Pesa channel status"""
    DRAFT = "draft"                    # Initial state, not configured
    CONFIGURED = "configured"          # Credentials added
    VERIFIED = "verified"              # Channel verified with Safaricom
    URLS_REGISTERED = "urls_registered" # URLs registered
    ACTIVE = "active"                  # Fully operational
    SUSPENDED = "suspended"            # Temporarily disabled
    ERROR = "error"                    # Configuration error


class MpesaChannel(Base):
    """
    M-Pesa Channel Model for Multi-Tenant Loyalty Platform
    
    Supports:
    - Multiple channels per merchant
    - Different channel types (PayBill, Till, Buy Goods)
    - Account number mapping for PayBills
    - Secure credential encryption
    - Channel status tracking
    """
    __tablename__ = "mpesa_channels"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Channel identification
    name = Column(String(100), nullable=False)  # Friendly name (e.g., "Main PayBill", "Shop Till")
    shortcode = Column(String(20), nullable=False, index=True)
    channel_type = Column(SQLEnum(ChannelType), nullable=False)
    environment = Column(SQLEnum(ChannelEnvironment), nullable=False, default=ChannelEnvironment.SANDBOX)

    # Encrypted credentials (never store in plain text)
    consumer_key_encrypted = Column(Text, nullable=True)
    consumer_secret_encrypted = Column(Text, nullable=True)
    passkey_encrypted = Column(Text, nullable=True)  # For STK Push

    # PayBill specific: Account number mapping
    account_mapping = Column(JSON, nullable=True)  # {"default": "loyalty", "VIP001": "vip_account"}
    
    # URL configuration
    validation_url = Column(String(512), nullable=True)
    confirmation_url = Column(String(512), nullable=True)
    callback_url = Column(String(512), nullable=True)  # For STK Push
    response_type = Column(String(20), nullable=False, default="Completed")

    # Status and metadata
    status = Column(SQLEnum(ChannelStatus), nullable=False, default=ChannelStatus.DRAFT)
    is_active = Column(Boolean, nullable=False, default=True)
    is_primary = Column(Boolean, nullable=False, default=False)  # Primary channel for merchant
    
    # Verification and registration tracking
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_registration_at = Column(DateTime(timezone=True), nullable=True)
    verification_response = Column(JSON, nullable=True)  # Store verification details
    
    # Configuration metadata
    config_metadata = Column(JSON, nullable=True)  # Additional configuration
    error_details = Column(JSON, nullable=True)    # Error information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    merchant = relationship("Merchant", back_populates="mpesa_channels")
    transactions = relationship("Transaction", back_populates="mpesa_channel")

    # Hybrid properties for secure credential access
    @hybrid_property
    def consumer_key(self) -> Optional[str]:
        """Decrypt and return consumer key"""
        if self.consumer_key_encrypted:
            return decrypt_data(self.consumer_key_encrypted)
        return None

    @consumer_key.setter
    def consumer_key(self, value: Optional[str]):
        """Encrypt and store consumer key"""
        if value:
            self.consumer_key_encrypted = encrypt_data(value)
        else:
            self.consumer_key_encrypted = None

    @hybrid_property
    def consumer_secret(self) -> Optional[str]:
        """Decrypt and return consumer secret"""
        if self.consumer_secret_encrypted:
            return decrypt_data(self.consumer_secret_encrypted)
        return None

    @consumer_secret.setter
    def consumer_secret(self, value: Optional[str]):
        """Encrypt and store consumer secret"""
        if value:
            self.consumer_secret_encrypted = encrypt_data(value)
        else:
            self.consumer_secret_encrypted = None

    @hybrid_property
    def passkey(self) -> Optional[str]:
        """Decrypt and return passkey"""
        if self.passkey_encrypted:
            return decrypt_data(self.passkey_encrypted)
        return None

    @passkey.setter
    def passkey(self, value: Optional[str]):
        """Encrypt and store passkey"""
        if value:
            self.passkey_encrypted = encrypt_data(value)
        else:
            self.passkey_encrypted = None

    def get_account_for_reference(self, bill_ref: str) -> str:
        """
        Get account mapping for bill reference.
        
        For PayBill channels, different account references can map to different
        loyalty program accounts or customer segments.
        """
        if not self.account_mapping:
            return "default"
        
        # Check for exact match first
        if bill_ref in self.account_mapping:
            return self.account_mapping[bill_ref]
        
        # Check for pattern matches (e.g., VIP* -> vip_account)
        for pattern, account in self.account_mapping.items():
            if "*" in pattern:
                pattern_prefix = pattern.replace("*", "")
                if bill_ref.startswith(pattern_prefix):
                    return account
        
        # Return default account
        return self.account_mapping.get("default", "default")

    def is_configured(self) -> bool:
        """Check if channel has minimum required configuration"""
        return (
            self.consumer_key is not None and
            self.consumer_secret is not None and
            self.shortcode is not None
        )

    def is_ready_for_transactions(self) -> bool:
        """Check if channel is ready to process transactions"""
        return (
            self.is_configured() and
            self.status == ChannelStatus.ACTIVE and
            self.is_active
        )

    def get_credentials_dict(self) -> Dict[str, Any]:
        """Get decrypted credentials as dictionary for service initialization"""
        return {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "shortcode": self.shortcode,
            "passkey": self.passkey,
            "environment": self.environment.value,
            "channel_type": self.channel_type.value
        }

    def __repr__(self):
        return f"<MpesaChannel(id={self.id}, merchant_id={self.merchant_id}, name='{self.name}', shortcode='{self.shortcode}', type='{self.channel_type.value}')>"


