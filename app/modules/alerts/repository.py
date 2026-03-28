from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.alert import Alert, AlertStatus

class AlertRepository:

    async def get_by_id(self, db: AsyncSession, alert_id: str) -> Alert | None:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    async def get_published(self, db: AsyncSession, skip: int=0, limit: int=20) -> tuple[list[Alert], int]:
        query = select(Alert).where(Alert.status == AlertStatus.ACTIVE).order_by(desc(Alert.published_at))
        result = await db.execute(query.offset(skip).limit(limit))
        count = await db.execute(select(func.count()).select_from(query.subquery()))
        return result.scalars().all(), count.scalar()

    async def get_by_analyst(self, db: AsyncSession, analyst_id: str | None) -> list[Alert]:
        query = select(Alert).where(Alert.analyst_id == analyst_id).order_by(desc(Alert.created_at))
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, analyst_id: str | None, data: dict) -> Alert:
        alert = Alert(**data, analyst_id=analyst_id)
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def update(self, db: AsyncSession, alert: Alert, data: dict) -> Alert:
        for key, value in data.items():
            setattr(alert, key, value)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def delete(self, db: AsyncSession, alert: Alert) -> None:
        await db.delete(alert)
        await db.commit()

alert_repo = AlertRepository()