"""
Pytest fixtures for Secret Message tests
"""
import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests"""
    return "asyncio"


@pytest.fixture(scope="function")
async def client():
    """
    Create async test client for FastAPI app.
    
    This is a simple client that doesn't use database isolation.
    Tests should clean up after themselves.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
    ) as ac:
        yield ac
