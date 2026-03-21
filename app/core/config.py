import os
import logging

logger = logging.getLogger(__name__)

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# DATABASE_URL - Priority: 1) Direct DATABASE_URL var, 2) Build from components
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    HOST = os.getenv("HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    USERNAME = os.getenv("USERNAME", "postgres")
    PASSWORD = os.getenv("PASSWORD", "")
    DATABASE = os.getenv("DATABASE", "postgres")
    
    DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{DB_PORT}/{DATABASE}?ssl=require"

logger.info(f"Database URL configured: {bool(DATABASE_URL)}")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "your-secret-key-change-in-production"
    logger.warning("SECRET_KEY not set, using default")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))