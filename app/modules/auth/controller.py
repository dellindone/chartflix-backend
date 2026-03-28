from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.response import success

auth_service = AuthService()

async def register(db: AsyncSession, data: RegisterRequest) -> dict:
    access_token, refresh_token = await auth_service.register(db, data)
    token_data = TokenResponse(access_token=access_token, refresh_token=refresh_token)
    return success(data=token_data.model_dump(), message="Registration successful")

async def login(db: AsyncSession, data: LoginRequest) -> dict:
    access_token, refresh_token = await auth_service.login(db, data)
    token_data = TokenResponse(access_token=access_token, refresh_token=refresh_token)
    return success(data=token_data.model_dump(), message="Login successful")

async def refresh(db: AsyncSession, refresh_token: str) -> dict:
    access_token, refresh_token = await auth_service.refresh(db, refresh_token)
    token_data = TokenResponse(access_token=access_token, refresh_token=refresh_token)
    return success(data=token_data.model_dump(), message="Token refreshed")

async def logout(db: AsyncSession, refresh_token: str) -> dict:
    await auth_service.logout(db, refresh_token)
    return success(data=None, message="Logout successful")
