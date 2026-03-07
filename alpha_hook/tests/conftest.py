"""
Конфигурация pytest и общие фикстуры для тестов alpha_hook
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from asyncpg import Pool

from src.main import app
from src.db.pools import init_pools, close_pools


# Мок для пула БД
class MockPool:
    """Мок-объект для asyncpg.Pool"""

    def __init__(self):
        self._maxsize = 10

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def acquire(self):
        """Метод для получения соединения"""
        return self

    async def __aenter__(self):
        return MockConnection()

    async def __aexit__(self, *args):
        pass


class MockConnection:
    """Мок-объект для asyncpg.Connection"""

    async def fetchval(self, query, *args):
        """Мок для fetchval"""
        # Имитируем ответ от БД
        if "save_callback_log" in query:
            return {"ans": "ok", "id": "test-uuid"}
        return None

    async def execute(self, query, *args):
        """Мок для execute"""
        return "INSERT 0 1"

    def transaction(self):
        """Мок для транзакций"""
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def mock_db_pools():
    """Мокируем пулы БД для тестов"""
    with patch('src.db.pools.create_pool', new_callable=AsyncMock) as mock_create_pool:
        # Настраиваем мок для create_pool
        mock_pool = MockPool()
        mock_create_pool.return_value = mock_pool

        # Подменяем get_write_pool
        with patch('src.db.pools.get_write_pool', return_value=mock_pool):
            yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура HTTP-клиента"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_payload() -> Dict[str, Any]:
    """Валидный payload"""
    return {
        "orderNumber": "DRV_TEST_001",
        "mdOrder": "3ff6962a-7dcc-4283-ab50-a6d7dd3386fe",
        "operation": "deposited",
        "status": 1,
        "amount": 150000,
        "checksum": "TEST"
    }


@pytest.fixture
def invalid_payload() -> Dict[str, Any]:
    """Невалидный payload"""
    return {
        "some": "field",
        "another": "value"
    }