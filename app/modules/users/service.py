from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.users.repository import user_repo
from app.schemas.user import UpdateProfileRequest

class UserService:
    async def update_profile(self, db: AsyncSession, user_id: str, data: UpdateProfileRequest):
        user = await user_repo.get_by_id(db, user_id=user_id)
        if not user:
            raise NotFoundException("User Not Found")
        
        updates = data.model_dump(exclude_unset=True)
        return await user_repo.update(db, user, updates)
    
user_service = UserService()