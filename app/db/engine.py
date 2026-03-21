from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

DATABASE_URL = f"""postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"""
engine = create_async_engine(DATABASE_URL)