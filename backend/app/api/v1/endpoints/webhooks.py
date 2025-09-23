from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services.daraja_service import DarajaService
from app.services.loyalty_service import LoyaltyService
from app.models.merchant import Merchant
from pydantic import BaseModel, Field
from datetime import datetime
import json
import logging
import uuid # For generating unique receipt numbers
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()

class SimulateDarajaTransactionRequest(BaseModel):
    till_number: str = Field(..., description="The M-Pesa Till Number for the merchant.")
    amount: float = Field(..., gt=0, description="The transaction amount.")
    customer_phone: str = Field(..., description="The customer's phone number (e.g., 254712345678).")
    customer_name: Optional[str] = Field(None, description="The customer's name.")
    mpesa_receipt_number: Optional[str] = Field(None, description="Optional: M-Pesa receipt number. Will be generated if not provided.")
    transaction_date: Optional[datetime] = Field(None, description="Optional: Transaction date. Defaults to current UTC time.")

@router.post("/daraja/transaction")
async def handle_daraja_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle incoming Daraja webhook for new transactions"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode())
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Extract till_number from payload to find merchant
        till_number = payload.get("data", {}).get("till_number") # Assuming till_number is in payload
        if not till_number:
            raise HTTPException(status_code=400, detail="Till number not found in webhook payload")

        # Find merchant by till number
        merchant_result = await db.execute(
            select(Merchant).where(Merchant.mpesa_till_number == till_number)
        )
        merchant = merchant_result.scalar_one_or_none()

        if not merchant:
            logger.warning(f"Webhook received for unknown till number: {till_number}")
            raise HTTPException(status_code=404, detail="Merchant not found for till number")

        # Initialize services with merchant_id
        daraja_service = DarajaService(db, merchant.id)
        loyalty_service = LoyaltyService(db)
        
        # Validate webhook signature (if provided)
        if x_signature:
            is_valid = await daraja_service.validate_webhook_signature(
                body.decode(), x_signature
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the transaction
        transaction = await daraja_service.process_webhook_transaction(payload)
        
        if transaction:
            # Loyalty processing is now handled within daraja_service.process_webhook_transaction
            # after the customer metrics are updated.
            # We can optionally trigger it here again if there's a specific reason,
            # but for now, it's integrated into the transaction processing.
            pass
        
        return {"status": "success", "transaction_id": transaction.id if transaction else None}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/daraja/simulate-transaction", status_code=status.HTTP_200_OK)
async def simulate_daraja_transaction(
    request_data: SimulateDarajaTransactionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Simulate an M-Pesa Daraja transaction for testing purposes."""
    
    # Find merchant by till number
    merchant_result = await db.execute(
        select(Merchant).where(Merchant.mpesa_till_number == request_data.till_number)
    )
    merchant = merchant_result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant with till number {request_data.till_number} not found.")

    # Construct a mock Daraja webhook payload
    mock_payload = {
        "data": {
            "id": str(uuid.uuid4()), # Unique ID for the simulated transaction
            "receipt_number": request_data.mpesa_receipt_number or f"R{uuid.uuid4().hex[:10].upper()}",
            "transaction_id": str(uuid.uuid4()),
            "till_number": request_data.till_number,
            "amount": request_data.amount,
            "customer_phone": request_data.customer_phone,
            "customer_name": request_data.customer_name,
            "transaction_date": (request_data.transaction_date or datetime.utcnow()).isoformat(),
            "description": "Simulated M-Pesa transaction",
            "reference": "SIMULATED_REF"
        }
    }
    
    logger.info(f"Simulating Daraja transaction for merchant {merchant.id}: {mock_payload}")

    # Call the actual webhook handler to process the simulated transaction
    # We'll bypass signature validation for simulation
    try:
        # Create a dummy Request object for the handler
        mock_request = Request(scope={"type": "http", "method": "POST", "headers": []})
        mock_request._body = json.dumps(mock_payload).encode('utf-8') # Set raw body

        response = await handle_daraja_webhook(
            request=mock_request,
            x_signature=None, # No signature for simulated webhook
            db=db
        )
        return {"message": "Simulated transaction processed successfully", "transaction_id": response.get("transaction_id")}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during simulated transaction processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process simulated transaction: {str(e)}")


@router.get("/daraja/health")
async def webhook_health_check():
    """Health check endpoint for webhook service"""
    return {"status": "healthy", "service": "daraja_webhook"}


# --- C2B URL registration and callbacks ---

class RegisterURLsRequest(BaseModel):
    ShortCode: str
    ResponseType: str = Field(default="Completed")
    ConfirmationURL: str
    ValidationURL: str


@router.post("/payments/c2b/register-urls", status_code=status.HTTP_200_OK)
async def register_c2b_urls(
    data: RegisterURLsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Forward URL registration to Daraja."""
    # Find any merchant context by ShortCode if needed; for now, use a generic service with merchant 0
    service = DarajaService(db, merchant_id=0)
    result = await service.register_c2b_urls(
        shortcode=data.ShortCode,
        confirmation_url=data.ConfirmationURL,
        validation_url=data.ValidationURL,
        response_type=data.ResponseType,
    )
    return result


@router.post("/payments/c2b/validation")
async def c2b_validation(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.json()
    # Merchant context is not required to validate basic shape; accept all by default
    service = DarajaService(db, merchant_id=0)
    return await service.handle_c2b_validation(payload)


@router.post("/payments/c2b/confirmation")
async def c2b_confirmation(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.json()
    # We’ll try to resolve merchant by BusinessShortCode inside the service
    service = DarajaService(db, merchant_id=0)
    tx = await service.handle_c2b_confirmation(payload)
    # Acknowledge receipt per docs
    return {"ResultCode": 0, "ResultDesc": "Success"}