from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logger import logger
from app.core.exceptions import AppException, app_exception_handler

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.APP_NAME}")

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "app": settings.APP_NAME}


from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.alerts.router import router as alerts_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.admin.router import router as admin_router
from app.modules.webhook.router import router as webhook_router
from app.modules.websocket.router import router as websocket_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(webhook_router, prefix="/api/v1")
app.include_router(websocket_router)