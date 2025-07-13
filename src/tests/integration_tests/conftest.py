import asyncio

import pytest

from src.core.config import settings
from src.db.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    if settings.MODE == "TEST":
        asyncio.run(_reset_db())


async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
