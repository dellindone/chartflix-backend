from datetime import timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token
from app.models.user import User
from app.modules.auth.repository import auth_repo
from app.schemas.auth import LoginRequest, RegisterRequest

class AuthService:
    
    async def _issue_tokens(self, db: AsyncSession, user: User) -> tuple[str, str]:
        access_token = create_access_token(user_id=user.id, role=user.role)
        refresh_token = create_refresh_token(user_id=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await auth_repo.save_refresh_token(db, user_id=user.id, token=refresh_token, expires_at=expires_at)
        return access_token, refresh_token

    async def register(self, db: AsyncSession, data: RegisterRequest) -> tuple[User, str, str]:
        existing = await auth_repo.get_user_by_email(db, data.email)
        if existing:
            raise ConflictException("Email already registered")
        
        hashed = hash_password(data.password)
        user = await auth_repo.create_user(db, email=data.email, password=hashed, name=data.name, phone=data.phone, location=data.location)
        access_token, refresh_token = await self._issue_tokens(db, user)
        return access_token, refresh_token

    async def login(self, db: AsyncSession, data: LoginRequest) -> tuple[str, str]:
        user = await auth_repo.get_user_by_email(db, data.email)
        if not user or not verify_password(data.password, user.password):
            raise UnauthorizedException("Invalid email or password")
        
        access_token, refresh_token = await self._issue_tokens(db, user)
        return access_token, refresh_token

    async def logout(self, db: AsyncSession, refresh_token: str) -> None:
        await auth_repo.delete_refresh_token(db, refresh_token)

    async def refresh(self, db: AsyncSession, refresh_token: str) -> tuple[str, str]:
        token_data = await auth_repo.get_refresh_token(db, refresh_token)
        if not token_data:
            raise UnauthorizedException("Invalid refresh token")
        
        if token_data.expires_at < datetime.now(timezone.utc):
            await auth_repo.delete_refresh_token(db, refresh_token)
            raise UnauthorizedException("Session Expired, please login again")
        
        user = await auth_repo.get_user_by_id(db, token_data.user_id)
        if not user:
            raise UnauthorizedException("Account not found")
        return create_access_token(user_id=user.id, role=user.role), refresh_token
