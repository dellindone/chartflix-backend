from app.db.base import Base
from app.db.engine import engine
from app.modules.auth.router import router as auth_router
from app.modules.user.router import router as user_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't fail startup, let the app start anyway

app.include_router(auth_router)
app.include_router(user_router)

if __name__ == "__main__":
    import os
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)