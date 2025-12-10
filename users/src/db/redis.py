import redis.asyncio as aioredis

from src.settings import settings

redis = aioredis.from_url(str(settings.redis_url), decode_responses=True)