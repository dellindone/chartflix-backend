import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.alert import Alert, AlertStatus
from app.models.user import User, UserRole
from app.modules.alerts.repository import alert_repo
from app.schemas.alert import CreateAlertRequest, UpdateAlertRequest
from app.core.websocket import ALERT_CHANNEL

class AlertService:
    async def get_all_published(self, db: AsyncSession, skip: int, limit: int):
        alerts, total = await alert_repo.get_published(db, skip, limit)
        return alerts, total

    async def get_my_alert(self, db: AsyncSession, analyst_id: str):
        return await alert_repo.get_by_analyst(db, analyst_id)
    
    async def get_one(self, db: AsyncSession, alert_id: str, current_user: User) -> Alert:
        alert = await alert_repo.get_by_id(db, alert_id)
        if not alert: raise NotFoundException("Alert not found")
        if alert.status != AlertStatus.ACTIVE:
            if current_user.role == UserRole.USER:
                raise NotFoundException("Alert not found")
        return alert
    
    async def update(self, db: AsyncSession, alert_id: str, data: UpdateAlertRequest, current_user: User) -> Alert:
        alert = await alert_repo.get_by_id(db, alert_id)
        if not alert: raise NotFoundException("Alert not found")

        if current_user.role != UserRole.ADMIN and alert.analyst_id != current_user.id:
            raise ForbiddenException("You can only publish your own alerts")
        
        updates = data.model_dump(exclude_unset=True)
        return await alert_repo.update(db, alert, updates)

    async def _publish(self, alert: Alert):
        try:
            message = json.dumps({
                "symbol": alert.symbol,
                "contract": alert.contract,
                "direction": alert.direction.value if hasattr(alert.direction, "value") else alert.direction,
                "ltp": alert.ltp,
                "option_ltp": alert.option_ltp,
                "investment": alert.investment,
            })
            redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, ssl_cert_reqs=None)
            await redis.publish(ALERT_CHANNEL, message)
            await redis.aclose()
        except Exception:
            pass

    async def create(self, db: AsyncSession, data: CreateAlertRequest, current_user: User) -> Alert:
        return await alert_repo.create(db, analyst_id=current_user.id, data=data.model_dump())

    async def toggle_publish(self, db: AsyncSession, alert_id: str, current_user: User) -> Alert:
        alert = await alert_repo.get_by_id(db, alert_id)
        if not alert: raise NotFoundException("Alert not found")

        if current_user.role != UserRole.ADMIN and alert.analyst_id != current_user.id:
            raise ForbiddenException("You can only publish your own alerts")
        
        if alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.INACTIVE
            alert.published_at = None
        else:
            alert.status = AlertStatus.ACTIVE
            alert.published_at = datetime.now(timezone.utc)
            await self._publish(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def delete(self, db: AsyncSession, alert_id: str):
        alert = await alert_repo.get_by_id(db, alert_id)
        if not alert: raise NotFoundException("Alert not found")
        await alert_repo.delete(db, alert)        

alert_service = AlertService()