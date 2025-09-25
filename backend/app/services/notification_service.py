from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timezone
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.customer import Customer

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_sms(self, customer_id: int, phone: str, message: str, campaign_id: Optional[int] = None) -> None:
        # Fetch customer to get merchant_id
        result = await self.db.execute(
            Customer.__table__.select().where(Customer.id == customer_id)
        )
        row = result.first()
        merchant_id = row.merchant_id if row else None

        notification = Notification(
            merchant_id=merchant_id or 0,
            customer_id=customer_id,
            campaign_id=campaign_id,
            notification_type=NotificationType.SMS,
            recipient=phone,
            message=message,
            status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc),
        )
        self.db.add(notification)
        await self.db.commit() 