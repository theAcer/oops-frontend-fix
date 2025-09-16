import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.loyalty import LoyaltyProgram, CustomerLoyalty
from app.models.campaign import Campaign, CampaignStatus, CampaignType, TargetAudience

@pytest.mark.asyncio
async def test_get_merchant_dashboard(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create test data
    customer = Customer(merchant_id=merchant_id, phone="254712345678", name="Test Customer", churn_risk_score=0.5)
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    transaction_date = datetime.utcnow() - timedelta(days=15)
    transaction = Transaction(
        merchant_id=merchant_id,
        customer_id=customer.id,
        mpesa_receipt_number="R12345",
        till_number="TESTTILL",
        amount=100.0,
        transaction_date=transaction_date,
        customer_phone="254712345678"
    )
    db.add(transaction)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/analytics/dashboard/{merchant_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["merchant_id"] == merchant_id
    assert "overview" in data
    assert data["overview"]["total_revenue"] == 100.0
    assert data["overview"]["total_transactions"] == 1
    assert data["overview"]["unique_customers"] == 1

@pytest.mark.asyncio
async def test_get_revenue_analytics(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create test transactions
    for i in range(5):
        transaction = Transaction(
            merchant_id=merchant_id,
            customer_id=None,
            mpesa_receipt_number=f"REV{i}",
            till_number="TESTTILL",
            amount=50.0 + i*10,
            transaction_date=datetime.utcnow() - timedelta(days=i),
            customer_phone=f"25471111111{i}"
        )
        db.add(transaction)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/analytics/revenue/{merchant_id}")
    assert response.status_code == 200
    data = response.json()

    assert "daily_trend" in data
    assert len(data["daily_trend"]) >= 5 # May include other days if data exists
    assert "hourly_patterns" in data
    assert "weekly_patterns" in data

@pytest.mark.asyncio
async def test_get_customer_analytics(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create test customers
    db.add(Customer(merchant_id=merchant_id, phone="254720000001", name="New Customer", customer_segment="new", total_spent=500, total_transactions=1, churn_risk_score=0.1))
    db.add(Customer(merchant_id=merchant_id, phone="254720000002", name="At Risk Customer", customer_segment="at_risk", total_spent=2000, total_transactions=5, churn_risk_score=0.8))
    db.add(Customer(merchant_id=merchant_id, phone="254720000003", name="VIP Customer", customer_segment="vip", total_spent=15000, total_transactions=30, churn_risk_score=0.05))
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/analytics/customers/{merchant_id}")
    assert response.status_code == 200
    data = response.json()

    assert "segments" in data
    assert data["segments"]["new"]["count"] >= 1 # Includes the test user's customer
    assert data["segments"]["at_risk"]["count"] >= 1
    assert data["segments"]["vip"]["count"] >= 1
    assert "top_customers" in data
    assert "churn_risk_distribution" in data

@pytest.mark.asyncio
async def test_get_loyalty_analytics(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create an active loyalty program
    program = LoyaltyProgram(
        merchant_id=merchant_id,
        name="Gold Program",
        program_type=LoyaltyProgramType.POINTS,
        points_per_currency=1.0,
        minimum_spend=100.0,
        is_active=True,
        start_date=datetime.utcnow() - timedelta(days=30),
        bronze_threshold=0, silver_threshold=1000, gold_threshold=5000, platinum_threshold=10000,
        bronze_multiplier=1.0, silver_multiplier=1.2, gold_multiplier=1.5, platinum_multiplier=2.0
    )
    db.add(program)
    await db.commit()
    await db.refresh(program)

    # Create a customer and loyalty record
    customer = Customer(merchant_id=merchant_id, phone="254730000001", name="Loyalty Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    customer_loyalty = CustomerLoyalty(
        customer_id=customer.id,
        loyalty_program_id=program.id,
        current_points=1500,
        lifetime_points=1500,
        current_tier="silver"
    )
    db.add(customer_loyalty)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/analytics/loyalty/{merchant_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["program_name"] == "Gold Program"
    assert data["total_members"] >= 1
    assert data["tier_distribution"]["silver"] >= 1

@pytest.mark.asyncio
async def test_get_campaign_analytics(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create a campaign
    campaign = Campaign(
        merchant_id=merchant_id,
        name="Summer Sale",
        campaign_type=CampaignType.DISCOUNT,
        target_audience=TargetAudience.ALL_CUSTOMERS,
        status=CampaignStatus.ACTIVE,
        launched_at=datetime.utcnow() - timedelta(days=7),
        conversion_count=5,
        reached_customers_count=100,
        total_revenue_generated=5000.0
    )
    db.add(campaign)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/analytics/campaigns/{merchant_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["active_campaigns"] >= 1
    assert len(data["campaigns_in_period"]) >= 1
    assert data["campaigns_in_period"][0]["name"] == "Summer Sale"