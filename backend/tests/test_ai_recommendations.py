import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.merchant import Merchant
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_get_customer_recommendation_summary(authenticated_client: AsyncClient, db: AsyncSession, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id
    customer = Customer(
        merchant_id=merchant_id,
        phone="254712345678",
        name="AI Customer",
        churn_risk_score=0.6,
        lifetime_value_prediction=1500.0,
        last_purchase_date=datetime.utcnow() - timedelta(days=10)
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    # Add some transactions for behavior analysis
    for i in range(3):
        transaction = Transaction(
            merchant_id=merchant_id,
            customer_id=customer.id,
            mpesa_receipt_number=f"AI{i}",
            till_number="TESTTILL",
            amount=100.0 + i*10,
            transaction_date=datetime.utcnow() - timedelta(days=i*5),
            customer_phone="254712345678"
        )
        db.add(transaction)
    await db.commit()

    response = await authenticated_client.get(f"/api/v1/ai/customer/{customer.id}/recommendations/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["customer_id"] == customer.id
    assert "churn_risk" in data
    assert "next_purchase" in data
    assert "personalized_offers" in data
    assert "lifetime_value" in data
    assert data["churn_risk"]["churn_risk_score"] >= 0.0 # Should be calculated
    assert data["lifetime_value"]["predicted_clv_12_months"] >= 0.0 # Should be calculated
    assert len(data["personalized_offers"]) >= 1 # Should generate some offers

@pytest.mark.asyncio
async def test_train_merchant_models(authenticated_client: AsyncClient, create_test_merchant: Merchant):
    merchant_id = create_test_merchant.id

    # This endpoint triggers a background task, so we just check the immediate response
    response = await authenticated_client.post(f"/api/v1/ai/merchant/{merchant_id}/train-models")
    assert response.status_code == 200
    assert response.json()["message"] == "Model training started in background"