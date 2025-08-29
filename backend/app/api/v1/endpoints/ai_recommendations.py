from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.services.ai_service import AIRecommendationService

router = APIRouter()

@router.get("/customer/{customer_id}/analysis")
async def analyze_customer_behavior(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive customer behavior analysis"""
    service = AIRecommendationService(db)
    analysis = await service.analyze_customer_behavior(customer_id)
    return analysis

@router.get("/customer/{customer_id}/churn-risk")
async def predict_churn_risk(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Predict customer churn risk"""
    service = AIRecommendationService(db)
    prediction = await service.predict_churn_risk(customer_id)
    return prediction

@router.get("/customer/{customer_id}/next-purchase")
async def predict_next_purchase(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Predict when customer will make next purchase"""
    service = AIRecommendationService(db)
    prediction = await service.predict_next_purchase(customer_id)
    return prediction

@router.get("/customer/{customer_id}/offers")
async def generate_personalized_offers(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized offers for customer"""
    service = AIRecommendationService(db)
    offers = await service.generate_personalized_offers(customer_id)
    return {"customer_id": customer_id, "offers": offers}

@router.get("/customer/{customer_id}/lifetime-value")
async def predict_customer_lifetime_value(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Predict customer lifetime value"""
    service = AIRecommendationService(db)
    clv = await service.predict_customer_lifetime_value(customer_id)
    return clv

@router.get("/merchant/{merchant_id}/campaign-timing")
async def get_optimal_campaign_timing(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get optimal timing for campaigns"""
    service = AIRecommendationService(db)
    timing = await service.get_optimal_campaign_timing(merchant_id)
    return timing

@router.get("/merchant/{merchant_id}/insights")
async def generate_merchant_insights(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Generate comprehensive AI insights for merchant"""
    service = AIRecommendationService(db)
    insights = await service.generate_merchant_insights(merchant_id)
    return insights

@router.post("/merchant/{merchant_id}/train-models")
async def train_merchant_models(
    merchant_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Train AI models for specific merchant (background task)"""
    service = AIRecommendationService(db)
    
    # Add training task to background
    background_tasks.add_task(service._train_churn_model)
    
    return {"message": "Model training started in background"}

@router.get("/customer/{customer_id}/recommendations/summary")
async def get_customer_recommendation_summary(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get summary of all AI recommendations for a customer"""
    service = AIRecommendationService(db)
    
    # Get all recommendations
    churn_risk = await service.predict_churn_risk(customer_id)
    next_purchase = await service.predict_next_purchase(customer_id)
    offers = await service.generate_personalized_offers(customer_id)
    clv = await service.predict_customer_lifetime_value(customer_id)
    
    return {
        "customer_id": customer_id,
        "churn_risk": churn_risk,
        "next_purchase": next_purchase,
        "personalized_offers": offers,
        "lifetime_value": clv,
        "generated_at": "2024-01-01T00:00:00Z"  # Current timestamp
    }
