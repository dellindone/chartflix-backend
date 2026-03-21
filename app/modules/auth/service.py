from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.schemas.auth import SignupRequest, LogoutRequest

from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.model.user.models import User
from app.model.token.token import Token

async def register_user(signup_request: SignupRequest, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.email == signup_request.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise Exception("User with this email already exists")
    
    if signup_request.password != signup_request.confirm_password:
        raise Exception("Passwords do not match")
    
    user = User(
        email=signup_request.email,
        hashed_password=hash_password(signup_request.password),
        name=signup_request.fullname,
        phone=signup_request.phone
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    await store_refresh_token(user.id, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def authenticate_user(data, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise Exception("Invalid email or password")
    
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    await store_refresh_token(user.id, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def store_refresh_token(user_id, refresh_token, db: AsyncSession):
    token_entry = Token(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(token_entry)
    await db.commit()

async def refresh_access_token(data, db: AsyncSession):
    refresh_token = data.refresh_token
    result = await db.execute(select(Token).where(Token.refresh_token == refresh_token))
    token_entry = result.scalar_one_or_none()
    if not token_entry or not token_entry.expires_at > datetime.now(timezone.utc):
        raise Exception("Invalid or expired refresh token")
    
    new_access_token = create_access_token({"sub": token_entry.user_id})
    return {"access_token": new_access_token, "token_type": "bearer"}

async def logout_user(db: AsyncSession, refresh_token: LogoutRequest):
    result = await db.execute(select(Token).where(Token.refresh_token == refresh_token.refresh_token))
    token_entry = result.scalar_one_or_none()

    if not token_entry:
        raise HTTPException(status_code=404, detail="Token not found")
    
    await db.delete(token_entry)
    await db.commit()
    return {"message": "Logged out successfully"}
    return {"message": "Logged out successfully"}
