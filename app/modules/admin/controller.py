from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.admin.service import admin_service
from app.schemas.admin import UpdateRoleRequest
from app.schemas.user import UserResponse
from app.utils.response import success


async def get_all_users(db: AsyncSession) -> dict:
    users = await admin_service.get_all_users(db)
    data = [UserResponse.model_validate(u).model_dump() for u in users]
    return success(data=data, message="Users fetched")


async def update_role(db: AsyncSession, user_id: str, data: UpdateRoleRequest) -> dict:
    user = await admin_service.update_role(db, user_id, data)
    return success(data=UserResponse.model_validate(user).model_dump(), message="Role updated")


async def delete_content(db: AsyncSession, content_id: str) -> dict:
    await admin_service.delete_content(db, content_id)
    return success(data=None, message="Content deleted")