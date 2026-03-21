from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import engine

SessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,   
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# dependency
async def get_db():
    async with SessionFactory() as session:
        yield session