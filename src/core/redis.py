from typing import AsyncGenerator

from redis.asyncio import Redis

from src.loggers.loggers import logger

redis = None


async def get_redis() -> AsyncGenerator:
    global redis
    if redis is None:
        redis = await Redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
        logger.info("🔌 Connected to Redis")
    yield redis
