import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.notification import Notification, NotificationType, NotificationStatus
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_send_single_sms(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(merchant_id=merchant_id, phone="254711223344", name="SMS Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Mock Africa's Talking API response
    respx.post("https://api.africastalking.com/version1/messaging").mock(
        return_value=Response(201, json={
            "SMSMessageData": {
                "Message": "Sent to 1/1 Total Cost: KES 1.00",
                "Recipients": [
                    {
                        "statusCode": 100,
                        "number": "254711223344",
                        "cost": "KES 1.00",
                        "status": "Success",
                        "messageId": "ATXid_12345"
                    }
                ]
            }
        })
    )

    sms_data = {
        "phone_number": "254711223344",
        "message": "Hello from Zidisha!",
        "notification_type": "promotional",
        "customer_id": customer.id
    }
    response = await authenticated_client.post(f"/api/v1/notifications/sms/send/{merchant_id}", json=sms_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message_id"] == "ATXid_12345"
    assert data["cost"] == 1.0

    # Verify notification logged in DB
    notification = await db.execute(
        db.select(Notification).filter_by(customer_id=customer.id)
    )
    notification = notification.scalar_one()
    assert notification.status == NotificationStatus.SENT
    assert notification.recipient == "+254711223344"
    assert notification.message == "Hello from Zidisha!"

@pytest.mark.asyncio
async def test_send_bulk_sms(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer1 = Customer(merchant_id=merchant_id, phone="254711111111", name="Customer One")
    customer2 = Customer(merchant_id=merchant_id, phone="254722222222", name="Customer Two")
    db.add_all([customer1, customer2])
    await db.commit()
    await db.refresh(customer1)
    await db.refresh(customer2)

    # Mock Africa's Talking API response for bulk
    respx.post("https://api.africastalking.com/version1/messaging").mock(
        return_value=Response(201, json={
            "SMSMessageData": {
                "Message": "Sent to 1/1 Total Cost: KES 1.00",
                "Recipients": [
                    {
                        "statusCode": 100,
                        "number": "254711111111",
                        "cost": "KES 1.00",
                        "status": "Success",
                        "messageId": "ATXid_bulk_1"
                    }
                ]
            }
        })
    )

    bulk_sms_data = {
        "recipients": [
            {"phone": "254711111111", "customer_id": customer1.id, "name": "Customer One"},
            {"phone": "254722222222", "customer_id": customer2.id, "name": "Customer Two"}
        ],
        "message": "Hi {name}, special offer for you!",
        "notification_type": "promotional"
    }
    response = await authenticated_client.post(f"/api/v1/notifications/sms/bulk/{merchant_id}", json=bulk_sms_data)
    assert response.status_code == 200 # For small bulk, it's synchronous
    data = response.json()
    assert data["total_recipients"] == 2
    assert data["successful_sends"] == 2 # Due to mocking, both will succeed
    assert data["failed_sends"] == 0

    # Verify notifications logged in DB
    notifications = await db.execute(
        db.select(Notification).filter(Notification.customer_id.in_([customer1.id, customer2.id]))
    )
    notifications = notifications.scalars().all()
    assert len(notifications) == 2
    assert all(n.status == NotificationStatus.SENT for n in notifications)

@pytest.mark.asyncio
async def test_get_notification_history(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(merchant_id=merchant_id, phone="254788888888", name="History Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    notification1 = Notification(
        merchant_id=merchant_id,
        customer_id=customer.id,
        notification_type=NotificationType.PROMOTIONAL,
        recipient="+254788888888",
        message="Promo 1",
        status=NotificationStatus.SENT,
        sent_at=datetime.utcnow() - timedelta(hours=1),
        cost=1.0
    )
    notification2 = Notification(
        merchant_id=merchant_id,
        customer_id=customer.id,
        notification_type=NotificationType.LOYALTY,
        recipient="+254788888888",
        message="Loyalty update",
        status=NotificationStatus.PENDING,
        cost=0.0
    )
    db.add_all([notification1, notification2])
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/notifications/history/{merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["notifications"][0]["message"] == "Loyalty update" # Ordered by created_at desc
    assert data["notifications"][1]["message"] == "Promo 1"

@pytest.mark.asyncio
async def test_get_sms_analytics(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(merchant_id=merchant_id, phone="254799999999", name="Analytics Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Create some notifications
    db.add(Notification(merchant_id=merchant_id, customer_id=customer.id, notification_type=NotificationType.PROMOTIONAL, recipient="+254799999999", message="Promo SMS", status=NotificationStatus.SENT, sent_at=datetime.utcnow(), cost=1.0))
    db.add(Notification(merchant_id=merchant_id, customer_id=customer.id, notification_type=NotificationType.LOYALTY, recipient="+254799999999", message="Loyalty SMS", status=NotificationStatus.SENT, sent_at=datetime.utcnow(), cost=1.0))
    db.add(Notification(merchant_id=merchant_id, customer_id=customer.id, notification_type=NotificationType.PROMOTIONAL, recipient="+254799999999", message="Failed SMS", status=NotificationStatus.FAILED, cost=0.0, error_message="Network error"))
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/notifications/analytics/{merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sent"] == 2
    assert data["total_failed"] == 1
    assert data["success_rate"] == (2 / 3) * 100
    assert "breakdown" in data
    assert data["breakdown"]["sent"]["promotional"] == 1
    assert data["breakdown"]["sent"]["loyalty"] == 1
    assert data["breakdown"]["failed"]["promotional"] == 1