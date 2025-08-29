from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionStatus, TransactionType

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    customer_name: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: int
    merchant_id: int
    customer_id: Optional[int]
    mpesa_receipt_number: str
    mpesa_transaction_id: Optional[str]
    till_number: str
    transaction_type: TransactionType
    status: TransactionStatus
    loyalty_points_earned: int
    loyalty_processed: bool
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionSyncResult(BaseModel):
    new_transactions: int
    updated_transactions: int
    total_amount: float
    sync_period_start: datetime
    sync_period_end: datetime
