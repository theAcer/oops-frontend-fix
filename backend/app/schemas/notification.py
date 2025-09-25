from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SMSRequest(BaseModel):
    phone_number: str
    message: str
    notification_type: Optional[str] = Field(default="promotional")
    customer_id: Optional[int] = None


class BulkRecipient(BaseModel):
    phone: str
    customer_id: Optional[int] = None
    name: Optional[str] = None


class BulkSMSRequest(BaseModel):
    recipients: List[Dict[str, Any]]
    message: str
    notification_type: Optional[str] = Field(default="promotional")


class CampaignSMSRequest(BaseModel):
    campaign_id: int
    target_customers: List[int]
    message_template: str


class ChurnPreventionRequest(BaseModel):
    customer_id: int
    discount_percentage: int
    expiry_date: str


class SMSResult(BaseModel):
    success: bool
    message: Optional[str] = None
    notification_id: Optional[int] = None
    error: Optional[str] = None


class BulkSMSResult(BaseModel):
    success: bool
    processed: int
    failed: int
    error: Optional[str] = None


class CampaignStartResponse(BaseModel):
    message: str
    campaign_id: int
    target_count: int


class NotificationHistoryItem(BaseModel):
    id: int
    phone_number: str
    message: str
    status: str
    created_at: str
    customer_id: Optional[int] = None


class NotificationHistoryResponse(BaseModel):
    notifications: List[NotificationHistoryItem]
    count: int


class SMSAnalytics(BaseModel):
    sent: int
    delivered: int
    failed: int
    delivery_rate: float
    window_days: int


class SMSAnalyticsResponse(BaseModel):
    analytics: SMSAnalytics


class TemplatesResponse(BaseModel):
    templates: Dict[str, str]


