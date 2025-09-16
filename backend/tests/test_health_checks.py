import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_check_db_connection(client: AsyncClient):
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "PostgreSQL connection successful" in response.json()["message"]

@pytest.mark.asyncio
async def test_check_redis_connection(client: AsyncClient):
    # respx can mock redis connections if needed, but for direct ping, it's usually fine
    # if the redis service is running.
    response = await client.get("/api/v1/health/redis")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Redis connection successful" in response.json()["message"]

@pytest.mark.asyncio
async def test_check_all_services(client: AsyncClient):
    response = await client.get("/api/v1/health/all")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_status"] == "healthy"
    assert data["database"]["status"] == "success"
    assert data["redis"]["status"] == "success"
    assert "timestamp" in data