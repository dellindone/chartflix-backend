from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.user import UserRole
from app.modules.admin.repository import admin_repo
from app.schemas.admin import UpdateRoleRequest

from app.models.alert import Alert
from app.models.recommendation import Recommendation

class AdminService:

    async def get_all_users(self, db: AsyncSession):
        return await admin_repo.get_all_users(db)
    
    async def update_role(self, db: AsyncSession, user_id: str, data: UpdateRoleRequest):
        user = await admin_repo.get_user_by_id(db, user_id)
        if not user: raise NotFoundException("User Not Found")

        if user.role == data.role.value:
            raise BadRequestException(message=f"User is already {data.role.value}")
        
        if data.role == UserRole.ADMIN:
            raise BadRequestException("Cannot assign admin role through API. Use database directly.")
        
        if data.role == UserRole.ANALYST:
            existing = await admin_repo.get_analyst_by_user_id(db, user_id)
            if not existing:
                await admin_repo.create_analyst_profile(db, user_id, tag="Analyst")
        
        if data.role != UserRole.ANALYST:
            analyst = await admin_repo.get_analyst_by_user_id(db, user_id)
            if analyst:
                await admin_repo.delete_analyst_profile(db, analyst)
        return await admin_repo.update_role(db, user, data.role.value)
    
    async def delete_content(self, db: AsyncSession, contend_id: str):
        alert = await db.execute(select(Alert).where(Alert.id == contend_id))
        alert = alert.scalar_one_or_none()
        if alert:
            await db.delete(alert)
            await db.commit()
            return
        
        reco = await db.execute(select(Recommendation).where(Recommendation.id == contend_id))
        reco = reco.scalar_one_or_none()
        if reco:
            await db.delete(reco)
            await db.commit()
            return
        
        raise NotFoundException("Content not found")
    
admin_service = AdminService()
