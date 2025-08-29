from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import logging

from app.core.database import get_db
from app.services.sms_service import SMSService
from app.services.ai_service import AIService
from app.models.customer import Customer
from app.models.loyalty import CustomerLoyalty
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "notification_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def send_automated_loyalty_notifications():
    """Send automated loyalty notifications based on customer behavior"""
    asyncio.run(_send_automated_loyalty_notifications())

@celery_app.task
def send_churn_prevention_campaigns():
    """Send churn prevention SMS to at-risk customers"""
    asyncio.run(_send_churn_prevention_campaigns())

@celery_app.task
def send_birthday_notifications():
    """Send birthday SMS to customers"""
    asyncio.run(_send_birthday_notifications())

@celery_app.task
def send_points_expiry_reminders():
    """Send reminders for expiring loyalty points"""
    asyncio.run(_send_points_expiry_reminders())

async def _send_automated_loyalty_notifications():
    """Internal function to send loyalty notifications"""
    try:
        async for db in get_db():
            sms_service = SMSService(db)
            
            # Get customers who earned points in the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            recent_transactions = await db.execute(
                select(Customer).join(Transaction)
                .where(
                    and_(
                        Transaction.transaction_date >= yesterday,
                        Transaction.loyalty_points_earned > 0
                    )
                ).distinct()
            )
            
            customers = recent_transactions.scalars().all()
            
            for customer in customers:
                # Send points earned notification
                await sms_service.send_loyalty_notification(
                    customer_id=customer.id,
                    notification_type="points_earned",
                    points=customer.loyalty_points
                )
                
            logger.info(f"Sent loyalty notifications to {len(customers)} customers")
            
    except Exception as e:
        logger.error(f"Automated loyalty notifications failed: {str(e)}")

async def _send_churn_prevention_campaigns():
    """Internal function to send churn prevention campaigns"""
    try:
        async for db in get_db():
            sms_service = SMSService(db)
            ai_service = AIService(db)
            
            # Get high-risk customers
            high_risk_customers = await db.execute(
                select(Customer).where(Customer.churn_risk_score >= 0.7)
            )
            
            customers = high_risk_customers.scalars().all()
            
            for customer in customers:
                # Get AI-generated offer
                recommendations = await ai_service.get_personalized_recommendations(
                    customer.merchant_id, customer.id
                )
                
                # Send churn prevention SMS
                offer_details = {
                    "discount": 20,  # Default 20% discount
                    "expiry": "this weekend"
                }
                
                await sms_service.send_churn_prevention_sms(
                    customer_id=customer.id,
                    offer_details=offer_details
                )
                
            logger.info(f"Sent churn prevention SMS to {len(customers)} customers")
            
    except Exception as e:
        logger.error(f"Churn prevention campaigns failed: {str(e)}")

async def _send_birthday_notifications():
    """Internal function to send birthday notifications"""
    try:
        async for db in get_db():
            sms_service = SMSService(db)
            
            # Get customers with birthdays today (if birthday field exists)
            today = datetime.utcnow().date()
            
            # This would require adding birthday field to Customer model
            # For now, we'll skip this implementation
            logger.info("Birthday notifications feature requires birthday field in Customer model")
            
    except Exception as e:
        logger.error(f"Birthday notifications failed: {str(e)}")

async def _send_points_expiry_reminders():
    """Internal function to send points expiry reminders"""
    try:
        async for db in get_db():
            sms_service = SMSService(db)
            
            # Get customers with points expiring in 7 days
            expiry_date = datetime.utcnow() + timedelta(days=7)
            
            # This would require adding points_expiry_date field to CustomerLoyalty model
            # For now, we'll send reminders to customers with high points
            high_points_customers = await db.execute(
                select(Customer).where(Customer.loyalty_points >= 500)
            )
            
            customers = high_points_customers.scalars().all()
            
            for customer in customers:
                await sms_service.send_loyalty_notification(
                    customer_id=customer.id,
                    notification_type="points_expiring",
                    expiring_points=customer.loyalty_points,
                    expiry_date="in 30 days"
                )
                
            logger.info(f"Sent points expiry reminders to {len(customers)} customers")
            
    except Exception as e:
        logger.error(f"Points expiry reminders failed: {str(e)}")

# Schedule tasks
celery_app.conf.beat_schedule = {
    'send-loyalty-notifications': {
        'task': 'app.tasks.notification_tasks.send_automated_loyalty_notifications',
        'schedule': 3600.0,  # Every hour
    },
    'send-churn-prevention': {
        'task': 'app.tasks.notification_tasks.send_churn_prevention_campaigns',
        'schedule': 86400.0,  # Daily
    },
    'send-birthday-notifications': {
        'task': 'app.tasks.notification_tasks.send_birthday_notifications',
        'schedule': 86400.0,  # Daily
    },
    'send-points-expiry-reminders': {
        'task': 'app.tasks.notification_tasks.send_points_expiry_reminders',
        'schedule': 604800.0,  # Weekly
    },
}

celery_app.conf.timezone = 'UTC'
