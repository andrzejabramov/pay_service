"""
Базовые тесты для webhook эндпоинтов alpha_hook
"""

import pytest
from httpx import AsyncClient
from typing import Dict, Any


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Тест health check endpoint"""
    response = await client.get("/webhook/test")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_valid_webhook(client: AsyncClient, valid_payload: Dict[str, Any]):
    """Тест валидного webhook"""
    response = await client.post(
        "/webhook/callback",
        json=valid_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "request_id" in data


@pytest.mark.asyncio
async def test_invalid_webhook(client: AsyncClient, invalid_payload: Dict[str, Any]):
    """Тест невалидного webhook (должен вернуть 200, но с ошибкой в логах)"""
    response = await client.post(
        "/webhook/callback",
        json=invalid_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "request_id" in data