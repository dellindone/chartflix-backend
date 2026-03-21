import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

try:
    if DATABASE_URL:
        engine = create_async_engine(
            DATABASE_URL,
            connect_args={
                "statement_cache_size": 0,
                "max_cached_statement_lifetime": 0,
                "max_cacheable_statement_size": 0,
            },
            pool_size=1,
            max_overflow=0,
            echo=False
        )
        logger.info("Database engine created successfully")
    else:
        logger.warning("DATABASE_URL is not set, database engine is None")
        engine = None
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None