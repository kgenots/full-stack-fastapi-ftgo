import asyncio
from typing import Any

from data_access.repository.cache_repository import CacheRepository
from data_access.repository.db_repository import DatabaseRepository

from config import BaseConfig
from data_access import get_logger

async def setup() -> None:
    from config.db import PostgresConfig
    logger = get_logger()
    await CacheRepository.initialize()
    logger.info("Connected to Redis")
    await DatabaseRepository.initialize()
    logger.info("Connected to Postgres")
    
async def teardown() -> None:
    logger = get_logger()
    await CacheRepository.terminate()
    logger.info("Disconnected from cache")
    await DatabaseRepository.terminate()
    logger.info("Disconnected from database")
