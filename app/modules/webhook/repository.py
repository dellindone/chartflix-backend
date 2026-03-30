from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.analyst import Analyst
from app.modules.alerts.repository import alert_repo

SYSTEM_EMAIL = "system@chartflix.com"


class WebhookRepository:

    async def get_system_analyst_id(self, db: AsyncSession) -> str | None:
        result = await db.execute(
            select(Analyst)
            .join(User, User.id == Analyst.user_id)
            .where(User.email == SYSTEM_EMAIL)
        )
        analyst = result.scalar_one_or_none()
        if not analyst:
            return None
        return str(analyst.user_id)

    async def create_alert(self, db: AsyncSession, analyst_id: str, data: dict):
        return await alert_repo.create(db, analyst_id=analyst_id, data=data)

webhook_repo = WebhookRepository()