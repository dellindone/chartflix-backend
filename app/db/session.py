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

# Get database session
async def get_db():
    if not SessionFactory:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    async with SessionFactory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Database error")