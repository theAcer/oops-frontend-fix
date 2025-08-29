from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.loyalty import LoyaltyProgram, CustomerLoyalty
from app.models.campaign import Campaign, Reward
from app.models.notification import Notification
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_merchant_dashboard_data(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard data for merchant"""
        try:
            # Get all dashboard components
            overview = await self.get_overview_metrics(merchant_id, start_date, end_date)
            revenue = await self.get_revenue_analytics(merchant_id, start_date, end_date)
            customers = await self.get_customer_analytics(merchant_id, start_date, end_date)
            loyalty = await self.get_loyalty_analytics(merchant_id, start_date, end_date)
            campaigns = await self.get_campaign_analytics(merchant_id, start_date, end_date)
            
            return {
                "merchant_id": merchant_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "overview": overview,
                "revenue": revenue,
                "customers": customers,
                "loyalty": loyalty,
                "campaigns": campaigns,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data error for merchant {merchant_id}: {str(e)}")
            return {"error": "Failed to generate dashboard data"}

    async def get_overview_metrics(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get high-level overview metrics"""
        
        # Current period metrics
        current_metrics = await self.db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_revenue'),
                func.avg(Transaction.amount).label('avg_transaction_value'),
                func.count(func.distinct(Transaction.customer_id)).label('unique_customers')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
        )
        current = current_metrics.first()
        
        # Previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date
        
        previous_metrics = await self.db.execute(
            select(
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_revenue'),
                func.avg(Transaction.amount).label('avg_transaction_value'),
                func.count(func.distinct(Transaction.customer_id)).label('unique_customers')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= prev_start,
                    Transaction.transaction_date <= prev_end
                )
            )
        )
        previous = previous_metrics.first()
        
        # Calculate growth rates
        def calculate_growth(current_val, previous_val):
            if not previous_val or previous_val == 0:
                return 0.0
            return ((current_val - previous_val) / previous_val) * 100
        
        # Get customer metrics
        customer_metrics = await self.db.execute(
            select(
                func.count(Customer.id).label('total_customers'),
                func.count(Customer.id).filter(Customer.customer_segment == 'new').label('new_customers'),
                func.count(Customer.id).filter(Customer.customer_segment == 'at_risk').label('at_risk_customers'),
                func.avg(Customer.churn_risk_score).label('avg_churn_risk')
            ).where(Customer.merchant_id == merchant_id)
        )
        customer_stats = customer_metrics.first()
        
        return {
            "total_revenue": float(current.total_revenue or 0),
            "total_transactions": current.total_transactions or 0,
            "average_transaction_value": float(current.avg_transaction_value or 0),
            "unique_customers": current.unique_customers or 0,
            "total_customers": customer_stats.total_customers or 0,
            "new_customers": customer_stats.new_customers or 0,
            "at_risk_customers": customer_stats.at_risk_customers or 0,
            "average_churn_risk": float(customer_stats.avg_churn_risk or 0),
            "growth_metrics": {
                "revenue_growth": calculate_growth(
                    current.total_revenue or 0, 
                    previous.total_revenue or 0
                ),
                "transaction_growth": calculate_growth(
                    current.total_transactions or 0, 
                    previous.total_transactions or 0
                ),
                "customer_growth": calculate_growth(
                    current.unique_customers or 0, 
                    previous.unique_customers or 0
                ),
                "avg_value_growth": calculate_growth(
                    current.avg_transaction_value or 0, 
                    previous.avg_transaction_value or 0
                )
            }
        }

    async def get_revenue_analytics(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get detailed revenue analytics"""
        
        # Daily revenue trend
        daily_revenue = await self.db.execute(
            select(
                func.date(Transaction.transaction_date).label('date'),
                func.sum(Transaction.amount).label('revenue'),
                func.count(Transaction.id).label('transactions')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by(func.date(Transaction.transaction_date))
            .order_by(func.date(Transaction.transaction_date))
        )
        
        daily_data = []
        for row in daily_revenue:
            daily_data.append({
                "date": row.date.isoformat(),
                "revenue": float(row.revenue),
                "transactions": row.transactions
            })
        
        # Hourly patterns
        hourly_revenue = await self.db.execute(
            select(
                func.extract('hour', Transaction.transaction_date).label('hour'),
                func.sum(Transaction.amount).label('revenue'),
                func.count(Transaction.id).label('transactions')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by(func.extract('hour', Transaction.transaction_date))
            .order_by(func.extract('hour', Transaction.transaction_date))
        )
        
        hourly_data = []
        for row in hourly_revenue:
            hourly_data.append({
                "hour": int(row.hour),
                "revenue": float(row.revenue),
                "transactions": row.transactions
            })
        
        # Day of week patterns
        dow_revenue = await self.db.execute(
            select(
                func.extract('dow', Transaction.transaction_date).label('day_of_week'),
                func.sum(Transaction.amount).label('revenue'),
                func.count(Transaction.id).label('transactions'),
                func.avg(Transaction.amount).label('avg_transaction')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by(func.extract('dow', Transaction.transaction_date))
            .order_by(func.extract('dow', Transaction.transaction_date))
        )
        
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        weekly_data = []
        for row in dow_revenue:
            weekly_data.append({
                "day": day_names[int(row.day_of_week)],
                "revenue": float(row.revenue),
                "transactions": row.transactions,
                "avg_transaction": float(row.avg_transaction)
            })
        
        # Revenue distribution by transaction size
        revenue_distribution = await self.db.execute(
            select(
                func.case(
                    (Transaction.amount < 100, 'Under 100'),
                    (Transaction.amount < 500, '100-500'),
                    (Transaction.amount < 1000, '500-1000'),
                    (Transaction.amount < 2000, '1000-2000'),
                    else_='Over 2000'
                ).label('range'),
                func.count(Transaction.id).label('count'),
                func.sum(Transaction.amount).label('revenue')
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).group_by('range')
        )
        
        distribution_data = []
        for row in revenue_distribution:
            distribution_data.append({
                "range": row.range,
                "count": row.count,
                "revenue": float(row.revenue)
            })
        
        return {
            "daily_trend": daily_data,
            "hourly_patterns": hourly_data,
            "weekly_patterns": weekly_data,
            "revenue_distribution": distribution_data,
            "peak_hour": max(hourly_data, key=lambda x: x['revenue'])['hour'] if hourly_data else None,
            "peak_day": max(weekly_data, key=lambda x: x['revenue'])['day'] if weekly_data else None
        }

    async def get_customer_analytics(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get detailed customer analytics"""
        
        # Customer segmentation
        segment_analysis = await self.db.execute(
            select(
                Customer.customer_segment,
                func.count(Customer.id).label('count'),
                func.avg(Customer.total_spent).label('avg_spent'),
                func.avg(Customer.total_transactions).label('avg_transactions'),
                func.avg(Customer.churn_risk_score).label('avg_churn_risk')
            ).where(Customer.merchant_id == merchant_id)
            .group_by(Customer.customer_segment)
        )
        
        segments = {}
        for row in segment_analysis:
            segments[row.customer_segment] = {
                "count": row.count,
                "avg_spent": float(row.avg_spent or 0),
                "avg_transactions": float(row.avg_transactions or 0),
                "avg_churn_risk": float(row.avg_churn_risk or 0)
            }
        
        # New vs returning customers in period
        new_customers_in_period = await self.db.execute(
            select(func.count(Customer.id)).where(
                and_(
                    Customer.merchant_id == merchant_id,
                    Customer.created_at >= start_date,
                    Customer.created_at <= end_date
                )
            )
        )
        new_customers_count = new_customers_in_period.scalar() or 0
        
        # Customer lifetime value distribution
        clv_distribution = await self.db.execute(
            select(
                func.case(
                    (Customer.lifetime_value_prediction < 500, 'Low (< 500)'),
                    (Customer.lifetime_value_prediction < 2000, 'Medium (500-2000)'),
                    (Customer.lifetime_value_prediction < 5000, 'High (2000-5000)'),
                    else_='Very High (5000+)'
                ).label('clv_range'),
                func.count(Customer.id).label('count')
            ).where(Customer.merchant_id == merchant_id)
            .group_by('clv_range')
        )
        
        clv_data = []
        for row in clv_distribution:
            clv_data.append({
                "range": row.clv_range,
                "count": row.count
            })
        
        # Top customers by value
        top_customers = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                Customer.phone,
                Customer.total_spent,
                Customer.total_transactions,
                Customer.loyalty_tier,
                Customer.churn_risk_score
            ).where(Customer.merchant_id == merchant_id)
            .order_by(Customer.total_spent.desc())
            .limit(10)
        )
        
        top_customers_data = []
        for row in top_customers:
            top_customers_data.append({
                "id": row.id,
                "name": row.name or "Unknown",
                "phone": row.phone,
                "total_spent": float(row.total_spent),
                "total_transactions": row.total_transactions,
                "loyalty_tier": row.loyalty_tier,
                "churn_risk_score": float(row.churn_risk_score)
            })
        
        # Churn risk analysis
        churn_risk_analysis = await self.db.execute(
            select(
                func.case(
                    (Customer.churn_risk_score < 0.3, 'Low Risk'),
                    (Customer.churn_risk_score < 0.7, 'Medium Risk'),
                    else_='High Risk'
                ).label('risk_level'),
                func.count(Customer.id).label('count')
            ).where(Customer.merchant_id == merchant_id)
            .group_by('risk_level')
        )
        
        churn_data = []
        for row in churn_risk_analysis:
            churn_data.append({
                "risk_level": row.risk_level,
                "count": row.count
            })
        
        return {
            "segments": segments,
            "new_customers_in_period": new_customers_count,
            "clv_distribution": clv_data,
            "top_customers": top_customers_data,
            "churn_risk_distribution": churn_data
        }

    async def get_loyalty_analytics(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get loyalty program analytics"""
        
        # Get active loyalty program
        active_program = await self.db.execute(
            select(LoyaltyProgram).where(
                and_(
                    LoyaltyProgram.merchant_id == merchant_id,
                    LoyaltyProgram.is_active == True
                )
            )
        )
        program = active_program.scalar_one_or_none()
        
        if not program:
            return {"error": "No active loyalty program"}
        
        # Loyalty program participation
        participation_stats = await self.db.execute(
            select(
                func.count(CustomerLoyalty.id).label('total_members'),
                func.avg(CustomerLoyalty.current_points).label('avg_points'),
                func.sum(CustomerLoyalty.lifetime_points).label('total_points_issued')
            ).where(CustomerLoyalty.loyalty_program_id == program.id)
        )
        participation = participation_stats.first()
        
        # Tier distribution
        tier_distribution = await self.db.execute(
            select(
                CustomerLoyalty.current_tier,
                func.count(CustomerLoyalty.id).label('count')
            ).where(CustomerLoyalty.loyalty_program_id == program.id)
            .group_by(CustomerLoyalty.current_tier)
        )
        
        tiers = {}
        for row in tier_distribution:
            tiers[row.current_tier] = row.count
        
        # Rewards issued and redeemed
        rewards_stats = await self.db.execute(
            select(
                func.count(Reward.id).label('total_rewards'),
                func.count(Reward.id).filter(Reward.is_redeemed == True).label('redeemed_rewards'),
                func.sum(Reward.points_awarded).label('total_points_awarded')
            ).join(CustomerLoyalty, Reward.customer_id == CustomerLoyalty.customer_id)
            .where(CustomerLoyalty.loyalty_program_id == program.id)
        )
        rewards = rewards_stats.first()
        
        # Points activity in period
        points_activity = await self.db.execute(
            select(
                func.sum(Reward.points_awarded).label('points_issued'),
                func.count(Reward.id).label('rewards_issued')
            ).join(CustomerLoyalty, Reward.customer_id == CustomerLoyalty.customer_id)
            .where(
                and_(
                    CustomerLoyalty.loyalty_program_id == program.id,
                    Reward.created_at >= start_date,
                    Reward.created_at <= end_date
                )
            )
        )
        activity = points_activity.first()
        
        return {
            "program_id": program.id,
            "program_name": program.name,
            "total_members": participation.total_members or 0,
            "average_points": float(participation.avg_points or 0),
            "total_points_issued": int(participation.total_points_issued or 0),
            "tier_distribution": tiers,
            "rewards": {
                "total_issued": rewards.total_rewards or 0,
                "total_redeemed": rewards.redeemed_rewards or 0,
                "redemption_rate": (rewards.redeemed_rewards or 0) / max(1, rewards.total_rewards or 1) * 100,
                "total_points_awarded": int(rewards.total_points_awarded or 0)
            },
            "period_activity": {
                "points_issued": int(activity.points_issued or 0),
                "rewards_issued": activity.rewards_issued or 0
            }
        }

    async def get_campaign_analytics(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get campaign performance analytics"""
        
        # Active campaigns
        active_campaigns = await self.db.execute(
            select(Campaign).where(
                and_(
                    Campaign.merchant_id == merchant_id,
                    Campaign.status == 'active'
                )
            )
        )
        active = active_campaigns.scalars().all()
        
        # Campaign performance in period
        campaign_performance = await self.db.execute(
            select(
                Campaign.id,
                Campaign.name,
                Campaign.campaign_type,
                Campaign.status,
                Campaign.target_customers_count,
                Campaign.reached_customers_count,
                Campaign.conversion_count,
                Campaign.total_revenue_generated,
                Campaign.sms_sent_count,
                Campaign.launched_at
            ).where(
                and_(
                    Campaign.merchant_id == merchant_id,
                    Campaign.launched_at >= start_date,
                    Campaign.launched_at <= end_date
                )
            ).order_by(Campaign.launched_at.desc())
        )
        
        campaigns_data = []
        for row in campaign_performance:
            conversion_rate = (row.conversion_count / max(1, row.reached_customers_count)) * 100
            campaigns_data.append({
                "id": row.id,
                "name": row.name,
                "type": row.campaign_type,
                "status": row.status,
                "target_customers": row.target_customers_count,
                "reached_customers": row.reached_customers_count,
                "conversions": row.conversion_count,
                "conversion_rate": conversion_rate,
                "revenue_generated": float(row.total_revenue_generated),
                "sms_sent": row.sms_sent_count,
                "launched_at": row.launched_at.isoformat() if row.launched_at else None
            })
        
        # Campaign type performance
        type_performance = await self.db.execute(
            select(
                Campaign.campaign_type,
                func.count(Campaign.id).label('count'),
                func.avg(Campaign.conversion_count / func.nullif(Campaign.reached_customers_count, 0) * 100).label('avg_conversion_rate'),
                func.sum(Campaign.total_revenue_generated).label('total_revenue')
            ).where(
                and_(
                    Campaign.merchant_id == merchant_id,
                    Campaign.launched_at >= start_date,
                    Campaign.launched_at <= end_date
                )
            ).group_by(Campaign.campaign_type)
        )
        
        type_data = []
        for row in type_performance:
            type_data.append({
                "type": row.campaign_type,
                "count": row.count,
                "avg_conversion_rate": float(row.avg_conversion_rate or 0),
                "total_revenue": float(row.total_revenue or 0)
            })
        
        return {
            "active_campaigns": len(active),
            "campaigns_in_period": campaigns_data,
            "campaign_type_performance": type_data,
            "total_campaigns_launched": len(campaigns_data)
        }

    async def get_customer_insights(self, merchant_id: int) -> Dict[str, Any]:
        """Get detailed customer behavior insights"""
        
        # Purchase behavior patterns
        behavior_patterns = await self.db.execute(
            select(
                func.avg(Customer.purchase_frequency_days).label('avg_frequency'),
                func.avg(Customer.average_order_value).label('avg_order_value'),
                func.count(Customer.id).filter(Customer.purchase_frequency_days <= 7).label('weekly_customers'),
                func.count(Customer.id).filter(Customer.purchase_frequency_days <= 30).label('monthly_customers')
            ).where(Customer.merchant_id == merchant_id)
        )
        patterns = behavior_patterns.first()
        
        # Customer journey analysis
        journey_analysis = await self.db.execute(
            select(
                Customer.customer_segment,
                func.avg(func.extract('days', Customer.created_at - Customer.first_purchase_date)).label('avg_onboarding_days'),
                func.avg(Customer.total_transactions).label('avg_transactions'),
                func.avg(Customer.total_spent).label('avg_spent')
            ).where(Customer.merchant_id == merchant_id)
            .group_by(Customer.customer_segment)
        )
        
        journey_data = {}
        for row in journey_analysis:
            journey_data[row.customer_segment] = {
                "avg_onboarding_days": float(row.avg_onboarding_days or 0),
                "avg_transactions": float(row.avg_transactions or 0),
                "avg_spent": float(row.avg_spent or 0)
            }
        
        return {
            "purchase_patterns": {
                "avg_frequency_days": float(patterns.avg_frequency or 0),
                "avg_order_value": float(patterns.avg_order_value or 0),
                "weekly_customers": patterns.weekly_customers or 0,
                "monthly_customers": patterns.monthly_customers or 0
            },
            "customer_journey": journey_data
        }

    async def get_churn_risk_customers(
        self, 
        merchant_id: int, 
        risk_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get customers at risk of churning"""
        
        at_risk_customers = await self.db.execute(
            select(
                Customer.id,
                Customer.name,
                Customer.phone,
                Customer.total_spent,
                Customer.last_purchase_date,
                Customer.churn_risk_score,
                Customer.loyalty_tier
            ).where(
                and_(
                    Customer.merchant_id == merchant_id,
                    Customer.churn_risk_score >= risk_threshold
                )
            ).order_by(Customer.churn_risk_score.desc())
            .limit(50)
        )
        
        customers_data = []
        for row in at_risk_customers:
            days_since_last = (datetime.utcnow() - row.last_purchase_date).days if row.last_purchase_date else 999
            customers_data.append({
                "id": row.id,
                "name": row.name or "Unknown",
                "phone": row.phone,
                "total_spent": float(row.total_spent),
                "days_since_last_purchase": days_since_last,
                "churn_risk_score": float(row.churn_risk_score),
                "loyalty_tier": row.loyalty_tier,
                "recommended_action": self._get_retention_action(row.churn_risk_score, row.loyalty_tier)
            })
        
        return customers_data

    def _get_retention_action(self, churn_risk: float, loyalty_tier: str) -> str:
        """Get recommended retention action"""
        if churn_risk >= 0.8:
            if loyalty_tier in ["gold", "platinum"]:
                return "Immediate personal outreach with VIP offer"
            else:
                return "Send high-value discount offer immediately"
        elif churn_risk >= 0.7:
            return "Send personalized re-engagement campaign"
        else:
            return "Include in next loyalty campaign"

    async def get_revenue_trends(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get revenue trends and forecasting"""
        
        # Weekly revenue trend
        weekly_revenue = await self.db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('week', transaction_date) as week,
                    SUM(amount) as revenue,
                    COUNT(*) as transactions
                FROM transactions 
                WHERE merchant_id = :merchant_id 
                    AND transaction_date >= :start_date 
                    AND transaction_date <= :end_date
                GROUP BY DATE_TRUNC('week', transaction_date)
                ORDER BY week
            """),
            {
                "merchant_id": merchant_id,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        weekly_data = []
        for row in weekly_revenue:
            weekly_data.append({
                "week": row.week.isoformat(),
                "revenue": float(row.revenue),
                "transactions": row.transactions
            })
        
        # Calculate trend
        if len(weekly_data) >= 2:
            recent_avg = sum(w["revenue"] for w in weekly_data[-2:]) / 2
            earlier_avg = sum(w["revenue"] for w in weekly_data[:2]) / 2
            trend = "increasing" if recent_avg > earlier_avg else "decreasing"
        else:
            trend = "stable"
        
        return {
            "weekly_trend": weekly_data,
            "trend_direction": trend,
            "total_weeks": len(weekly_data)
        }

    async def export_analytics_data(
        self, 
        merchant_id: int, 
        data_type: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Export analytics data for external use"""
        
        if data_type == "transactions":
            return await self._export_transactions(merchant_id, start_date, end_date)
        elif data_type == "customers":
            return await self._export_customers(merchant_id)
        elif data_type == "loyalty":
            return await self._export_loyalty_data(merchant_id)
        elif data_type == "campaigns":
            return await self._export_campaigns(merchant_id, start_date, end_date)
        else:
            return {"error": "Invalid data type"}

    async def _export_transactions(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Export transaction data"""
        
        transactions = await self.db.execute(
            select(
                Transaction.id,
                Transaction.mpesa_receipt_number,
                Transaction.amount,
                Transaction.customer_phone,
                Transaction.customer_name,
                Transaction.transaction_date,
                Transaction.loyalty_points_earned
            ).where(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).order_by(Transaction.transaction_date.desc())
        )
        
        data = []
        for row in transactions:
            data.append({
                "id": row.id,
                "receipt_number": row.mpesa_receipt_number,
                "amount": float(row.amount),
                "customer_phone": row.customer_phone,
                "customer_name": row.customer_name,
                "date": row.transaction_date.isoformat(),
                "loyalty_points": row.loyalty_points_earned
            })
        
        return {
            "data_type": "transactions",
            "count": len(data),
            "data": data
        }

    async def _export_customers(self, merchant_id: int) -> Dict[str, Any]:
        """Export customer data"""
        
        customers = await self.db.execute(
            select(
                Customer.id,
                Customer.phone,
                Customer.name,
                Customer.customer_segment,
                Customer.total_spent,
                Customer.total_transactions,
                Customer.loyalty_points,
                Customer.loyalty_tier,
                Customer.churn_risk_score,
                Customer.created_at
            ).where(Customer.merchant_id == merchant_id)
            .order_by(Customer.total_spent.desc())
        )
        
        data = []
        for row in customers:
            data.append({
                "id": row.id,
                "phone": row.phone,
                "name": row.name,
                "segment": row.customer_segment,
                "total_spent": float(row.total_spent),
                "total_transactions": row.total_transactions,
                "loyalty_points": row.loyalty_points,
                "loyalty_tier": row.loyalty_tier,
                "churn_risk": float(row.churn_risk_score),
                "joined_date": row.created_at.isoformat()
            })
        
        return {
            "data_type": "customers",
            "count": len(data),
            "data": data
        }

    async def _export_loyalty_data(self, merchant_id: int) -> Dict[str, Any]:
        """Export loyalty program data"""
        
        loyalty_data = await self.db.execute(
            select(
                CustomerLoyalty.customer_id,
                CustomerLoyalty.current_points,
                CustomerLoyalty.lifetime_points,
                CustomerLoyalty.current_tier,
                CustomerLoyalty.joined_at,
                Customer.phone,
                Customer.name
            ).join(Customer, CustomerLoyalty.customer_id == Customer.id)
            .join(LoyaltyProgram, CustomerLoyalty.loyalty_program_id == LoyaltyProgram.id)
            .where(LoyaltyProgram.merchant_id == merchant_id)
        )
        
        data = []
        for row in loyalty_data:
            data.append({
                "customer_id": row.customer_id,
                "phone": row.phone,
                "name": row.name,
                "current_points": row.current_points,
                "lifetime_points": row.lifetime_points,
                "tier": row.current_tier,
                "joined_date": row.joined_at.isoformat()
            })
        
        return {
            "data_type": "loyalty",
            "count": len(data),
            "data": data
        }

    async def _export_campaigns(
        self, 
        merchant_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Export campaign data"""
        
        campaigns = await self.db.execute(
            select(
                Campaign.id,
                Campaign.name,
                Campaign.campaign_type,
                Campaign.status,
                Campaign.target_customers_count,
                Campaign.reached_customers_count,
                Campaign.conversion_count,
                Campaign.total_revenue_generated,
                Campaign.launched_at
            ).where(
                and_(
                    Campaign.merchant_id == merchant_id,
                    Campaign.created_at >= start_date,
                    Campaign.created_at <= end_date
                )
            )
        )
        
        data = []
        for row in campaigns:
            data.append({
                "id": row.id,
                "name": row.name,
                "type": row.campaign_type,
                "status": row.status,
                "target_customers": row.target_customers_count,
                "reached_customers": row.reached_customers_count,
                "conversions": row.conversion_count,
                "revenue_generated": float(row.total_revenue_generated),
                "launched_date": row.launched_at.isoformat() if row.launched_at else None
            })
        
        return {
            "data_type": "campaigns",
            "count": len(data),
            "data": data
        }
