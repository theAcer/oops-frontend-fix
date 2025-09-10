from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from datetime import datetime
from app.core.database import get_db
from app.core.redis import get_redis_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/db")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    """
    Check PostgreSQL database connection.
    Performs a simple SELECT 1 query to verify connectivity.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "success", "message": "PostgreSQL connection successful"}
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL connection failed: {e}"
        )

@router.get("/redis")
async def check_redis_connection(redis_client: redis.Redis = Depends(get_redis_client)):
    """
    Check Redis connection.
    Performs a PING command to verify connectivity.
    """
    try:
        await redis_client.ping()
        return {"status": "success", "message": "Redis connection successful"}
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis connection failed: {e}"
        )

@router.get("/all")
async def check_all_services(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Check all critical service connections (PostgreSQL and Redis).
    Returns an aggregated status for both services.
    """
    db_status = {"status": "pending"}
    redis_status = {"status": "pending"}

    try:
        await db.execute(text("SELECT 1"))
        db_status = {"status": "success", "message": "PostgreSQL connection successful"}
    except Exception as e:
        db_status = {"status": "failed", "message": f"PostgreSQL connection failed: {e}"}
        logger.error(f"PostgreSQL connection failed during /health/all: {e}")

    try:
        await redis_client.ping()
        redis_status = {"status": "success", "message": "Redis connection successful"}
    except Exception as e:
        redis_status = {"status": "failed", "message": f"Redis connection failed: {e}"}
        logger.error(f"Redis connection failed during /health/all: {e}")

    overall_status = "healthy" if db_status["status"] == "success" and redis_status["status"] == "success" else "unhealthy"

    return {
        "overall_status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }