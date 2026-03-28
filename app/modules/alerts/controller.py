from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.alerts.service import alert_service
from app.schemas.alert import CreateAlertRequest, AlertResponse, UpdateAlertRequest
from app.utils.pagination import get_pagination_params, paginate
from app.utils.response import success

async def get_all(db: AsyncSession, current_user: User, page: int, limit: int):
    skip = get_pagination_params(page=page, limit=limit)
    alerts, total = await alert_service.get_all_published(db, skip, limit)
    data = [AlertResponse.model_validate(a).model_dump() for a in alerts]
    return success(data=data, message="Alerts Fetched", meta=paginate(total, page, limit))

async def get_my_alerts(db: AsyncSession, current_user: User) -> dict:
    alerts = await alert_service.get_my_alert(db, current_user.id)
    data = [AlertResponse.model_validate(a).model_dump() for a in alerts]
    return success(data=data, message="alert fetched")

async def get_one(db: AsyncSession, alert_id: str, current_user: User) -> dict:
    alert = await alert_service.get_one(db, alert_id, current_user)
    return success(data=AlertResponse.model_validate(alert).model_dump(), message="Alert Fetched")

async def create(db: AsyncSession, data: CreateAlertRequest, current_user: User) -> dict:
    alert = await alert_service.create(db, data, current_user)
    return success(data=AlertResponse.model_validate(alert).model_dump(), message="Alert Created")

async def update(db: AsyncSession, alert_id: str, data: UpdateAlertRequest, current_user: User) -> dict:
    alert = await alert_service.update(db, alert_id, data, current_user)
    return success(data=AlertResponse.model_validate(alert).model_dump(), message="Alert updated")

async def toggle_publish(db: AsyncSession, alert_id: str, current_user: User) -> dict:
    alert = await alert_service.toggle_publish(db, alert_id, current_user)
    return success(data=AlertResponse.model_validate(alert).model_dump(), message="Alert Publish Status Updated")

async def delete(db: AsyncSession, alert_id: str) -> None:
    await alert_service.delete(db, alert_id)
    return success(data=None, message="Alert Deleted")
