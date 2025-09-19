import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_ # Import func and and_
from app.core.config import settings
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.customer import Customer
from app.models.merchant import Merchant # Import Merchant model

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.AFRICAS_TALKING_API_KEY
        self.username = settings.AFRICAS_TALKING_USERNAME
        self.base_url = "https://api.africastalking.com/version1/messaging"
        
    async def send_sms(
        self, 
        phone_number: str, 
        message: str, 
        merchant_id: int, # merchant_id is now required
        notification_type: NotificationType = NotificationType.PROMOTIONAL,
        customer_id: Optional[int] = None,
        campaign_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send SMS to a single recipient"""
        
        try:
            # Format phone number for Kenya (+254)
            formatted_phone = self._format_phone_number(phone_number)
            
            # Prepare SMS payload
            payload = {
                "username": self.username,
                "to": formatted_phone,
                "message": message,
                "from": settings.SMS_SENDER_ID or "LOYALTY"
            }
            
            headers = {
                "apiKey": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            # Send SMS via Africa's Talking API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    data=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                response_data = response.json()
                
                # Log notification in database
                notification = Notification(
                    merchant_id=merchant_id, # Use the passed merchant_id
                    customer_id=customer_id,
                    campaign_id=campaign_id,
                    notification_type=notification_type,
                    recipient=formatted_phone, # Changed from recipient_phone to recipient
                    message=message, # Changed from message_content to message
                    status=NotificationStatus.SENT if response.status_code == 201 else NotificationStatus.FAILED,
                    provider="africastalking", # Explicitly set provider
                    provider_message_id=response_data.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("messageId"),
                    sent_at=datetime.utcnow() if response.status_code == 201 else None,
                    provider_response=response_data, # Store the full response data
                    cost=float(response_data.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("cost", "0").split(" ")[1]) # Extract cost as float
                )
                
                self.db.add(notification)
                await self.db.commit()
                
                return {
                    "success": response.status_code == 201,
                    "message_id": notification.provider_message_id, # Use provider_message_id
                    "notification_id": notification.id,
                    "cost": notification.cost,
                    "status": response_data.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("status")
                }
                
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            
            # Log failed notification
            notification = Notification(
                merchant_id=merchant_id, # Use the passed merchant_id
                customer_id=customer_id,
                campaign_id=campaign_id,
                notification_type=notification_type,
                recipient=phone_number, # Changed from recipient_phone to recipient
                message=message, # Changed from message_content to message
                status=NotificationStatus.FAILED,
                provider="africastalking",
                provider_response=str(e) # Store the error message
            )
            
            self.db.add(notification)
            await self.db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "notification_id": notification.id
            }
    
    async def send_bulk_sms(
        self, 
        recipients: List[Dict[str, Any]], 
        message: str,
        merchant_id: int, # merchant_id is now required
        notification_type: NotificationType = NotificationType.PROMOTIONAL,
        campaign_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send SMS to multiple recipients"""
        
        results = []
        successful_sends = 0
        failed_sends = 0
        
        for recipient in recipients:
            phone = recipient.get("phone")
            customer_id = recipient.get("customer_id")
            
            # Personalize message if customer name is available
            personalized_message = message
            if recipient.get("name"):
                personalized_message = message.replace("{name}", recipient["name"])
            
            result = await self.send_sms(
                phone_number=phone,
                message=personalized_message,
                merchant_id=merchant_id, # Pass merchant_id
                notification_type=notification_type,
                customer_id=customer_id,
                campaign_id=campaign_id
            )
            
            results.append({
                "phone": phone,
                "customer_id": customer_id,
                "success": result["success"],
                "notification_id": result["notification_id"]
            })
            
            if result["success"]:
                successful_sends += 1
            else:
                failed_sends += 1
        
        return {
            "total_recipients": len(recipients),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "results": results
        }
    
    async def send_loyalty_notification(
        self, 
        customer_id: int, 
        notification_type: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Send loyalty-related notifications"""
        
        # Get customer details
        customer_result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        # Generate message based on notification type
        message = self._generate_loyalty_message(notification_type, customer, **kwargs)
        
        return await self.send_sms(
            phone_number=customer.phone,
            message=message,
            merchant_id=customer.merchant_id, # Pass merchant_id from customer
            notification_type=NotificationType.LOYALTY,
            customer_id=customer_id
        )
    
    async def send_campaign_sms(
        self, 
        campaign_id: int, 
        target_customers: List[int],
        message_template: str
    ) -> Dict[str, Any]:
        """Send SMS campaign to targeted customers"""
        
        # Get customer details
        customers_result = await self.db.execute(
            select(Customer).where(Customer.id.in_(target_customers))
        )
        customers = customers_result.scalars().all()
        
        if not customers:
            return {"success": False, "error": "No customers found"}
        
        # Prepare recipients list
        recipients = []
        # Assuming all customers in a campaign belong to the same merchant
        merchant_id = None
        if customers:
            merchant_id = customers[0].merchant_id

        for customer in customers:
            recipients.append({
                "phone": customer.phone,
                "customer_id": customer.id,
                "name": customer.name or "Valued Customer"
            })
        
        # Send bulk SMS
        return await self.send_bulk_sms(
            recipients=recipients,
            message=message_template,
            merchant_id=merchant_id, # Pass merchant_id
            notification_type=NotificationType.PROMOTIONAL,
            campaign_id=campaign_id
        )
    
    async def send_churn_prevention_sms(
        self, 
        customer_id: int, 
        offer_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send churn prevention SMS with personalized offer"""
        
        customer_result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        # Generate personalized churn prevention message
        message = f"Hi {customer.name or 'there'}! We miss you. Come back and enjoy {offer_details.get('discount', '20')}% off your next purchase. Valid until {offer_details.get('expiry', 'this weekend')}. Reply STOP to opt out."
        
        return await self.send_sms(
            phone_number=customer.phone,
            message=message,
            merchant_id=customer.merchant_id, # Pass merchant_id from customer
            notification_type=NotificationType.RETENTION,
            customer_id=customer_id
        )
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Kenya (+254)"""
        # Remove any spaces, dashes, or plus signs
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Handle different formats
        if clean_phone.startswith('254'):
            return f"+{clean_phone}"
        elif clean_phone.startswith('0'):
            return f"+254{clean_phone[1:]}"
        elif len(clean_phone) == 9: # Assuming 9-digit numbers are missing '0' prefix
            return f"+254{clean_phone}"
        else:
            # If it's not a standard Kenyan format, assume it's already international or try to prepend +254
            if not clean_phone.startswith('+'):
                return f"+254{clean_phone}" # Default to +254 if no other prefix
            return clean_phone
    
    def _generate_loyalty_message(
        self, 
        notification_type: str, 
        customer: Customer, 
        **kwargs
    ) -> str:
        """Generate loyalty notification messages"""
        
        name = customer.name or "Valued Customer"
        
        if notification_type == "points_earned":
            points = kwargs.get("points", 0)
            return f"Hi {name}! You've earned {points} loyalty points from your recent purchase. Total points: {customer.loyalty_points}. Keep shopping to earn more rewards!"
        
        elif notification_type == "tier_upgrade":
            new_tier = kwargs.get("new_tier", "Silver")
            return f"Congratulations {name}! You've been upgraded to {new_tier} tier. Enjoy exclusive benefits and higher rewards on your purchases!"
        
        elif notification_type == "reward_available":
            reward = kwargs.get("reward", "special discount")
            return f"Great news {name}! You have a {reward} waiting for you. Visit us soon to claim your reward. Valid for limited time only!"
        
        elif notification_type == "points_expiring":
            points = kwargs.get("expiring_points", 0)
            expiry_date = kwargs.get("expiry_date", "soon")
            return f"Hi {name}! {points} of your loyalty points expire {expiry_date}. Use them now to get amazing rewards!"
        
        else:
            return f"Hi {name}! Thank you for being a loyal customer. Visit us for exclusive offers and rewards!"
    
    async def get_notification_history(
        self, 
        merchant_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get SMS notification history for merchant"""
        
        notifications_result = await self.db.execute(
            select(Notification)
            .where(Notification.merchant_id == merchant_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        notifications = notifications_result.scalars().all()
        
        history = []
        for notification in notifications:
            history.append({
                "id": notification.id,
                "type": notification.notification_type.value,
                "recipient": notification.recipient, # Changed from recipient_phone to recipient
                "message": notification.message, # Changed from message_content to message
                "status": notification.status.value,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "created_at": notification.created_at.isoformat(),
                "error": notification.provider_response, # Changed from error_message to provider_response
                "cost": float(notification.cost)
            })
        
        return history
    
    async def get_sms_analytics(
        self, 
        merchant_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get SMS analytics for merchant"""
        
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get SMS statistics
        stats_result = await self.db.execute(
            select(
                Notification.status,
                Notification.notification_type,
                func.count(Notification.id).label('count')
            ).where(
                and_(
                    Notification.merchant_id == merchant_id,
                    Notification.notification_type.in_([NotificationType.SMS, NotificationType.PROMOTIONAL, NotificationType.LOYALTY, NotificationType.RETENTION]), # Filter for SMS-related types
                    Notification.created_at >= start_date
                )
            ).group_by(Notification.status, Notification.notification_type)
        )
        
        stats = {}
        total_sent = 0
        total_failed = 0
        
        for row in stats_result:
            status = row.status.value
            notification_type = row.notification_type.value
            count = row.count
            
            if status not in stats:
                stats[status] = {}
            stats[status][notification_type] = count
            
            if status == "sent":
                total_sent += count
            elif status == "failed":
                total_failed += count
        
        success_rate = (total_sent / max(1, total_sent + total_failed)) * 100
        
        return {
            "period_days": days,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": round(success_rate, 2),
            "breakdown": stats
        }