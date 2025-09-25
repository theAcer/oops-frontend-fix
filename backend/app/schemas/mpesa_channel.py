from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ChannelTypeEnum(str, Enum):
    """M-Pesa channel types"""
    PAYBILL = "paybill"
    TILL = "till"
    BUYGOODS = "buygoods"


class ChannelEnvironmentEnum(str, Enum):
    """M-Pesa environments"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class ChannelStatusEnum(str, Enum):
    """M-Pesa channel status"""
    DRAFT = "draft"
    CONFIGURED = "configured"
    VERIFIED = "verified"
    URLS_REGISTERED = "urls_registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"


class MpesaChannelBase(BaseModel):
    """Base M-Pesa channel schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Friendly name for the channel")
    shortcode: str = Field(..., min_length=5, max_length=20, description="M-Pesa shortcode")
    channel_type: ChannelTypeEnum = Field(..., description="Type of M-Pesa channel")
    environment: ChannelEnvironmentEnum = Field(default=ChannelEnvironmentEnum.SANDBOX, description="M-Pesa environment")
    
    @validator('shortcode')
    def validate_shortcode(cls, v):
        if not v.isdigit():
            raise ValueError('Shortcode must contain only digits')
        return v


class MpesaChannelCreate(MpesaChannelBase):
    """Schema for creating M-Pesa channel"""
    # Credentials (will be encrypted before storage)
    consumer_key: str = Field(..., min_length=10, description="M-Pesa consumer key")
    consumer_secret: str = Field(..., min_length=10, description="M-Pesa consumer secret")
    passkey: Optional[str] = Field(None, description="M-Pesa passkey for STK Push")
    
    # URL configuration
    validation_url: Optional[HttpUrl] = Field(None, description="Validation URL for C2B")
    confirmation_url: Optional[HttpUrl] = Field(None, description="Confirmation URL for C2B")
    callback_url: Optional[HttpUrl] = Field(None, description="Callback URL for STK Push")
    response_type: str = Field(default="Completed", pattern="^(Completed|Cancelled)$")
    
    # PayBill specific configuration
    account_mapping: Optional[Dict[str, str]] = Field(
        None, 
        description="Account mapping for PayBill channels",
        example={"default": "loyalty", "VIP*": "vip_account", "GOLD001": "gold_account"}
    )
    
    # Additional configuration
    config_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional configuration metadata")
    is_primary: bool = Field(default=False, description="Whether this is the primary channel for the merchant")


class MpesaChannelUpdate(BaseModel):
    """Schema for updating M-Pesa channel"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    shortcode: Optional[str] = Field(None, min_length=5, max_length=20)
    channel_type: Optional[ChannelTypeEnum] = None
    environment: Optional[ChannelEnvironmentEnum] = None
    
    # Credentials (optional for updates)
    consumer_key: Optional[str] = Field(None, min_length=10)
    consumer_secret: Optional[str] = Field(None, min_length=10)
    passkey: Optional[str] = None
    
    # URL configuration
    validation_url: Optional[HttpUrl] = None
    confirmation_url: Optional[HttpUrl] = None
    callback_url: Optional[HttpUrl] = None
    response_type: Optional[str] = Field(None, paattern="^(Completed|Cancelled)$")
    
    # PayBill configuration
    account_mapping: Optional[Dict[str, str]] = None
    
    # Status and metadata
    status: Optional[ChannelStatusEnum] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
    config_metadata: Optional[Dict[str, Any]] = None
    
    @validator('shortcode')
    def validate_shortcode(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError('Shortcode must contain only digits')
        return v


class MpesaChannelResponse(BaseModel):
    """Schema for M-Pesa channel response"""
    id: int
    merchant_id: int
    name: str
    shortcode: str
    channel_type: ChannelTypeEnum
    environment: ChannelEnvironmentEnum
    
    # Status information
    status: ChannelStatusEnum
    is_active: bool
    is_primary: bool
    
    # URL configuration (public info)
    validation_url: Optional[str] = None
    confirmation_url: Optional[str] = None
    callback_url: Optional[str] = None
    response_type: str
    
    # PayBill configuration
    account_mapping: Optional[Dict[str, str]] = None
    
    # Verification status
    last_verified_at: Optional[datetime] = None
    last_registration_at: Optional[datetime] = None
    
    # Metadata
    config_metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Note: Credentials are never included in responses for security
    
    class Config:
        from_attributes = True
        use_enum_values = True


class MpesaChannelListResponse(BaseModel):
    """Schema for listing M-Pesa channels"""
    channels: List[MpesaChannelResponse]
    total: int
    page: int
    per_page: int


class MpesaChannelVerificationRequest(BaseModel):
    """Schema for channel verification request"""
    channel_id: int


class MpesaChannelVerificationResponse(BaseModel):
    """Schema for channel verification response"""
    channel_id: int
    status: str
    verified: bool
    verification_details: Dict[str, Any]
    verified_at: datetime


class MpesaChannelURLRegistrationRequest(BaseModel):
    """Schema for URL registration request"""
    channel_id: int
    validation_url: HttpUrl
    confirmation_url: HttpUrl
    response_type: str = Field(default="Completed", pattern="^(Completed|Cancelled)$")


class MpesaChannelURLRegistrationResponse(BaseModel):
    """Schema for URL registration response"""
    channel_id: int
    status: str
    registered: bool
    registration_details: Dict[str, Any]
    registered_at: datetime


class MpesaChannelStatusResponse(BaseModel):
    """Schema for channel status response"""
    channel_id: int
    shortcode: str
    status: ChannelStatusEnum
    is_active: bool
    is_configured: bool
    is_ready_for_transactions: bool
    last_checked: datetime
    health_details: Dict[str, Any]


class MpesaChannelSimulationRequest(BaseModel):
    """Schema for transaction simulation request"""
    channel_id: int
    amount: float = Field(..., gt=0, le=70000, description="Transaction amount (1-70000 KES)")
    customer_phone: str = Field(..., pattern=r"^254[0-9]{9}$", description="Customer phone number (254XXXXXXXXX)")
    bill_ref: Optional[str] = Field(None, max_length=50, description="Bill reference number")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 70000:
            raise ValueError('Amount cannot exceed KES 70,000')
        return round(v, 2)


class MpesaChannelSimulationResponse(BaseModel):
    """Schema for transaction simulation response"""
    channel_id: int
    simulation_id: str
    status: str
    amount: float
    customer_phone: str
    bill_ref: str
    response_details: Dict[str, Any]
    simulated_at: datetime
