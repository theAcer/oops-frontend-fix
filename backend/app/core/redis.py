import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

# Global Redis client instance
redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Dependency to get a Redis client instance."""
    global redis_client
    if redis_client is None:
        # Initialize Redis client from URL specified in settings
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis_client():
    """Closes the global Redis client connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None