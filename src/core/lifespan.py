from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.loggers.loggers import logger
from src.services.token_service import TokenService
from src.utils.unit_of_work import UnitOfWork

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    @scheduler.scheduled_job("interval", minutes=15)
    async def clean_sessions():
        token_service = TokenService(UnitOfWork())
        await token_service.cleanup_expired_sessions()

    scheduler.start()
    logger.info("Starting lifespan")
    yield
    scheduler.shutdown()
    logger.info("Stopping lifespan")
