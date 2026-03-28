from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users import controller
from app.models.user import User
from app.schemas.user import UpdateProfileRequest

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return await controller.get_profile(current_user)

@router.patch("/me")
async def update_profile(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.update_profile(db, current_user, data)