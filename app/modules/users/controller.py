from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.users.service import user_service
from app.utils.response import success
from app.schemas.user import UpdateProfileRequest, UserResponse

async def get_profile(current_user: User) -> dict:
    return success(
        data=UserResponse.model_validate(current_user).model_dump(),
        message="Profile Fetched"
    )

async def update_profile(db: AsyncSession, current_user: User, data: UpdateProfileRequest) -> dict:
    user = await user_service.update_profile(db, current_user.id, data)
    return success(
        data=UserResponse.model_validate(user).model_dump(),
        message="Profile Update"
    )