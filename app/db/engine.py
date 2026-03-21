import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import DATABASE_URL

logger = logging.getLogger(__name__)

logger.info(f"[ENGINE] DATABASE_URL available: {bool(DATABASE_URL)}")

try:
    if DATABASE_URL:
        # Mask password in logs for security
        masked_url = DATABASE_URL.split("://")[0] + "://***:***@" + DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "***"
        logger.info(f"[ENGINE] Creating async engine with URL: {masked_url}")
        
        engine = create_async_engine(
            DATABASE_URL,
            connect_args={
                "statement_cache_size": 0,
                "timeout": 30  # 30 second connection timeout
            },
            echo=False,  # Set to True for SQL debugging in test
            pool_size=5,
            max_overflow=10,
        )
        logger.info("[ENGINE] ✓ Database engine created successfully")
    else:
        logger.warning("[ENGINE] ✗ DATABASE_URL is not set, database engine is None")
        logger.warning("[ENGINE] Check that DATABASE_URL or database components (HOST, DB_PORT, USERNAME, PASSWORD, DATABASE) are set")
        engine = None
except Exception as e:
    logger.error(f"[ENGINE] ✗ Failed to create database engine: {e}", exc_info=True)
    engine = None