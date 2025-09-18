import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from app.core.database import Base, get_db
from main import app
from httpx import AsyncClient
from app.models.merchant import Merchant, BusinessType
from app.models.user import User
from app.services.auth_service import AuthService
import os # Import os
import uuid

# Use a separate test database
# IMPORTANT: Use 'db' as the hostname to connect to the PostgreSQL service within Docker Compose
# Read the DATABASE_URL from environment variables, which is set correctly in docker-compose.yml
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:password@db-test:5432/test_db")

# These will be initialized in the function-scoped fixture
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
            await session.rollback()
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Set up and tear down the test database per test function."""
    global _test_engine, _TestSessionLocal
    
    _test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    _TestSessionLocal = async_sessionmaker(
        _test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    conn = await _test_engine.connect()
    try:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    finally:
        await conn.close()

    yield

    conn = await _test_engine.connect()
    try:
        await conn.run_sync(Base.metadata.drop_all)
    finally:
        await conn.close()

    await _test_engine.dispose()
    _test_engine = None
    _TestSessionLocal = None

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture
async def create_test_merchant() -> Merchant:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        unique = uuid.uuid4().hex[:8]
        merchant = Merchant(
            business_name=f"Test Merchant {unique}",
            owner_name="Test Owner",
            email=f"test_merchant_{unique}@example.com",
            phone="254700000000",
            business_type=BusinessType.RETAIL,
            mpesa_till_number=f"TESTTILL{unique}"
        )
        session.add(merchant)
        await session.commit()
        await session.refresh(merchant)
        return merchant

@pytest_asyncio.fixture
async def create_test_user(create_test_merchant: Merchant) -> User:
    if _TestSessionLocal is None:
        raise RuntimeError("TestSessionLocal not initialized. Ensure setup_test_db fixture runs.")
    async with _TestSessionLocal() as session:
        auth_service = AuthService(session)
        hashed_password = auth_service.get_password_hash("password123")
        user = User(
            email=f"test_user_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=hashed_password,
            name="Test User",
            merchant_id=create_test_merchant.id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

@pytest_asyncio.fixture
async def get_auth_token(client: AsyncClient, create_test_user: User) -> str:
    login_data = {
        "email": create_test_user.email,
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, get_auth_token: str) -> AsyncClient:
    client.headers["Authorization"] = f"Bearer {get_auth_token}"
    return client