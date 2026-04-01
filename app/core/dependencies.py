from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or expired")
    
    user_id = payload.get("sub")    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in [r.lower() for r in roles]:
            raise HTTPException(
                status_code=403,
                detail=f"User role '{current_user.role}' does not have access to this resource"
            )
        return current_user
    return role_checker

async def require_approved(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "admin":
        return current_user
    if not current_user.is_approved:
        raise HTTPException(status_code=403, detail="Access not approved. Please contact admin.")
    return current_user