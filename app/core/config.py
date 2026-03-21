import os
import logging

logger = logging.getLogger(__name__)

# Only load .env file if it exists (for local development)
# Railway sets environment variables directly, so we don't load .env there
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded .env file")
except:
    logger.info("No .env file to load (normal on Railway)")

# DATABASE_URL - Priority: 1) Direct DATABASE_URL var, 2) Build from components
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    logger.info("✓ DATABASE_URL found from environment")
else:
    logger.info("DATABASE_URL not found, attempting to build from components...")
    
    # Log what we have
    HOST = os.getenv("HOST")
    DB_PORT = os.getenv("DB_PORT")
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    DATABASE = os.getenv("DATABASE")
    
    logger.info(f"  HOST: {bool(HOST)}")
    logger.info(f"  DB_PORT: {bool(DB_PORT)}")
    logger.info(f"  USERNAME: {bool(USERNAME)}")
    logger.info(f"  PASSWORD: {bool(PASSWORD)}")
    logger.info(f"  DATABASE: {bool(DATABASE)}")
    
    try:
        HOST = HOST or "localhost"
        DB_PORT = DB_PORT or "5432"
        USERNAME = USERNAME or "postgres"
        PASSWORD = PASSWORD or ""
        DATABASE = DATABASE or "postgres"
        
        DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{DB_PORT}/{DATABASE}?ssl=require"
        logger.info("✓ Database URL built from environment variables")
    except Exception as e:
        logger.error(f"✗ Failed to build DATABASE_URL: {e}")
        DATABASE_URL = None

logger.info(f"DATABASE_URL configured: {bool(DATABASE_URL)}")

# JWT configuration with safe defaults
try:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        SECRET_KEY = "your-secret-key-change-in-production"
        logger.warning("⚠ SECRET_KEY not set, using default (INSECURE)")
    else:
        logger.info("✓ SECRET_KEY configured")
    
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    logger.info(f"✓ JWT Config: {ALGORITHM}, access_expire={ACCESS_TOKEN_EXPIRE_MINUTES}m, refresh_expire={REFRESH_TOKEN_EXPIRE_DAYS}d")
except Exception as e:
    logger.error(f"Error parsing JWT configuration: {e}")
    raise