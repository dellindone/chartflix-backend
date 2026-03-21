from app.db.base import Base
from app.db.engine import engine
from app.modules.auth.router import router as auth_router
from app.modules.user.router import router as user_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
    print("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)
app.include_router(user_router)

import os
import uvicorn
print("PORT:", os.environ.get("PORT"))
port = int(os.environ.get("PORT", 8000))

uvicorn.run("main:app", host="0.0.0.0", port=port)