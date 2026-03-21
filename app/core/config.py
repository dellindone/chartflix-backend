from dotenv import load_dotenv
import os

load_dotenv()

# If DATABASE_URL is provided as env var, use it directly (for Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

# Otherwise, build it from components (for local development)
if not DATABASE_URL:
    HOST = os.getenv("HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT") or os.getenv("PORT", "5432")  # Try DB_PORT first, then PORT
    USERNAME = os.getenv("USERNAME", "postgres")
    PASSWORD = os.getenv("PASSWORD", "")
    DATABASE = os.getenv("DATABASE", "postgres")
    
    try:
        DATABASE_URL = f"postgresql+asyncpg://{USERNAME}:{PASSWORD}@{HOST}:{DB_PORT}/{DATABASE}?ssl=require"
    except Exception as e:
        print(f"Error building DATABASE_URL: {e}")
        DATABASE_URL = None

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))