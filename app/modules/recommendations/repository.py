from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.recommendation import Recommendation, RecoStatus

class RecommendationRepository:
    async def get_by_id(self, db: AsyncSession,reco_id: str) -> Recommendation | None:
        result = await db.execute(select(Recommendation).where(Recommendation.id == reco_id))
        return result.scalar_one_or_none()
    
    async def get_published(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> tuple[list[Recommendation], int]:
        query = select(Recommendation).where(Recommendation.status == RecoStatus.PUBLISHED).order_by(desc(Recommendation.published_at))
        count = await db.execute(select(func.count()).select_from(query.subquery()))
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), count.scalar()
    
    async def get_by_analyst(self, db: AsyncSession, analyst_id: str) -> list[Recommendation]:
        result = await db.execute(select(Recommendation).where(Recommendation.analyst_id == analyst_id).order_by(desc(Recommendation.created_at)))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, analyst_id: str, data: dict) -> Recommendation:
        reco = Recommendation(**data, analyst_id=analyst_id)
        db.add(reco)
        await db.commit()
        await db.refresh(reco)
        return reco
    
    async def update(self, db: AsyncSession, reco: Recommendation, data: dict) -> Recommendation:
        for key, value in data.items():
            setattr(reco, key, value)

        await db.commit()
        await db.refresh(reco)
        return reco

    async def delete(self, db: AsyncSession, reco: Recommendation):
        await db.delete(reco)
        await db.commit()

reco_repo = RecommendationRepository()
