from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.sms_service import SMSService
from app.models.notification import NotificationType

router = APIRouter()

class SMSRequest(BaseModel):
    phone_number: str
    message: str
    notification_type: Optional[str] = "promotional"
    customer_id: Optional[int] = None # Added customer_id

class BulkSMSRequest(BaseModel):
    recipients: List[Dict[str, Any]]  # [{"phone": "...", "customer_id": ..., "name": "..."}]
    message: str
    notification_type: Optional[str] = "promotional"

class CampaignSMSRequest(BaseModel):
    campaign_id: int
    target_customers: List[int]
    message_template: str

class ChurnPreventionRequest(BaseModel):
    customer_id: int
    discount_percentage: int
    expiry_date: str

@router.post("/sms/send/{merchant_id}")
async def send_single_sms(
    merchant_id: int,
    request: SMSRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send SMS to a single recipient"""
    sms_service = SMSService(db)
    
    # Convert string to enum
    notification_type = NotificationType.PROMOTIONAL
    if request.notification_type:
        try:
            notification_type = NotificationType(request.notification_type.lower())
        except ValueError:
            notification_type = NotificationType.PROMOTIONAL
    
    result = await sms_service.send_sms(
        phone_number=request.phone_number,
        message=request.message,
        merchant_id=merchant_id,
        notification_type=notification_type,
        customer_id=request.customer_id # Pass customer_id from request
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "SMS sending failed"))
    
    return result

@router.post("/sms/bulk/{merchant_id}")
async def send_bulk_sms(
    merchant_id: int,
    request: BulkSMSRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send SMS to multiple recipients"""
    sms_service = SMSService(db)
    
    # Convert string to enum
    notification_type = NotificationType.PROMOTIONAL
    if request.notification_type:
        try:
            notification_type = NotificationType(request.notification_type.lower())
        except ValueError:
            notification_type = NotificationType.PROMOTIONAL
    
    # For large bulk sends, process in background
    if len(request.recipients) > 10:
        background_tasks.add_task(
            sms_service.send_bulk_sms,
            request.recipients,
            request.message,
            merchant_id,
            notification_type
        )
        return {
            "message": "Bulk SMS processing started in background",
            "recipient_count": len(request.recipients)
        }
    else:
        result = await sms_service.send_bulk_sms(
            recipients=request.recipients,
            message=request.message,
            merchant_id=merchant_id,
            notification_type=notification_type
        )
        return result

@router.post("/sms/campaign")
async def send_campaign_sms(
    request: CampaignSMSRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send SMS campaign to targeted customers"""
    sms_service = SMSService(db)
    
    # Process campaign SMS in background
    background_tasks.add_task(
        sms_service.send_campaign_sms,
        request.campaign_id,
        request.target_customers,
        request.message_template
    )
    
    return {
        "message": "Campaign SMS processing started",
        "campaign_id": request.campaign_id,
        "target_count": len(request.target_customers)
    }

@router.post("/sms/loyalty/{customer_id}")
async def send_loyalty_notification(
    customer_id: int,
    notification_type: str,
    points: Optional[int] = None,
    new_tier: Optional[str] = None,
    reward: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Send loyalty-related SMS notification"""
    sms_service = SMSService(db)
    
    kwargs = {}
    if points:
        kwargs["points"] = points
    if new_tier:
        kwargs["new_tier"] = new_tier
    if reward:
        kwargs["reward"] = reward
    
    result = await sms_service.send_loyalty_notification(
        customer_id=customer_id,
        notification_type=notification_type,
        **kwargs
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Loyalty SMS failed"))
    
    return result

@router.post("/sms/churn-prevention")
async def send_churn_prevention_sms(
    request: ChurnPreventionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send churn prevention SMS with personalized offer"""
    sms_service = SMSService(db)
    
    offer_details = {
        "discount": request.discount_percentage,
        "expiry": request.expiry_date
    }
    
    result = await sms_service.send_churn_prevention_sms(
        customer_id=request.customer_id,
        offer_details=offer_details
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Churn prevention SMS failed"))
    
    return result

@router.get("/history/{merchant_id}")
async def get_notification_history(
    merchant_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get SMS notification history"""
    sms_service = SMSService(db)
    history = await sms_service.get_notification_history(merchant_id, limit)
    return {"notifications": history, "count": len(history)}

@router.get("/analytics/{merchant_id}")
async def get_sms_analytics(
    merchant_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get SMS analytics and performance metrics"""
    sms_service = SMSService(db)
    analytics = await sms_service.get_sms_analytics(merchant_id, days)
    return analytics

@router.get("/templates")
async def get_message_templates():
    """Get predefined SMS message templates"""
    templates = {
        "welcome": "Welcome to our loyalty program, {name}! Start earning points with every purchase.",
        "points_earned": "Hi {name}! You earned {points} points from your recent purchase. Total: {total_points} points.",
        "tier_upgrade": "Congratulations {name}! You've been upgraded to {tier} tier with exclusive benefits!",
        "reward_available": "Great news {name}! You have a {reward} waiting. Visit us to claim it!",
        "churn_prevention": "We miss you {name}! Come back and enjoy {discount}% off your next purchase.",
        "promotional": "Special offer for you {name}! {offer_details}. Limited time only!",
        "birthday": "Happy Birthday {name}! Enjoy a special {gift} on us. Valid this month!",
        "anniversary": "Thank you for being with us for {years} year(s), {name}! Here's a special reward: {reward}."
    }
    return {"templates": templates}
