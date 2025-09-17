import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from app.core.database import Base, get_db
from main import app
from httpx import AsyncClient
from app.models.merchant import Merchant
from app.models.user import User
from app.services.auth_service import AuthService
import os # Import os

# Use a separate test database
# IMPORTANT: Use 'db' as the hostname to connect to the PostgreSQL service within Docker Compose
# Read the DATABASE_URL from environment variables, which is set correctly in docker-compose.yml
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:password@db-test:5432/test_db")

# These will be initialized in the session-scoped fixture
_test_engine: AsyncEngine | None = None
_TestSessionLocal: async_sessionmaker[AsyncSession] | None = None

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency for tests."""
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        try:
            yield session
        finally:
            # Rollback any changes after each test to ensure isolation
            await session.rollback() 
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Set up and tear down the test database."""
    global _test_engine, _TestSessionLocal
    
    _test_engine = create_async_engine(
        TEST_DATABASE_URL, # Use the updated TEST_DATABASE_URL
        echo=False,
        future=True
    )
    _TestSessionLocal = async_sessionmaker(
        _test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Explicitly open and close connection for schema creation/deletion
    conn = await _test_engine.connect()
    try:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    finally:
        await conn.close() # Ensure the connection is closed
    
    await asyncio.sleep(0.1) # Small delay to ensure resources are freed
    yield
    
    # Explicitly open and close connection for schema teardown
    conn = await _test_engine.connect()
    try:
        await conn.run_sync(Base.metadata.drop_all)
    finally:
        await conn.close() # Ensure the connection is closed
    
    await _test_engine.dispose()
    _test_engine = None
    _TestSessionLocal = None

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    # This fixture now relies on _TestSessionLocal being set up by setup_test_db
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        try:
            yield session
        finally:
            # Rollback any changes after each test to ensure isolation
            await session.rollback() 
            await session.close()

@pytest_asyncio.fixture
async def create_test_merchant(db: AsyncSession) -> Merchant:
    """Helper fixture to create a merchant directly in the database."""
    merchant = Merchant(
        business_name="Test Merchant",
        owner_name="Test Owner",
        email="test_merchant@example.com",
        phone="254700000000",
        business_type="retail",
        mpesa_till_number="TESTTILL"
    )
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)
    return merchant

@pytest_asyncio.fixture
async def create_test_user(db: AsyncSession, create_test_merchant: Merchant) -> User:
    """Helper fixture to create a user directly in the database."""
    auth_service = AuthService(db) # Instantiate AuthService with the current session
    hashed_password = auth_service.get_password_hash("password123")
    user = User(
        email="test_user@example.com",
        hashed_password=hashed_password,
        name="Test User",
        merchant_id=create_test_merchant.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest_asyncio.fixture
async def get_auth_token(client: AsyncClient, create_test_user: User) -> str:
    """Helper fixture to get an auth token for a test user."""
    login_data = {
        "email": create_test_user.email,
        "password": "password123" # The password used when creating the user
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, get_auth_token: str) -> AsyncClient:
    """Fixture for an authenticated client."""
    client.headers["Authorization"] = f"Bearer {get_auth_token}"
    return client