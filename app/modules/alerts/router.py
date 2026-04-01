from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts import controller
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role, require_approved
from app.models.user import User
from app.schemas.alert import CreateAlertRequest, UpdateAlertRequest

router = APIRouter(prefix = "/alerts", tags=["Alerts"])

@router.get("")
async def get_all(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_approved)
):
    return await controller.get_all(db, current_user, page, limit)

@router.get("/my")
async def get_my_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    return await controller.get_my_alerts(db, current_user)

@router.get("/{alert_id}")
async def get_one(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_approved)
):
    return await controller.get_one(db, alert_id, current_user)

@router.post("", status_code=201)
async def create(
    data: CreateAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.create(db, data, current_user)

@router.patch("/{alert_id}")
async def update(
    alert_id: str,
    data: UpdateAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.update(db, alert_id, data, current_user)

@router.patch("/{alert_id}/publish")
async def toggle_publish(
    alert_id: str,
    db: AsyncSession=Depends(get_db),
    current_user: User=Depends(require_role("analyst", "admin"))
):
    return await controller.toggle_publish(db, alert_id, current_user)

@router.delete("/{alert_id}", status_code=204)
async def delete(alert_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_role("admin"))):
    return await controller.delete(db, alert_id)
