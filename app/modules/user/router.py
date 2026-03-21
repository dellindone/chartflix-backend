from fastapi import APIRouter, Depends

from app.schemas.user import UserProfileResponse
from app.modules.auth.deps import get_current_user

router = APIRouter(prefix="/user", tags=["users"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user = Depends(get_current_user)):
    return current_user
