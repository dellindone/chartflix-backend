from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import AccessTokenResponse, RefreshTokenRequest, SignupRequest, SignInRequest, Token, LogoutRequest, LogoutResponse
from app.modules.auth.service import register_user, authenticate_user, refresh_access_token, logout_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/signup', response_model=Token)
async def register(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await register_user(data, db)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/signin', response_model=Token)
async def login(data: SignInRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await authenticate_user(data, db)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post('/refresh', response_model=AccessTokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_access_token(data, db)

@router.post('/logout', response_model=LogoutResponse)
async def logout(refresh_token: LogoutRequest, db: AsyncSession = Depends(get_db)):
    return await logout_user(db, refresh_token)

