from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.merchant import MerchantCreate, MerchantResponse, MerchantUpdate
from app.services.merchant_service import MerchantService

router = APIRouter()

@router.post("/", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def create_merchant(
    merchant_data: MerchantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new merchant"""
    service = MerchantService(db)
    return await service.create_merchant(merchant_data)

@router.get("/", response_model=List[MerchantResponse])
async def get_merchants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all merchants"""
    service = MerchantService(db)
    return await service.get_merchants(skip=skip, limit=limit)

@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get merchant by ID"""
    service = MerchantService(db)
    merchant = await service.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.put("/{merchant_id}", response_model=MerchantResponse)
async def update_merchant(
    merchant_id: int,
    merchant_data: MerchantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update merchant"""
    service = MerchantService(db)
    merchant = await service.update_merchant(merchant_id, merchant_data)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete merchant"""
    service = MerchantService(db)
    success = await service.delete_merchant(merchant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {"message": "Merchant deleted successfully"}
