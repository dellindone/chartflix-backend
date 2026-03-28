from fastapi import APIRouter, Depends
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.schemas.user import UserProfileResponse
from app.modules.auth.deps import get_current_user
from app.core.security import verify_token
from app.model.user.models import User


security = HTTPBearer()
router = APIRouter(prefix="/user", tags=["users"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user = Depends(get_current_user)):
    return current_user

@router.put("update-profile", response_model=UserProfileResponse)
async def update_user_profile(
    data: UserProfileResponse,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    # get user id
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update = await db.execute(update(User).where(User.id == user_id).values(
        name=data.name,
        phone=data.phone
    ).returning(User))
    await db.commit()
    updated_user = update.scalar_one_or_none()
    return updated_user