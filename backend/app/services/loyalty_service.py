from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from app.models.loyalty import LoyaltyProgram, CustomerLoyalty, LoyaltyProgramType
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.campaign import Reward, Campaign
from app.schemas.loyalty import LoyaltyProgramCreate, LoyaltyProgramUpdate, RewardCalculationResult
import logging
import math

logger = logging.getLogger(__name__)

class LoyaltyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_loyalty_program(self, program_data: LoyaltyProgramCreate) -> LoyaltyProgram:
        """Create a new loyalty program"""
        program = LoyaltyProgram(**program_data.model_dump())
        self.db.add(program)
        await self.db.commit()
        await self.db.refresh(program)
        
        logger.info(f"Created loyalty program {program.id} for merchant {program.merchant_id}")
        return program

    async def get_loyalty_program(self, program_id: int) -> Optional[LoyaltyProgram]:
        """Get loyalty program by ID"""
        result = await self.db.execute(
            select(LoyaltyProgram).where(LoyaltyProgram.id == program_id)
        )
        return result.scalar_one_or_none()

    async def get_merchant_loyalty_programs(self, merchant_id: int) -> List[LoyaltyProgram]:
        """Get all loyalty programs for a merchant"""
        result = await self.db.execute(
            select(LoyaltyProgram)
            .where(LoyaltyProgram.merchant_id == merchant_id)
            .order_by(LoyaltyProgram.created_at.desc())
        )
        return result.scalars().all()

    async def get_active_loyalty_program(self, merchant_id: int) -> Optional[LoyaltyProgram]:
        """Get the active loyalty program for a merchant"""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(LoyaltyProgram).where(
                and_(
                    LoyaltyProgram.merchant_id == merchant_id,
                    LoyaltyProgram.is_active == True,
                    LoyaltyProgram.start_date <= now,
                    (LoyaltyProgram.end_date.is_(None)) | (LoyaltyProgram.end_date >= now)
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_loyalty_program(
        self, 
        program_id: int, 
        program_data: LoyaltyProgramUpdate
    ) -> Optional[LoyaltyProgram]:
        """Update loyalty program"""
        program = await self.get_loyalty_program(program_id)
        if not program:
            return None
        
        update_data = program_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)
        
        await self.db.commit()
        await self.db.refresh(program)
        return program

    async def activate_loyalty_program(self, program_id: int) -> bool:
        """Activate a loyalty program"""
        program = await self.get_loyalty_program(program_id)
        if not program:
            return False
        
        # Deactivate other programs for the same merchant
        await self.db.execute(
            select(LoyaltyProgram).where(
                and_(
                    LoyaltyProgram.merchant_id == program.merchant_id,
                    LoyaltyProgram.id != program_id
                )
            ).update({"is_active": False})
        )
        
        # Activate this program
        program.is_active = True
        program.start_date = datetime.utcnow()
        
        await self.db.commit()
        logger.info(f"Activated loyalty program {program_id}")
        return True

    async def get_or_create_customer_loyalty(
        self, 
        customer_id: int, 
        loyalty_program_id: int
    ) -> CustomerLoyalty:
        """Get or create customer loyalty record"""
        result = await self.db.execute(
            select(CustomerLoyalty).where(
                and_(
                    CustomerLoyalty.customer_id == customer_id,
                    CustomerLoyalty.loyalty_program_id == loyalty_program_id
                )
            )
        )
        customer_loyalty = result.scalar_one_or_none()
        
        if not customer_loyalty:
            customer_loyalty = CustomerLoyalty(
                customer_id=customer_id,
                loyalty_program_id=loyalty_program_id,
                current_points=0,
                lifetime_points=0,
                current_tier="bronze",
                current_visits=0,
                total_visits=0
            )
            self.db.add(customer_loyalty)
            await self.db.commit()
            await self.db.refresh(customer_loyalty)
        
        return customer_loyalty

    def _calculate_tier_from_points(self, points: int, program: LoyaltyProgram) -> str:
        """Calculate customer tier based on points"""
        if points >= program.platinum_threshold:
            return "platinum"
        elif points >= program.gold_threshold:
            return "gold"
        elif points >= program.silver_threshold:
            return "silver"
        else:
            return "bronze"

    def _get_tier_multiplier(self, tier: str, program: LoyaltyProgram) -> float:
        """Get points multiplier for a tier"""
        multipliers = {
            "bronze": program.bronze_multiplier,
            "silver": program.silver_multiplier,
            "gold": program.gold_multiplier,
            "platinum": program.platinum_multiplier
        }
        return multipliers.get(tier, 1.0)

    def _calculate_points_to_next_tier(self, current_points: int, program: LoyaltyProgram) -> int:
        """Calculate points needed for next tier"""
        if current_points < program.silver_threshold:
            return int(program.silver_threshold - current_points)
        elif current_points < program.gold_threshold:
            return int(program.gold_threshold - current_points)
        elif current_points < program.platinum_threshold:
            return int(program.platinum_threshold - current_points)
        else:
            return 0

    async def calculate_transaction_rewards(
        self, 
        transaction: Transaction, 
        program: LoyaltyProgram
    ) -> RewardCalculationResult:
        """Calculate rewards for a transaction"""
        if transaction.amount < program.minimum_spend:
            return RewardCalculationResult(
                points_earned=0,
                tier_multiplier=1.0,
                bonus_points=0,
                total_points=0,
                new_tier=None,
                tier_upgraded=False
            )

        # Get customer loyalty record
        customer_loyalty = await self.get_or_create_customer_loyalty(
            transaction.customer_id, program.id
        )
        
        current_tier = customer_loyalty.current_tier
        tier_multiplier = self._get_tier_multiplier(current_tier, program)
        
        # Calculate base points
        if program.program_type == LoyaltyProgramType.POINTS:
            base_points = int(transaction.amount * program.points_per_currency)
        elif program.program_type == LoyaltyProgramType.VISITS:
            base_points = 1  # One point per visit
        elif program.program_type == LoyaltyProgramType.SPEND:
            base_points = int(transaction.amount / 100)  # 1 point per 100 currency units
        else:  # HYBRID
            base_points = max(1, int(transaction.amount * program.points_per_currency))
        
        # Apply tier multiplier
        points_earned = int(base_points * tier_multiplier)
        
        # Check for bonus points (campaigns, special offers, etc.)
        bonus_points = await self._calculate_bonus_points(transaction, program)
        
        total_points = points_earned + bonus_points
        
        # Calculate new tier after adding points
        new_total_points = customer_loyalty.lifetime_points + total_points
        new_tier = self._calculate_tier_from_points(new_total_points, program)
        tier_upgraded = new_tier != current_tier
        
        return RewardCalculationResult(
            points_earned=points_earned,
            tier_multiplier=tier_multiplier,
            bonus_points=bonus_points,
            total_points=total_points,
            new_tier=new_tier if tier_upgraded else None,
            tier_upgraded=tier_upgraded
        )

    async def _calculate_bonus_points(self, transaction: Transaction, program: LoyaltyProgram) -> int:
        """Calculate bonus points from active campaigns"""
        bonus_points = 0
        
        # Check for active campaigns that apply to this transaction
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Campaign).where(
                and_(
                    Campaign.merchant_id == transaction.merchant_id,
                    Campaign.status == "active",
                    Campaign.start_date <= now,
                    (Campaign.end_date.is_(None)) | (Campaign.end_date >= now),
                    Campaign.campaign_type == "points_bonus",
                    Campaign.minimum_spend <= transaction.amount
                )
            )
        )
        campaigns = result.scalars().all()
        
        for campaign in campaigns:
            if campaign.points_multiplier and campaign.points_multiplier > 1:
                # Apply points multiplier bonus
                base_points = int(transaction.amount * program.points_per_currency)
                campaign_bonus = int(base_points * (campaign.points_multiplier - 1))
                bonus_points += campaign_bonus
                
                logger.info(f"Applied campaign {campaign.id} bonus: {campaign_bonus} points")
        
        return bonus_points

    async def process_transaction_loyalty(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Process loyalty rewards for a transaction"""
        # Get transaction
        transaction = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = transaction.scalar_one_or_none()
        
        if not transaction or transaction.loyalty_processed:
            return None
        
        # Get active loyalty program
        program = await self.get_active_loyalty_program(transaction.merchant_id)
        if not program:
            logger.info(f"No active loyalty program for merchant {transaction.merchant_id}")
            return None
        
        # Calculate rewards
        reward_result = await self.calculate_transaction_rewards(transaction, program)
        
        if reward_result.total_points == 0:
            transaction.loyalty_processed = True
            await self.db.commit()
            return None
        
        # Get or create customer loyalty record
        customer_loyalty = await self.get_or_create_customer_loyalty(
            transaction.customer_id, program.id
        )
        
        # Update customer loyalty
        customer_loyalty.current_points += reward_result.total_points
        customer_loyalty.lifetime_points += reward_result.total_points
        customer_loyalty.last_activity = datetime.utcnow()
        
        # Handle visit-based programs
        if program.program_type in [LoyaltyProgramType.VISITS, LoyaltyProgramType.HYBRID]:
            customer_loyalty.current_visits += 1
            customer_loyalty.total_visits += 1
            
            # Check for visit-based rewards
            if (program.visits_required and 
                customer_loyalty.current_visits >= program.visits_required):
                
                # Create visit-based reward
                await self._create_visit_reward(
                    customer_loyalty, program, transaction
                )
                customer_loyalty.current_visits = 0  # Reset visit counter
        
        # Handle tier upgrade
        if reward_result.tier_upgraded:
            old_tier = customer_loyalty.current_tier
            customer_loyalty.current_tier = reward_result.new_tier
            customer_loyalty.tier_achieved_at = datetime.utcnow()
            
            # Update customer's main loyalty tier
            customer = await self.db.execute(
                select(Customer).where(Customer.id == transaction.customer_id)
            )
            customer = customer.scalar_one()
            customer.loyalty_tier = reward_result.new_tier
            customer.loyalty_points = customer_loyalty.current_points
            
            logger.info(f"Customer {transaction.customer_id} upgraded from {old_tier} to {reward_result.new_tier}")
            
            # Create tier upgrade reward
            await self._create_tier_upgrade_reward(
                customer_loyalty, program, transaction, old_tier, reward_result.new_tier
            )
        else:
            # Update customer's points
            customer = await self.db.execute(
                select(Customer).where(Customer.id == transaction.customer_id)
            )
            customer = customer.scalar_one()
            customer.loyalty_points = customer_loyalty.current_points
        
        # Update tier progress
        customer_loyalty.points_to_next_tier = self._calculate_points_to_next_tier(
            customer_loyalty.lifetime_points, program
        )
        
        # Calculate progress percentage
        if customer_loyalty.points_to_next_tier > 0:
            tier_thresholds = {
                "bronze": (0, program.silver_threshold),
                "silver": (program.silver_threshold, program.gold_threshold),
                "gold": (program.gold_threshold, program.platinum_threshold),
                "platinum": (program.platinum_threshold, float('inf'))
            }
            
            current_tier = customer_loyalty.current_tier
            if current_tier in tier_thresholds:
                min_points, max_points = tier_thresholds[current_tier]
                if max_points != float('inf'):
                    progress = (customer_loyalty.lifetime_points - min_points) / (max_points - min_points)
                    customer_loyalty.tier_progress_percentage = min(100.0, max(0.0, progress * 100))
                else:
                    customer_loyalty.tier_progress_percentage = 100.0
        
        # Create points reward record
        reward = Reward(
            customer_id=transaction.customer_id,
            transaction_id=transaction.id,
            reward_type="points",
            points_awarded=reward_result.total_points,
            description=f"Earned {reward_result.total_points} loyalty points"
        )
        self.db.add(reward)
        
        # Mark transaction as processed
        transaction.loyalty_points_earned = reward_result.total_points
        transaction.loyalty_processed = True
        transaction.loyalty_processed_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Processed loyalty for transaction {transaction_id}: {reward_result.total_points} points")
        
        return {
            "transaction_id": transaction_id,
            "points_earned": reward_result.total_points,
            "tier_upgraded": reward_result.tier_upgraded,
            "new_tier": reward_result.new_tier,
            "current_points": customer_loyalty.current_points
        }

    async def _create_visit_reward(
        self, 
        customer_loyalty: CustomerLoyalty, 
        program: LoyaltyProgram, 
        transaction: Transaction
    ):
        """Create reward for completing visit requirement"""
        reward = Reward(
            customer_id=customer_loyalty.customer_id,
            transaction_id=transaction.id,
            reward_type="free_item",
            description=f"Free item after {program.visits_required} visits",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        self.db.add(reward)
        
        logger.info(f"Created visit reward for customer {customer_loyalty.customer_id}")

    async def _create_tier_upgrade_reward(
        self, 
        customer_loyalty: CustomerLoyalty, 
        program: LoyaltyProgram, 
        transaction: Transaction,
        old_tier: str,
        new_tier: str
    ):
        """Create reward for tier upgrade"""
        # Define tier upgrade bonuses
        tier_bonuses = {
            "silver": 100,
            "gold": 250,
            "platinum": 500
        }
        
        bonus_points = tier_bonuses.get(new_tier, 0)
        
        if bonus_points > 0:
            reward = Reward(
                customer_id=customer_loyalty.customer_id,
                transaction_id=transaction.id,
                reward_type="points",
                points_awarded=bonus_points,
                description=f"Tier upgrade bonus: {old_tier} → {new_tier}"
            )
            self.db.add(reward)
            
            # Add bonus points to customer loyalty
            customer_loyalty.current_points += bonus_points
            customer_loyalty.lifetime_points += bonus_points
            
            logger.info(f"Created tier upgrade reward: {bonus_points} points for {old_tier} → {new_tier}")

    async def calculate_and_apply_rewards(self, transaction_id: int) -> Dict[str, Any]:
        """Calculate and apply rewards for a transaction (API endpoint)"""
        result = await self.process_transaction_loyalty(transaction_id)
        
        if not result:
            return {"message": "No rewards calculated", "transaction_id": transaction_id}
        
        return {
            "message": "Rewards calculated and applied",
            **result
        }

    async def redeem_reward(self, reward_id: int, customer_id: int) -> bool:
        """Redeem a customer reward"""
        result = await self.db.execute(
            select(Reward).where(
                and_(
                    Reward.id == reward_id,
                    Reward.customer_id == customer_id,
                    Reward.is_redeemed == False
                )
            )
        )
        reward = result.scalar_one_or_none()
        
        if not reward:
            return False
        
        # Check if reward is expired
        if reward.expires_at and reward.expires_at < datetime.utcnow():
            return False
        
        # Redeem the reward
        reward.is_redeemed = True
        reward.redeemed_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Redeemed reward {reward_id} for customer {customer_id}")
        return True

    async def get_customer_rewards(self, customer_id: int, include_redeemed: bool = False) -> List[Reward]:
        """Get customer's available rewards"""
        query = select(Reward).where(Reward.customer_id == customer_id)
        
        if not include_redeemed:
            query = query.where(Reward.is_redeemed == False)
        
        # Filter out expired rewards
        now = datetime.utcnow()
        query = query.where(
            (Reward.expires_at.is_(None)) | (Reward.expires_at >= now)
        )
        
        result = await self.db.execute(query.order_by(Reward.created_at.desc()))
        return result.scalars().all()

    async def get_loyalty_analytics(self, merchant_id: int) -> Dict[str, Any]:
        """Get loyalty program analytics for a merchant"""
        # Get active program
        program = await self.get_active_loyalty_program(merchant_id)
        if not program:
            return {"error": "No active loyalty program"}
        
        # Get customer loyalty statistics
        result = await self.db.execute(
            select(
                func.count(CustomerLoyalty.id).label('total_members'),
                func.avg(CustomerLoyalty.current_points).label('avg_points'),
                func.sum(CustomerLoyalty.lifetime_points).label('total_points_issued'),
                func.count(CustomerLoyalty.id).filter(CustomerLoyalty.current_tier == 'bronze').label('bronze_members'),
                func.count(CustomerLoyalty.id).filter(CustomerLoyalty.current_tier == 'silver').label('silver_members'),
                func.count(CustomerLoyalty.id).filter(CustomerLoyalty.current_tier == 'gold').label('gold_members'),
                func.count(CustomerLoyalty.id).filter(CustomerLoyalty.current_tier == 'platinum').label('platinum_members')
            ).where(CustomerLoyalty.loyalty_program_id == program.id)
        )
        stats = result.first()
        
        # Get reward statistics
        reward_result = await self.db.execute(
            select(
                func.count(Reward.id).label('total_rewards'),
                func.count(Reward.id).filter(Reward.is_redeemed == True).label('redeemed_rewards'),
                func.sum(Reward.points_awarded).label('total_points_awarded')
            ).join(CustomerLoyalty, Reward.customer_id == CustomerLoyalty.customer_id)
            .where(CustomerLoyalty.loyalty_program_id == program.id)
        )
        reward_stats = reward_result.first()
        
        return {
            "program_id": program.id,
            "program_name": program.name,
            "total_members": stats.total_members or 0,
            "average_points": float(stats.avg_points or 0),
            "total_points_issued": int(stats.total_points_issued or 0),
            "tier_distribution": {
                "bronze": stats.bronze_members or 0,
                "silver": stats.silver_members or 0,
                "gold": stats.gold_members or 0,
                "platinum": stats.platinum_members or 0
            },
            "rewards": {
                "total_issued": reward_stats.total_rewards or 0,
                "total_redeemed": reward_stats.redeemed_rewards or 0,
                "redemption_rate": (reward_stats.redeemed_rewards or 0) / max(1, reward_stats.total_rewards or 1) * 100,
                "total_points_awarded": int(reward_stats.total_points_awarded or 0)
            }
        }
