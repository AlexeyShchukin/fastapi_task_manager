from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.redis import create_redis
from src.loggers.loggers import logger
from src.services.token_service import TokenService
from src.utils.unit_of_work import UnitOfWork

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    @scheduler.scheduled_job("cron", hour=3, minute=0)
    async def clean_sessions():
        token_service = TokenService(UnitOfWork())
        await token_service.cleanup_expired_and_used_sessions()

    scheduler.start()
    logger.info("Starting lifespan")
    yield
    scheduler.shutdown()
    logger.info("Stopping lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await create_redis()
    app.state.redis = redis
    yield
    await app.state.redis.close()
