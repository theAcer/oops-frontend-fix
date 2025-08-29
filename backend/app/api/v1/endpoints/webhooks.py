from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services.daraaa_service import DaraaaService
from app.services.loyalty_service import LoyaltyService
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/daraaa/transaction")
async def handle_daraaa_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle incoming Daraaa webhook for new transactions"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Parse JSON payload
        try:
            payload = json.loads(body.decode())
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Initialize services
        daraaa_service = DaraaaService(db)
        loyalty_service = LoyaltyService(db)
        
        # Validate webhook signature (if provided)
        if x_signature:
            is_valid = await daraaa_service.validate_webhook_signature(
                body.decode(), x_signature
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the transaction
        transaction = await daraaa_service.process_webhook_transaction(payload)
        
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

@router.get("/daraaa/health")
async def webhook_health_check():
    """Health check endpoint for webhook service"""
    return {"status": "healthy", "service": "daraaa_webhook"}
