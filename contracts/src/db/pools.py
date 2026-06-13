import asyncpg
from loguru import logger
from src.settings import settings

_write_pool: asyncpg.Pool | None = None
_read_pool: asyncpg.Pool | None = None


async def init_pools():
    global _write_pool, _read_pool

    dsn_write = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    dsn_read = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_REPLICA_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

    _write_pool = await asyncpg.create_pool(
        dsn_write,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
    )
    logger.info("✅ Write pool initialized")

    _read_pool = await asyncpg.create_pool(
        dsn_read,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
    )
    logger.info("✅ Read pool initialized")


async def close_pools():
    global _write_pool, _read_pool
    if _write_pool:
        await _write_pool.close()
        logger.info("🛑 Write pool closed")
    if _read_pool:
        await _read_pool.close()
        logger.info("🛑 Read pool closed")


def get_write_pool() -> asyncpg.Pool:
    assert _write_pool is not None, "Write pool not initialized"
    return _write_pool


def get_read_pool() -> asyncpg.Pool:
    assert _read_pool is not None, "Read pool not initialized"
    return _read_pool
