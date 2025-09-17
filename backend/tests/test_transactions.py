import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionStatus, TransactionType
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_get_transactions(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    customer = Customer(merchant_id=merchant_id, phone="254711111111", name="Transaction Customer")
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Create some transactions
    transaction1 = Transaction(
        merchant_id=merchant_id,
        customer_id=customer.id,
        mpesa_receipt_number="TRX001",
        till_number="TESTTILL",
        amount=100.0,
        transaction_date=datetime.utcnow() - timedelta(days=5),
        customer_phone="254711111111"
    )
    transaction2 = Transaction(
        merchant_id=merchant_id,
        customer_id=customer.id,
        mpesa_receipt_number="TRX002",
        till_number="TESTTILL",
        amount=250.0,
        transaction_date=datetime.utcnow() - timedelta(days=2),
        customer_phone="254711111111"
    )
    db.add_all([transaction1, transaction2])
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/transactions?merchant_id={merchant_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(t["mpesa_receipt_number"] == "TRX001" for t in data)

@pytest.mark.asyncio
async def test_get_transactions_by_customer(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    customer1 = Customer(merchant_id=merchant_id, phone="254711111111", name="Customer A")
    customer2 = Customer(merchant_id=merchant_id, phone="254722222222", name="Customer B")
    db.add_all([customer1, customer2])
    await db.commit()
    await db.refresh(customer1)
    await db.refresh(customer2)

    transaction1 = Transaction(
        merchant_id=merchant_id, customer_id=customer1.id, mpesa_receipt_number="CUST001", till_number="TESTTILL", amount=50.0, transaction_date=datetime.utcnow(), customer_phone="254711111111"
    )
    transaction2 = Transaction(
        merchant_id=merchant_id, customer_id=customer2.id, mpesa_receipt_number="CUST002", till_number="TESTTILL", amount=75.0, transaction_date=datetime.utcnow(), customer_phone="254722222222"
    )
    db.add_all([transaction1, transaction2])
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/transactions?merchant_id={merchant_id}&customer_id={customer1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["mpesa_receipt_number"] == "CUST001"

@pytest.mark.asyncio
async def test_get_transaction_by_id(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    transaction = Transaction(
        merchant_id=merchant_id,
        customer_id=None,
        mpesa_receipt_number="SINGLE001",
        till_number="TESTTILL",
        amount=300.0,
        transaction_date=datetime.utcnow(),
        customer_phone="254733333333"
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    response = await authenticated_client.get(f"/api/v1/transactions/{transaction.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["mpesa_receipt_number"] == "SINGLE001"
    assert data["amount"] == 300.0

@pytest.mark.asyncio
async def test_get_transaction_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/transactions/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"

@pytest.mark.asyncio
@respx.mock
async def test_sync_transactions_from_daraja(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant = create_test_merchant
    merchant_id = merchant.id
    merchant.daraja_consumer_key = "test_key"
    merchant.daraja_consumer_secret = "test_secret"
    merchant.daraja_shortcode = "174379"
    merchant.daraja_passkey = "test_passkey"
    await db.commit()
    await db.refresh(merchant)

    # Mock Daraja API token endpoint
    respx.get("https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials").mock(
        return_value=Response(200, json={"access_token": "mock_token", "expires_in": 3599})
    )

    # Mock Daraja API transactions endpoint (assuming it's a custom mock endpoint for pulling)
    respx.get("https://sandbox.safaricom.co.ke/transactions").mock(
        return_value=Response(200, json={
            "data": [
                {
                    "id": "daraaa_id_1",
                    "receipt_number": "MPESA001",
                    "transaction_id": "TRANSID001",
                    "till_number": merchant.mpesa_till_number,
                    "amount": 500.0,
                    "customer_phone": "254712345678",
                    "customer_name": "John Doe",
                    "transaction_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "description": "Test purchase"
                }
            ]
        })
    )

    response = await authenticated_client.post(f"/api/v1/transactions/sync-daraja", json={"merchant_id": merchant_id})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Synced 1 new transactions"

    # Verify transaction and customer created
    transaction_in_db = await db.execute(db.select(Transaction).filter_by(mpesa_receipt_number="MPESA001"))
    transaction_in_db = transaction_in_db.scalar_one()
    assert transaction_in_db.amount == 500.0
    assert transaction_in_db.customer_name == "John Doe"

    customer_in_db = await db.execute(db.select(Customer).filter_by(phone="254712345678"))
    customer_in_db = customer_in_db.scalar_one()
    assert customer_in_db.name == "John Doe"
    assert customer_in_db.total_spent == 500.0 # Customer metrics should be updated