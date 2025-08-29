from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas.customer import CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    merchant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get customers for a merchant"""
    service = CustomerService(db)
    return await service.get_customers_by_merchant(merchant_id, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by ID"""
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update customer information"""
    service = CustomerService(db)
    customer = await service.update_customer(customer_id, customer_data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{customer_id}/loyalty")
async def get_customer_loyalty(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer loyalty status and points"""
    service = CustomerService(db)
    return await service.get_customer_loyalty_status(customer_id)
