import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_invalid_tenant_header_rejected(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Tenant-ID": "not-a-uuid"})
    assert response.status_code == 400
