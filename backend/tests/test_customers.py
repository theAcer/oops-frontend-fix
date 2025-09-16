import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer import CustomerUpdate

@pytest.mark.asyncio
async def test_get_customers_by_merchant(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer1 = Customer(merchant_id=merchant_id, phone="254711111111", name="Customer One")
    customer2 = Customer(merchant_id=merchant_id, phone="254722222222", name="Customer Two")
    db.add_all([customer1, customer2])
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/customers?merchant_id={merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2 # May include customer from auth setup
    assert any(c["name"] == "Customer One" for c in data)

@pytest.mark.asyncio
async def test_get_customer_by_id(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(merchant_id=merchant_id, phone="254733333333", name="Single Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    response = await authenticated_client.get(f"/api/v1/customers/{customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Single Customer"
    assert data["phone"] == "254733333333"

@pytest.mark.asyncio
async def test_get_customer_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/customers/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

@pytest.mark.asyncio
async def test_update_customer(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(merchant_id=merchant_id, phone="254744444444", name="Old Name", email="old@example.com")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    update_data = {"name": "New Name", "email": "new@example.com", "marketing_consent": False}
    response = await authenticated_client.put(f"/api/v1/customers/{customer.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["email"] == "new@example.com"
    assert data["marketing_consent"] == False

    # Verify in DB
    await db.refresh(customer)
    assert customer.name == "New Name"
    assert customer.email == "new@example.com"
    assert customer.marketing_consent == False

@pytest.mark.asyncio
async def test_update_customer_not_found(authenticated_client: AsyncClient):
    update_data = {"name": "Non Existent"}
    response = await authenticated_client.put("/api/v1/customers/99999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

@pytest.mark.asyncio
async def test_get_customer_loyalty(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: dict):
    merchant_id = create_test_merchant["id"]
    customer = Customer(
        merchant_id=merchant_id,
        phone="254755555555",
        name="Loyalty Customer",
        loyalty_points=500,
        loyalty_tier="silver",
        churn_risk_score=0.3
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    response = await authenticated_client.get(f"/api/v1/customers/{customer.id}/loyalty")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == customer.id
    assert data["loyalty_points"] == 500
    assert data["loyalty_tier"] == "silver"
    assert data["churn_risk_score"] == 0.3
    assert "rewards_available" in data # Should be 0 initially
    assert "points_to_next_tier" in data
    assert "tier_progress_percentage" in data

@pytest.mark.asyncio
async def test_customer_service_find_or_create_customer(db: AsyncSession, create_test_merchant: dict):
    from app.services.customer_service import CustomerService
    merchant_id = create_test_merchant["id"]
    service = CustomerService(db)

    # Test create new customer
    new_customer = await service.find_or_create_customer(merchant_id, "254701000000", "New Guy")
    assert new_customer.phone == "254701000000"
    assert new_customer.name == "New Guy"
    assert new_customer.customer_segment == "new"

    # Test find existing customer
    existing_customer = await service.find_or_create_customer(merchant_id, "254701000000", "Updated Name")
    assert existing_customer.id == new_customer.id
    assert existing_customer.name == "New Guy" # Name should not be updated if already set

    # Test find existing customer with no name initially, then update
    customer_no_name = await service.find_or_create_customer(merchant_id, "254702000000")
    assert customer_no_name.name is None
    updated_customer_name = await service.find_or_create_customer(merchant_id, "254702000000", "Named Guy")
    assert updated_customer_name.name == "Named Guy"

@pytest.mark.asyncio
async def test_customer_service_update_customer_metrics(db: AsyncSession, create_test_merchant: dict):
    from app.services.customer_service import CustomerService
    merchant_id = create_test_merchant["id"]
    service = CustomerService(db)

    customer = Customer(merchant_id=merchant_id, phone="254703000000", name="Metrics Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Add transactions
    transaction1 = Transaction(
        merchant_id=merchant_id, customer_id=customer.id, mpesa_receipt_number="MTRX1", till_number="TESTTILL", amount=100.0, transaction_date=datetime.utcnow() - timedelta(days=30), customer_phone="254703000000"
    )
    transaction2 = Transaction(
        merchant_id=merchant_id, customer_id=customer.id, mpesa_receipt_number="MTRX2", till_number="TESTTILL", amount=200.0, transaction_date=datetime.utcnow() - timedelta(days=15), customer_phone="254703000000"
    )
    transaction3 = Transaction(
        merchant_id=merchant_id, customer_id=customer.id, mpesa_receipt_number="MTRX3", till_number="TESTTILL", amount=300.0, transaction_date=datetime.utcnow() - timedelta(days=5), customer_phone="254703000000"
    )
    db.add_all([transaction1, transaction2, transaction3])
    await db.commit()

    await service.update_customer_metrics(customer.id)
    await db.refresh(customer)

    assert customer.total_transactions == 3
    assert customer.total_spent == 600.0
    assert customer.average_order_value == 200.0
    assert customer.first_purchase_date is not None
    assert customer.last_purchase_date is not None
    assert customer.purchase_frequency_days is not None
    assert customer.customer_segment == "regular" # Based on 3 transactions and recent activity