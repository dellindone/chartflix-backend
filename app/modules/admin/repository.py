from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.analyst import Analyst

class AdminRepository:

    async def get_all_users(self, db: AsyncSession) -> list[User]:
        users = await db.execute(select(User).order_by(User.created_at))
        return users.scalars().all()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        user = await db.execute(select(User).where(User.id == user_id))
        return user.scalar_one_or_none()
    
    async def get_analyst_by_user_id(self, db: AsyncSession, user_id: str) -> Analyst:
        analyst = await db.execute(select(Analyst).where(Analyst.user_id == user_id))
        return analyst.scalar_one_or_none()

    async def update_role(self, db: AsyncSession, user: User, role: str) -> User:
        user.role = role
        await db.commit()
        await db.refresh(user)
        return user
    
    async def create_analyst_profile(self, db: AsyncSession, user_id: str, tag: str) -> Analyst:
        analyst = Analyst(user_id=user_id, tag=tag)
        db.add(analyst)
        await db.commit()
        await db.refresh(analyst)
        return analyst
    
    async def delete_analyst_profile(self, db: AsyncSession, analyst: Analyst) -> None:
        await db.delete(analyst)
        await db.commit()

admin_repo = AdminRepository()
