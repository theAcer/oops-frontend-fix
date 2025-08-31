from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.transaction import Transaction
from app.models.merchant import Merchant
from app.services.daraja_service import DarajaService # Changed import
from app.services.customer_service import CustomerService

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # DarajaService now needs merchant_id, so it cannot be initialized here directly.
        # It will be initialized within methods that have merchant_id.
        self.customer_service = CustomerService(db)

    async def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_transactions(
        self,
        merchant_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions with optional filters"""
        query = select(Transaction)
        
        conditions = []
        if merchant_id:
            conditions.append(Transaction.merchant_id == merchant_id)
        if customer_id:
            conditions.append(Transaction.customer_id == customer_id)
        if start_date:
            conditions.append(Transaction.transaction_date >= start_date)
        if end_date:
            conditions.append(Transaction.transaction_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit).order_by(Transaction.transaction_date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def sync_transactions_from_daraja(self, merchant_id: int) -> Dict[str, Any]: # Renamed method
        """Sync transactions from Daraja API"""
        daraja_service = DarajaService(self.db, merchant_id) # Initialize DarajaService here
        result = await daraja_service.sync_merchant_transactions() # Call method without merchant_id as it's in init
        
        # Update customer metrics for all affected customers
        if result["new_transactions"] > 0:
            # Get all customers for this merchant that had new transactions
            recent_transactions = await self.get_transactions(
                merchant_id=merchant_id,
                start_date=result["sync_period_start"]
            )
            
            customer_ids = set(t.customer_id for t in recent_transactions if t.customer_id)
            
            for customer_id in customer_ids:
                await self.customer_service.update_customer_metrics(customer_id)
        
        return result

    async def get_merchant_transaction_summary(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get transaction summary for a merchant"""
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_amount'),
                func.avg(Transaction.amount).label('average_amount'),
                func.count(func.distinct(Transaction.customer_id)).label('unique_customers')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
        )
        
        summary = result.first()
        
        return {
            "total_transactions": summary.total_transactions or 0,
            "total_amount": float(summary.total_amount or 0),
            "average_amount": float(summary.average_amount or 0),
            "unique_customers": summary.unique_customers or 0,
            "period_start": start_date,
            "period_end": end_date
        }