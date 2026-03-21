import logging
import sys

# Setup logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting app imports...")
    
    from app.db.base import Base
    logger.info("✓ Imported Base")
    
    from app.db.engine import engine
    logger.info("✓ Imported engine")
    
    from app.modules.auth.router import router as auth_router
    logger.info("✓ Imported auth_router")
    
    from app.modules.user.router import router as user_router
    logger.info("✓ Imported user_router")

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    logger.info("All imports successful, creating FastAPI app...")
    
except Exception as e:
    logger.error(f"Import error: {e}", exc_info=True)
    raise

app = FastAPI(
    title="Chartflix Backend API",
    description="API for Chartflix, a Stock Alert tracking application"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    try:
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified")
        else:
            logger.warning("Database engine not initialized")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        # Don't fail startup, let the app start anyway

app.include_router(auth_router)
app.include_router(user_router)

logger.info("FastAPI app created successfully")