from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services.campaign_service import CampaignService

router = APIRouter()

@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new marketing campaign"""
    service = CampaignService(db)
    return await service.create_campaign(campaign_data)

@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    merchant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get campaigns for a merchant"""
    service = CampaignService(db)
    return await service.get_merchant_campaigns(merchant_id, skip=skip, limit=limit)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get campaign by ID"""
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update campaign"""
    service = CampaignService(db)
    campaign = await service.update_campaign(campaign_id, campaign_data)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Launch a campaign"""
    service = CampaignService(db)
    success = await service.launch_campaign(campaign_id)
    if not success:
        raise HTTPException(status_code=400, detail="Campaign cannot be launched")
    return {"message": "Campaign launched successfully"}

@router.get("/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get campaign performance metrics"""
    service = CampaignService(db)
    performance = await service.get_campaign_performance(campaign_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return performance
