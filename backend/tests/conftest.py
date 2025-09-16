import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from main import app
from httpx import AsyncClient
from app.models.merchant import Merchant # Import Merchant model
from app.models.user import User # Import User model
from app.services.auth_service import AuthService # Import AuthService

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency for tests."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Set up and tear down the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Add a small delay to ensure DB is fully ready
    await asyncio.sleep(0.1) 
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def create_test_merchant(client: AsyncClient) -> Dict[str, Any]: # Now depends on client
    """Helper fixture to create a merchant for tests via API."""
    merchant_data = {
        "business_name": "Test Merchant",
        "owner_name": "Test Owner",
        "email": "test_merchant@example.com",
        "phone": "254700000000",
        "business_type": "retail",
        "mpesa_till_number": "TESTTILL"
    }
    response = await client.post("/api/v1/merchants/", json=merchant_data)
    assert response.status_code == 201
    return response.json() # Return dict

@pytest_asyncio.fixture
async def create_test_user(client: AsyncClient, create_test_merchant: Dict[str, Any]) -> Dict[str, Any]: # Now depends on client and create_test_merchant
    """Helper fixture to create a user linked to a merchant for tests via API."""
    merchant_id = create_test_merchant["id"]
    user_data = {
        "email": "test_user@example.com",
        "password": "password123",
        "name": "Test User",
        "merchant_id": merchant_id
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json() # Return dict

@pytest_asyncio.fixture
async def get_auth_token(client: AsyncClient, create_test_user: Dict[str, Any]) -> str: # Now depends on client and user
    """Helper fixture to get an auth token for a test user."""
    login_data = {
        "email": create_test_user["email"],
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, get_auth_token: str) -> AsyncClient:
    """Fixture for an authenticated client."""
    client.headers["Authorization"] = f"Bearer {get_auth_token}"
    return client