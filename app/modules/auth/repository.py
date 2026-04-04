import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user import User
from app.models.refresh_token import RefreshToken

def hash_token(token) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

class AuthRepository:
    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, email: str, password: str, name: str, phone: str, location: str) -> User:
        user = User(
            email=email,
            password=password,
            name=name,
            phone=phone,
            location=location,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_refresh_token(self, db: AsyncSession, token: str) -> RefreshToken | None:
        token = await db.execute(select(RefreshToken).where(RefreshToken.token == hash_token(token)))
        return token.scalar_one_or_none()

    async def save_refresh_token(self, db: AsyncSession, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token=hash_token(token),
            expires_at=expires_at
        )
        db.add(token)
        await db.commit()

    async def delete_refresh_token(self, db: AsyncSession, token: str) -> None:
        await db.execute(delete(RefreshToken).where(RefreshToken.token == hash_token(token)))
        await db.commit()

auth_repo = AuthRepository()