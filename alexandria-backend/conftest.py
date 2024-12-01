import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from main_maria import app

DATABASE_URL = "mysql+aiomysql://root:test123@localhost:3306/experiments"

# Async engine
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope='session')
def event_loop():
    """Create an event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    """Provide a database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client():
    """Provide an HTTP client for testing."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://0.0.0.0:8000") as client:
            yield client
