from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    merchant_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get transactions with optional filters"""
    service = TransactionService(db)
    return await service.get_transactions(
        merchant_id=merchant_id,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

@router.post("/sync-daraja") # Renamed endpoint
async def sync_transactions(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Sync transactions from Daraja API for a merchant""" # Updated description
    service = TransactionService(db)
    result = await service.sync_transactions_from_daraja(merchant_id) # Changed method call
    return {"message": f"Synced {result['new_transactions']} new transactions"}

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get transaction by ID"""
    service = TransactionService(db)
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction