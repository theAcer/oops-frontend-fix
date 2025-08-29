from fastapi import APIRouter
from app.api.v1.endpoints import merchants, customers, transactions, loyalty, campaigns, analytics, webhooks, ai_recommendations, notifications

api_router = APIRouter()

api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(loyalty.router, prefix="/loyalty", tags=["loyalty"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(ai_recommendations.router, prefix="/ai", tags=["ai-recommendations"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
