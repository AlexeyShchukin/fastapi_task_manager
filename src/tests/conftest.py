import os

from dotenv import load_dotenv
import pytest_asyncio

from src.core.redis import create_redis

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env.test"))


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    """
    Provides an asynchronous Redis client for tests.
    Creates a new client, clears the database before each test
    and closes the connection after.
    """
    client = await create_redis()
    try:
        await client.flushdb()
        yield client
    finally:
        await client.close()
