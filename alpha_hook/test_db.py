import asyncio
import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import settings
from loguru import logger
import asyncpg


async def test_db_connection():
    """Тест подключения к БД (мастер и реплика)"""
    logger.info("Testing database connection...")

    try:
        # Тест write pool (мастер)
        conn_write = await asyncpg.connect(dsn=str(settings.database_write_url), timeout=10)
        await conn_write.execute("SELECT 1")
        await conn_write.close()
        logger.success("✅ Write pool (master) connection OK")

        # Тест read pool (реплика)
        conn_read = await asyncpg.connect(dsn=str(settings.database_read_url), timeout=10)
        await conn_read.execute("SELECT 1")
        await conn_read.close()
        logger.success("✅ Read pool (replica) connection OK")

        return True

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Минимальная настройка логгера (только консоль)
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>"
    )

    success = asyncio.run(test_db_connection())
    sys.exit(0 if success else 1)