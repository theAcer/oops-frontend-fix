from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/dashboard/{merchant_id}")
async def get_merchant_dashboard(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive merchant dashboard analytics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    dashboard_data = await service.get_merchant_dashboard_data(
        merchant_id, start_date, end_date
    )
    return dashboard_data

@router.get("/overview/{merchant_id}")
async def get_overview_metrics(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get high-level overview metrics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    overview = await service.get_overview_metrics(merchant_id, start_date, end_date)
    return overview

@router.get("/revenue/{merchant_id}")
async def get_revenue_analytics(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed revenue analytics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    revenue_data = await service.get_revenue_analytics(merchant_id, start_date, end_date)
    return revenue_data

@router.get("/customers/{merchant_id}")
async def get_customer_analytics(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed customer analytics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    customer_data = await service.get_customer_analytics(merchant_id, start_date, end_date)
    return customer_data

@router.get("/loyalty/{merchant_id}")
async def get_loyalty_analytics(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty program analytics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    loyalty_data = await service.get_loyalty_analytics(merchant_id, start_date, end_date)
    return loyalty_data

@router.get("/campaigns/{merchant_id}")
async def get_campaign_analytics(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get campaign performance analytics"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    campaign_data = await service.get_campaign_analytics(merchant_id, start_date, end_date)
    return campaign_data

@router.get("/customer-insights/{merchant_id}")
async def get_customer_insights(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed customer behavior insights"""
    service = AnalyticsService(db)
    insights = await service.get_customer_insights(merchant_id)
    return insights

@router.get("/churn-risk/{merchant_id}")
async def get_churn_risk_customers(
    merchant_id: int,
    risk_threshold: float = Query(0.7, description="Minimum churn risk score"),
    db: AsyncSession = Depends(get_db)
):
    """Get customers at risk of churning"""
    service = AnalyticsService(db)
    at_risk_customers = await service.get_churn_risk_customers(merchant_id, risk_threshold)
    return {"customers": at_risk_customers, "count": len(at_risk_customers)}

@router.get("/revenue-trends/{merchant_id}")
async def get_revenue_trends(
    merchant_id: int,
    days: int = Query(90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue trends and forecasting"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    trends = await service.get_revenue_trends(merchant_id, start_date, end_date)
    return trends

@router.get("/export/{merchant_id}")
async def export_analytics_data(
    merchant_id: int,
    data_type: str = Query(..., description="Type of data to export: transactions, customers, loyalty, campaigns"),
    days: int = Query(30, description="Number of days to include"),
    db: AsyncSession = Depends(get_db)
):
    """Export analytics data for external use"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    export_data = await service.export_analytics_data(merchant_id, data_type, start_date, end_date)
    return export_data

@router.get("/kpis/{merchant_id}")
async def get_key_performance_indicators(
    merchant_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get key performance indicators summary"""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get overview metrics which contain KPIs
    overview = await service.get_overview_metrics(merchant_id, start_date, end_date)
    
    # Extract key KPIs
    kpis = {
        "total_revenue": overview.get("total_revenue", 0),
        "total_transactions": overview.get("total_transactions", 0),
        "average_transaction_value": overview.get("average_transaction_value", 0),
        "unique_customers": overview.get("unique_customers", 0),
        "revenue_growth": overview.get("growth_metrics", {}).get("revenue_growth", 0),
        "customer_growth": overview.get("growth_metrics", {}).get("customer_growth", 0),
        "at_risk_customers": overview.get("at_risk_customers", 0),
        "average_churn_risk": overview.get("average_churn_risk", 0)
    }
    
    return kpis

@router.get("/real-time/{merchant_id}")
async def get_real_time_metrics(
    merchant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time metrics for today"""
    service = AnalyticsService(db)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today + timedelta(days=1)
    
    today_metrics = await service.get_overview_metrics(merchant_id, today, end_of_today)
    
    return {
        "date": today.isoformat(),
        "metrics": {
            "today_revenue": today_metrics.get("total_revenue", 0),
            "today_transactions": today_metrics.get("total_transactions", 0),
            "today_customers": today_metrics.get("unique_customers", 0),
            "avg_transaction_today": today_metrics.get("average_transaction_value", 0)
        }
    }
