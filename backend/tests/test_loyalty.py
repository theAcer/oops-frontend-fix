import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.loyalty import LoyaltyProgram, LoyaltyProgramType, CustomerLoyalty
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.campaign import Reward

@pytest.mark.asyncio
async def test_create_loyalty_program(authenticated_client: AsyncClient, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    program_data = {
        "merchant_id": merchant_id,
        "name": "Bronze Tier Rewards",
        "description": "Earn points with every purchase",
        "program_type": "points",
        "points_per_currency": 1.0,
        "minimum_spend": 50.0
    }
    response = await authenticated_client.post("/api/v1/loyalty/programs", json=program_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bronze Tier Rewards"
    assert data["is_active"] == True # Default is_active is True in model

@pytest.mark.asyncio
async def test_get_loyalty_programs(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    program = LoyaltyProgram(
        merchant_id=merchant_id,
        name="Test Program",
        program_type=LoyaltyProgramType.POINTS,
        points_per_currency=1.0,
        minimum_spend=10.0
    )
    db.add(program)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/loyalty/programs?merchant_id={merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Program"

@pytest.mark.asyncio
async def test_activate_loyalty_program(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    program1 = LoyaltyProgram(
        merchant_id=merchant_id,
        name="Program 1",
        program_type=LoyaltyProgramType.POINTS,
        points_per_currency=1.0,
        minimum_spend=10.0,
        is_active=False
    )
    program2 = LoyaltyProgram(
        merchant_id=merchant_id,
        name="Program 2",
        program_type=LoyaltyProgramType.POINTS,
        points_per_currency=1.0,
        minimum_spend=10.0,
        is_active=True # Initially active
    )
    db.add_all([program1, program2])
    await db.commit()
    await db.refresh(program1)
    await db.refresh(program2)

    response = await authenticated_client.post(f"/api/v1/loyalty/programs/{program1.id}/activate")
    assert response.status_code == 200
    assert response.json()["message"] == "Loyalty program activated"

    # Verify program1 is active and program2 is inactive
    await db.refresh(program1)
    await db.refresh(program2)
    assert program1.is_active == True
    assert program2.is_active == False

@pytest.mark.asyncio
async def test_calculate_and_apply_rewards(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create an active loyalty program
    program = LoyaltyProgram(
        merchant_id=merchant_id,
        name="Test Rewards",
        program_type=LoyaltyProgramType.POINTS,
        points_per_currency=1.0,
        minimum_spend=10.0,
        is_active=True,
        start_date=datetime.utcnow() - timedelta(days=1),
        bronze_threshold=0, silver_threshold=100, gold_threshold=500, platinum_threshold=1000,
        bronze_multiplier=1.0, silver_multiplier=1.2, gold_multiplier=1.5, platinum_multiplier=2.0
    )
    db.add(program)
    await db.commit()
    await db.refresh(program)

    # Create a customer
    customer = Customer(merchant_id=merchant_id, phone="254740000001", name="Reward Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Create a transaction
    transaction = Transaction(
        merchant_id=merchant_id,
        customer_id=customer.id,
        mpesa_receipt_number="TRX123",
        till_number="TESTTILL",
        amount=100.0,
        transaction_date=datetime.utcnow(),
        customer_phone="254740000001"
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    response = await authenticated_client.post("/api/v1/loyalty/calculate-rewards", json={"transaction_id": transaction.id})
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Rewards calculated and applied"
    assert data["points_earned"] == 100 # 100 KES * 1.0 points/KES
    assert data["current_points"] == 100

    # Verify customer loyalty updated
    await db.refresh(customer)
    assert customer.loyalty_points == 100
    assert customer.loyalty_tier == "bronze" # Still bronze, as silver_threshold is 100

    # Verify transaction processed
    await db.refresh(transaction)
    assert transaction.loyalty_processed == True
    assert transaction.loyalty_points_earned == 100

@pytest.mark.asyncio
async def test_redeem_reward(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create a customer
    customer = Customer(merchant_id=merchant_id, phone="254750000001", name="Redeem Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Create an unredeemed reward
    reward = Reward(
        customer_id=customer.id,
        reward_type="discount",
        description="10% off next purchase",
        is_redeemed=False,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(reward)
    await db.commit()
    await db.refresh(reward)

    response = await authenticated_client.post(f"/api/v1/loyalty/rewards/{reward.id}/redeem", json={"customer_id": customer.id})
    assert response.status_code == 200
    assert response.json()["message"] == "Reward redeemed successfully"

    # Verify reward is marked as redeemed
    await db.refresh(reward)
    assert reward.is_redeemed == True
    assert reward.redeemed_at is not None

@pytest.mark.asyncio
async def test_get_customer_rewards(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]

    # Create a customer
    customer = Customer(merchant_id=merchant_id, phone="254760000001", name="Rewards List Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Create multiple rewards
    reward1 = Reward(customer_id=customer.id, reward_type="points", points_awarded=50, is_redeemed=False, expires_at=datetime.utcnow() + timedelta(days=10))
    reward2 = Reward(customer_id=customer.id, reward_type="discount", discount_amount=10.0, is_redeemed=True, redeemed_at=datetime.utcnow())
    reward3 = Reward(customer_id=customer.id, reward_type="free_item", is_redeemed=False, expires_at=datetime.utcnow() - timedelta(days=1)) # Expired
    db.add_all([reward1, reward2, reward3])
    await db.commit()

    # Get only unredeemed, non-expired rewards
    response = await authenticated_client.get(f"/api/v1/loyalty/customers/{customer.id}/rewards")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == reward1.id
    assert data[0]["is_redeemed"] == False

    # Get all rewards including redeemed and expired
    response_all = await authenticated_client.get(f"/api/v1/loyalty/customers/{customer.id}/rewards?include_redeemed=true")
    assert response_all.status_code == 200
    data_all = response_all.json()
    assert len(data_all) == 2 # Should include reward1 and reward2, but not expired reward3
    assert any(r["id"] == reward1.id for r in data_all)
    assert any(r["id"] == reward2.id for r in data_all)