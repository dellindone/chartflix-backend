from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User

class UserRepository:

    async def get_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def update(self, db: AsyncSession, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user

user_repo = UserRepository()