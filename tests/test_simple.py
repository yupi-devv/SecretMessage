"""
Simple integration tests for Secret Message API
"""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="function")
async def client():
    """Create async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_page(client):
    """Test main page loads"""
    response = await client.get("/")
    assert response.status_code == 200
    assert b"Secret Message" in response.content


@pytest.mark.asyncio
async def test_create_message_text_only(client):
    """Test creating message with text only - SIMPLE"""
    response = await client.post(
        "/v1/create",
        data={"msgtext": "Test secret message", "expiry_delta_minutes": ""},
    )
    assert response.status_code == 200
    data = response.json()
    assert "url_code" in data
    assert data["message_text"] == "Test secret message"


@pytest.mark.asyncio
async def test_create_message_empty_fails(client):
    """Test that empty message without files fails"""
    response = await client.post(
        "/v1/create", data={"msgtext": "", "expiry_delta_minutes": ""}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_docs(client):
    """Test API documentation is accessible"""
    response = await client.get("/docs")
    assert response.status_code == 200


# Simple sanity test
def test_basic():
    """Basic sanity test"""
    assert 1 == 1
