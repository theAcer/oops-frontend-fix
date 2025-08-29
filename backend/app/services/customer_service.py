from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer import CustomerUpdate

class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to standard format"""
        phone = ''.join(filter(str.isdigit, phone))
        
        if phone.startswith('254'):
            return phone
        elif phone.startswith('0'):
            return '254' + phone[1:]
        elif len(phone) == 9:
            return '254' + phone
        
        return phone

    async def find_or_create_customer(
        self, 
        merchant_id: int, 
        phone: str, 
        name: Optional[str] = None
    ) -> Customer:
        """Find existing customer or create new one"""
        normalized_phone = self._normalize_phone_number(phone)
        
        # Try to find existing customer
        result = await self.db.execute(
            select(Customer).where(
                Customer.merchant_id == merchant_id,
                Customer.phone == normalized_phone
            )
        )
        customer = result.scalar_one_or_none()
        
        if customer:
            # Update name if provided and not already set
            if name and not customer.name:
                customer.name = name
                await self.db.commit()
                await self.db.refresh(customer)
            return customer
        
        # Create new customer
        customer = Customer(
            merchant_id=merchant_id,
            phone=normalized_phone,
            name=name,
            customer_segment="new"
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        
        return customer

    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def get_customers_by_merchant(
        self, 
        merchant_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        """Get customers for a merchant"""
        result = await self.db.execute(
            select(Customer)
            .where(Customer.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_customer(
        self, 
        customer_id: int, 
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer information"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update_customer_metrics(self, customer_id: int) -> None:
        """Update customer metrics based on transaction history"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return
        
        # Get transaction statistics
        result = await self.db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_spent'),
                func.avg(Transaction.amount).label('average_order_value'),
                func.min(Transaction.transaction_date).label('first_purchase'),
                func.max(Transaction.transaction_date).label('last_purchase')
            ).where(Transaction.customer_id == customer_id)
        )
        stats = result.first()
        
        if stats and stats.total_transactions > 0:
            # Update customer metrics
            customer.total_transactions = stats.total_transactions
            customer.total_spent = float(stats.total_spent or 0)
            customer.average_order_value = float(stats.average_order_value or 0)
            customer.first_purchase_date = stats.first_purchase
            customer.last_purchase_date = stats.last_purchase
            
            # Calculate purchase frequency
            if stats.first_purchase and stats.last_purchase and stats.total_transactions > 1:
                days_diff = (stats.last_purchase - stats.first_purchase).days
                customer.purchase_frequency_days = days_diff / (stats.total_transactions - 1)
            
            # Update customer segment
            customer.customer_segment = self._calculate_customer_segment(customer)
            
            await self.db.commit()

    def _calculate_customer_segment(self, customer: Customer) -> str:
        """Calculate customer segment based on behavior"""
        if not customer.last_purchase_date:
            return "new"
        
        days_since_last_purchase = (datetime.utcnow() - customer.last_purchase_date).days
        
        # Churned customers (no purchase in 90+ days)
        if days_since_last_purchase > 90:
            return "churned"
        
        # At-risk customers (no purchase in 30-90 days)
        if days_since_last_purchase > 30:
            return "at_risk"
        
        # VIP customers (high spend and frequency)
        if customer.total_spent > 10000 and customer.total_transactions > 20:
            return "vip"
        
        # Regular customers (multiple purchases)
        if customer.total_transactions > 5:
            return "regular"
        
        return "new"

    async def get_customer_loyalty_status(self, customer_id: int) -> dict:
        """Get comprehensive loyalty status for a customer"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return {}
        
        # Get available rewards count
        from app.models.campaign import Reward
        result = await self.db.execute(
            select(func.count(Reward.id)).where(
                Reward.customer_id == customer_id,
                Reward.is_redeemed == False
            )
        )
        rewards_available = result.scalar() or 0
        
        return {
            "customer_id": customer.id,
            "loyalty_points": customer.loyalty_points,
            "loyalty_tier": customer.loyalty_tier,
            "points_to_next_tier": self._calculate_points_to_next_tier(customer),
            "tier_progress_percentage": self._calculate_tier_progress(customer),
            "current_visits": 0,  # Will be updated when loyalty programs are implemented
            "rewards_available": rewards_available,
            "churn_risk_score": customer.churn_risk_score
        }

    def _calculate_points_to_next_tier(self, customer: Customer) -> int:
        """Calculate points needed for next tier"""
        tier_thresholds = {
            "bronze": 1000,
            "silver": 5000,
            "gold": 10000,
            "platinum": float('inf')
        }
        
        current_tier = customer.loyalty_tier
        current_points = customer.loyalty_points
        
        for tier, threshold in tier_thresholds.items():
            if tier != current_tier and threshold > current_points:
                return int(threshold - current_points)
        
        return 0

    def _calculate_tier_progress(self, customer: Customer) -> float:
        """Calculate progress percentage to next tier"""
        tier_thresholds = {
            "bronze": (0, 1000),
            "silver": (1000, 5000),
            "gold": (5000, 10000),
            "platinum": (10000, float('inf'))
        }
        
        current_tier = customer.loyalty_tier
        current_points = customer.loyalty_points
        
        if current_tier in tier_thresholds:
            min_points, max_points = tier_thresholds[current_tier]
            if max_points == float('inf'):
                return 100.0
            
            progress = (current_points - min_points) / (max_points - min_points)
            return min(100.0, max(0.0, progress * 100))
        
        return 0.0
