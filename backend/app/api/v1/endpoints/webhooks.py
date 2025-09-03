from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services.daraja_service import DarajaService # Changed import
from app.services.loyalty_service import LoyaltyService
from app.models.merchant import Merchant # Added import to find merchant for DarajaService init
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/daraja/transaction") # Renamed endpoint for clarity
async def handle_daraja_webhook( # Renamed function
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
        daraja_service = DarajaService(db, merchant.id) # Pass merchant_id
        loyalty_service = LoyaltyService(db)
        
        # Validate webhook signature (if provided)
        if x_signature:
            is_valid = await daraja_service.validate_webhook_signature( # Changed service call
                body.decode(), x_signature
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the transaction
        transaction = await daraja_service.process_webhook_transaction(payload) # Changed service call
        
        if transaction:
            # Process loyalty rewards for the new transaction
            try:
                await loyalty_service.process_transaction_loyalty(transaction.id)
                logger.info(f"Loyalty processed for transaction {transaction.id}")
            except Exception as e:
                logger.error(f"Failed to process loyalty for transaction {transaction.id}: {str(e)}")
                # Don't fail the webhook for loyalty processing errors
        
        return {"status": "success", "transaction_id": transaction.id if transaction else None}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/daraja/health") # Renamed endpoint
async def webhook_health_check():
    """Health check endpoint for webhook service"""
    return {"status": "healthy", "service": "daraja_webhook"} # Renamed service