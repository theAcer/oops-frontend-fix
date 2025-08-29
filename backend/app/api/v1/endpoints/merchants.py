from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.merchant import MerchantCreate, MerchantResponse, MerchantUpdate
from app.services.merchant_service import MerchantService
from app.services.auth_service import AuthService
from app.api.v1.endpoints.auth import oauth2_scheme # Import oauth2_scheme
from app.models.user import User # Import User model

router = APIRouter()

@router.post("/", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def create_merchant(
    merchant_data: MerchantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new merchant"""
    service = MerchantService(db)
    return await service.create_merchant(merchant_data)

@router.post("/link-user-merchant", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def link_user_to_merchant(
    merchant_data: MerchantCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Create a new merchant and link it to the current authenticated user."""
    auth_service = AuthService(db)
    current_user = await auth_service.get_current_user(token)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    if current_user.merchant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already linked to a merchant")

    merchant_service = MerchantService(db)
    new_merchant = await merchant_service.create_merchant(merchant_data)

    # Link the newly created merchant to the current user
    await merchant_service.link_merchant_to_user(new_merchant.id, current_user.id)
    
    # Refresh the user object to reflect the new merchant_id
    await db.refresh(current_user)

    return new_merchant

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