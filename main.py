from fastapi import FastAPI
from app.modules.auth.router import router as auth_router

app = FastAPI(
            title="Chartflix Backend API",
            description="API for Chartflix, a Stock Alert tracking application"
    )

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(auth_router)