import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "statement_cache_size": 0
    })