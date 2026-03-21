from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import engine
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

if engine:
    SessionFactory = sessionmaker(
        bind=engine,
        class_=AsyncSession,   
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
else:
    SessionFactory = None
    logger.warning("Database engine is not initialized, sessions will not work")

# dependency
async def get_db():
    if not SessionFactory:
        logger.error("Attempted to get_db but SessionFactory is None")
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        async with SessionFactory() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")