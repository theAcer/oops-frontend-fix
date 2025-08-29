from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.campaign import Campaign, CampaignStatus, TargetAudience
from app.models.customer import Customer
from app.models.notification import Notification
from app.schemas.campaign import CampaignCreate, CampaignUpdate
import json
import logging

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        """Create a new marketing campaign"""
        campaign = Campaign(**campaign_data.model_dump())
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        
        logger.info(f"Created campaign {campaign.id} for merchant {campaign.merchant_id}")
        return campaign

    async def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def get_merchant_campaigns(
        self, 
        merchant_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Campaign]:
        """Get campaigns for a merchant"""
        result = await self.db.execute(
            select(Campaign)
            .where(Campaign.merchant_id == merchant_id)
            .offset(skip)
            .limit(limit)
            .order_by(Campaign.created_at.desc())
        )
        return result.scalars().all()

    async def update_campaign(
        self, 
        campaign_id: int, 
        campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """Update campaign"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def _get_target_customers(self, campaign: Campaign) -> List[Customer]:
        """Get customers that match campaign targeting criteria"""
        query = select(Customer).where(Customer.merchant_id == campaign.merchant_id)
        
        if campaign.target_audience == TargetAudience.NEW_CUSTOMERS:
            query = query.where(Customer.customer_segment == "new")
        elif campaign.target_audience == TargetAudience.REGULAR_CUSTOMERS:
            query = query.where(Customer.customer_segment == "regular")
        elif campaign.target_audience == TargetAudience.VIP_CUSTOMERS:
            query = query.where(Customer.customer_segment == "vip")
        elif campaign.target_audience == TargetAudience.AT_RISK_CUSTOMERS:
            query = query.where(Customer.customer_segment == "at_risk")
        elif campaign.target_audience == TargetAudience.CHURNED_CUSTOMERS:
            query = query.where(Customer.customer_segment == "churned")
        elif campaign.target_audience == TargetAudience.CUSTOM_SEGMENT:
            # Parse custom segment criteria
            if campaign.custom_segment_criteria:
                try:
                    criteria = json.loads(campaign.custom_segment_criteria)
                    # Apply custom filters based on criteria
                    # This is a simplified example - extend based on your needs
                    if "min_spend" in criteria:
                        query = query.where(Customer.total_spent >= criteria["min_spend"])
                    if "max_spend" in criteria:
                        query = query.where(Customer.total_spent <= criteria["max_spend"])
                    if "min_transactions" in criteria:
                        query = query.where(Customer.total_transactions >= criteria["min_transactions"])
                except json.JSONDecodeError:
                    logger.error(f"Invalid custom segment criteria for campaign {campaign.id}")
        
        # Only include customers who have opted in for marketing
        query = query.where(Customer.marketing_consent == True)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def launch_campaign(self, campaign_id: int) -> bool:
        """Launch a campaign"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign or campaign.status != CampaignStatus.DRAFT:
            return False
        
        # Get target customers
        target_customers = await self._get_target_customers(campaign)
        
        # Update campaign status and metrics
        campaign.status = CampaignStatus.ACTIVE
        campaign.launched_at = datetime.utcnow()
        campaign.target_customers_count = len(target_customers)
        
        # Send SMS notifications if enabled
        if campaign.send_sms and campaign.sms_message:
            await self._send_campaign_sms(campaign, target_customers)
        
        await self.db.commit()
        
        logger.info(f"Launched campaign {campaign_id} targeting {len(target_customers)} customers")
        return True

    async def _send_campaign_sms(self, campaign: Campaign, customers: List[Customer]):
        """Send SMS notifications for campaign"""
        from app.services.notification_service import NotificationService
        
        notification_service = NotificationService(self.db)
        sent_count = 0
        
        for customer in customers:
            try:
                await notification_service.send_sms(
                    customer_id=customer.id,
                    phone=customer.phone,
                    message=campaign.sms_message,
                    campaign_id=campaign.id
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send SMS to customer {customer.id}: {str(e)}")
        
        campaign.sms_sent_count = sent_count
        campaign.reached_customers_count = sent_count

    async def get_campaign_performance(self, campaign_id: int) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return {}
        
        # Get conversion metrics (customers who made purchases after campaign)
        if campaign.launched_at:
            # Count transactions after campaign launch
            from app.models.transaction import Transaction
            result = await self.db.execute(
                select(func.count(Transaction.id)).where(
                    and_(
                        Transaction.merchant_id == campaign.merchant_id,
                        Transaction.transaction_date >= campaign.launched_at
                    )
                )
            )
            post_campaign_transactions = result.scalar() or 0
            
            # This is a simplified conversion tracking
            # In a real system, you'd want more sophisticated attribution
            estimated_conversions = min(post_campaign_transactions, campaign.target_customers_count)
            campaign.conversion_count = estimated_conversions
            
            await self.db.commit()
        
        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": campaign.status,
            "target_customers": campaign.target_customers_count,
            "reached_customers": campaign.reached_customers_count,
            "conversions": campaign.conversion_count,
            "conversion_rate": (campaign.conversion_count / max(1, campaign.reached_customers_count)) * 100,
            "sms_sent": campaign.sms_sent_count,
            "revenue_generated": campaign.total_revenue_generated,
            "launched_at": campaign.launched_at
        }
