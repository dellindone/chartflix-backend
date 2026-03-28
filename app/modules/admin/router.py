from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.modules.admin import controller
from app.schemas.admin import UpdateRoleRequest

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin"))
):
    return await controller.get_all_users(db)


@router.patch("/users/{user_id}/role")
async def update_role(
    user_id: str,
    data: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin"))
):
    return await controller.update_role(db, user_id, data)


@router.delete("/content/{content_id}", status_code=204)
async def delete_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin"))
):
    return await controller.delete_content(db, content_id)