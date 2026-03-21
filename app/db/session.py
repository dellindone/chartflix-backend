from sqlalchemy.orm import sessionmaker
from app.db.engine import engine

SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# dependency
async def get_db():
    async with SessionFactory() as session:
        yield session