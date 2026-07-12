import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_status_returns_version(client: AsyncClient) -> None:
    response = await client.get("/api/v1/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"
    assert payload["tenant_id"] is None


@pytest.mark.asyncio
async def test_status_echoes_tenant_header(client: AsyncClient) -> None:
    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.get("/api/v1/status", headers={"X-Tenant-ID": tenant_id})
    assert response.status_code == 200
    assert response.json()["tenant_id"] == tenant_id


@pytest.mark.asyncio
async def test_invalid_tenant_header_rejected(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Tenant-ID": "not-a-uuid"})
    assert response.status_code == 400

