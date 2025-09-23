from pydantic import BaseModel, Field
from typing import Optional


class MpesaChannelBase(BaseModel):
    shortcode: str = Field(..., min_length=5, max_length=20)
    channel_type: str = Field(..., pattern="^(paybill|till)$")
    environment: str = Field(default="sandbox", pattern="^(sandbox|production)$")
    response_type: str = Field(default="Completed", pattern="^(Completed|Cancelled)$")
    validation_url: Optional[str] = None
    confirmation_url: Optional[str] = None


class MpesaChannelCreate(MpesaChannelBase):
    consumer_key: Optional[str] = None
    consumer_secret: Optional[str] = None


class MpesaChannelUpdate(BaseModel):
    shortcode: Optional[str] = None
    channel_type: Optional[str] = Field(None, pattern="^(paybill|till)$")
    environment: Optional[str] = Field(None, pattern="^(sandbox|production)$")
    response_type: Optional[str] = Field(None, pattern="^(Completed|Cancelled)$")
    validation_url: Optional[str] = None
    confirmation_url: Optional[str] = None
    consumer_key: Optional[str] = None
    consumer_secret: Optional[str] = None
    status: Optional[str] = None


class MpesaChannelResponse(MpesaChannelBase):
    id: int
    merchant_id: int
    status: str

    class Config:
        from_attributes = True
