import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from main import app
from httpx import AsyncClient

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency for tests."""
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Set up and tear down the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Removed custom event_loop fixture, relying on pytest-asyncio's default

@pytest.fixture(scope="session")
async def _client_instance() -> AsyncGenerator[AsyncClient, None]:
    """Helper fixture to create an asynchronous test client instance for the session."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session")
def client(_client_instance: AsyncClient) -> AsyncClient:
    """Provides the AsyncClient instance, ensuring it's properly awaited by pytest-asyncio."""
    return _client_instance

@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def create_test_merchant(client: AsyncClient) -> dict:
    """Helper fixture to create a merchant for tests."""
    # client is already the AsyncClient instance due to the refactor
    merchant_data = {
        "business_name": "Test Merchant",
        "owner_name": "Test Owner",
        "email": "test_merchant@example.com",
        "phone": "254700000000",
        "business_type": "retail",
        "mpesa_till_number": "TESTTILL"
    }
    response = await client.post("/api/v1/merchants", json=merchant_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture
async def create_test_user(client: AsyncClient, create_test_merchant: dict) -> dict:
    """Helper fixture to create a user linked to a merchant for tests."""
    # client is already the AsyncClient instance
    merchant = await create_test_merchant # This still needs await as it's an async fixture
    merchant_id = merchant["id"]
    user_data = {
        "email": "test_user@example.com",
        "password": "password123",
        "name": "Test User",
        "merchant_id": merchant_id
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture
async def get_auth_token(client: AsyncClient, create_test_user: dict) -> str:
    """Helper fixture to get an auth token for a test user."""
    # client is already the AsyncClient instance
    user = await create_test_user # This still needs await
    login_data = {
        "email": user["email"],
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
async def authenticated_client(client: AsyncClient, get_auth_token: str) -> AsyncClient:
    """Fixture for an authenticated client."""
    # client is already the AsyncClient instance
    token = await get_auth_token # This still needs await
    client.headers["Authorization"] = f"Bearer {token}"
    return client