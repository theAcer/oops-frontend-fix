import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.campaign import Campaign, CampaignStatus, CampaignType, TargetAudience
from app.models.customer import Customer
from app.models.merchant import Merchant # Import Merchant

@pytest.mark.asyncio
async def test_create_campaign(authenticated_client: AsyncClient, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    campaign_data = {
        "merchant_id": merchant_id,
        "name": "New Customer Welcome",
        "description": "10% off for new customers",
        "campaign_type": "discount",
        "target_audience": "new_customers",
        "discount_percentage": 10.0,
        "minimum_spend": 0.0,
        "sms_message": "Welcome! Get 10% off your first purchase.",
        "send_sms": True,
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    response = await authenticated_client.post("/api/v1/campaigns", json=campaign_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Customer Welcome"
    assert data["status"] == "draft" # Default status is draft

@pytest.mark.asyncio
async def test_get_campaigns(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    campaign = Campaign(
        merchant_id=merchant_id,
        name="Existing Campaign",
        campaign_type=CampaignType.POINTS_BONUS,
        target_audience=TargetAudience.ALL_CUSTOMERS,
        status=CampaignStatus.ACTIVE
    )
    db.add(campaign)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/campaigns?merchant_id={merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Existing Campaign"

@pytest.mark.asyncio
async def test_launch_campaign(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    campaign = Campaign(
        merchant_id=merchant_id,
        name="Launch Test Campaign",
        description="Campaign to be launched",
        campaign_type=CampaignType.DISCOUNT,
        target_audience=TargetAudience.ALL_CUSTOMERS,
        status=CampaignStatus.DRAFT,
        sms_message="Hello from your campaign!",
        send_sms=True,
        start_date=datetime.utcnow() - timedelta(days=1),
        end_date=datetime.utcnow() + timedelta(days=7)
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    # Create a customer for the campaign to target
    customer = Customer(merchant_id=merchant_id, phone="254770000001", name="Target Customer", marketing_consent=True)
    db.add(customer)
    await db.commit()

    response = await authenticated_client.post(f"/api/v1/campaigns/{campaign.id}/launch")
    assert response.status_code == 200
    assert response.json()["message"] == "Campaign launched successfully"

    # Verify campaign status and metrics updated
    await db.refresh(campaign)
    assert campaign.status == CampaignStatus.ACTIVE
    assert campaign.launched_at is not None
    assert campaign.target_customers_count >= 1 # Should include the test customer
    assert campaign.reached_customers_count >= 1 # Should include the test customer (if SMS sent)

@pytest.mark.asyncio
async def test_get_campaign_performance(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    campaign = Campaign(
        merchant_id=merchant_id,
        name="Performance Campaign",
        campaign_type=CampaignType.DISCOUNT,
        target_audience=TargetAudience.ALL_CUSTOMERS,
        status=CampaignStatus.ACTIVE,
        launched_at=datetime.utcnow() - timedelta(days=5),
        target_customers_count=100,
        reached_customers_count=80,
        conversion_count=10,
        total_revenue_generated=1000.0
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    response = await authenticated_client.get(f"/api/v1/campaigns/{campaign.id}/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_name"] == "Performance Campaign"
    assert data["status"] == "active"
    assert data["conversions"] == 10
    assert data["conversion_rate"] == (10 / 80) * 100