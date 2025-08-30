import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.main import app
from httpx import AsyncClient

import sys
import os

# Add the backend directory to sys.path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/test_db"

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

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an asynchronous test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac