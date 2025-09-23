from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.loyalty import LoyaltyProgramCreate, LoyaltyProgramResponse, LoyaltyProgramUpdate
from app.services.loyalty_service import LoyaltyService

router = APIRouter()

@router.post("/programs", response_model=LoyaltyProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_loyalty_program(
    program_data: LoyaltyProgramCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new loyalty program"""
    service = LoyaltyService(db)
    return await service.create_loyalty_program(program_data)

@router.get("/programs", response_model=List[LoyaltyProgramResponse])
async def get_loyalty_programs(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty programs for a merchant"""
    service = LoyaltyService(db)
    return await service.get_merchant_loyalty_programs(merchant_id)

@router.get("/programs/{program_id}", response_model=LoyaltyProgramResponse)
async def get_loyalty_program(
    program_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty program by ID"""
    service = LoyaltyService(db)
    program = await service.get_loyalty_program(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    return program

@router.put("/programs/{program_id}", response_model=LoyaltyProgramResponse)
async def update_loyalty_program(
    program_id: int,
    program_data: LoyaltyProgramUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update loyalty program"""
    service = LoyaltyService(db)
    program = await service.update_loyalty_program(program_id, program_data)
    if not program:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    return program

@router.post("/programs/{program_id}/activate", response_model=dict)
async def activate_loyalty_program(
    program_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activate a loyalty program"""
    service = LoyaltyService(db)
    success = await service.activate_loyalty_program(program_id)
    if not success:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    return {"message": "Loyalty program activated"}

@router.post("/calculate-rewards", response_model=dict)
async def calculate_rewards(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Calculate and apply rewards for a transaction"""
    service = LoyaltyService(db)
    result = await service.calculate_and_apply_rewards(transaction_id)
    return result

@router.post("/rewards/{reward_id}/redeem", response_model=dict)
async def redeem_reward(
    reward_id: int,
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Redeem a customer reward"""
    service = LoyaltyService(db)
    success = await service.redeem_reward(reward_id, customer_id)
    if not success:
        raise HTTPException(status_code=400, detail="Reward not found or already redeemed")
    return {"message": "Reward redeemed successfully"}

@router.get("/customers/{customer_id}/rewards", response_model=list)
async def get_customer_rewards(
    customer_id: int,
    include_redeemed: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get customer's available rewards"""
    service = LoyaltyService(db)
    rewards = await service.get_customer_rewards(customer_id, include_redeemed)
    return rewards

@router.get("/analytics/{merchant_id}", response_model=dict)
async def get_loyalty_analytics(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty program analytics"""
    service = LoyaltyService(db)
    analytics = await service.get_loyalty_analytics(merchant_id)
    return analytics
