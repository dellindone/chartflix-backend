from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.recommendation import Recommendation, RecoStatus
from app.models.user import User, UserRole
from app.models.analyst import Analyst
from app.modules.recommendations.repository import reco_repo
from app.schemas.recommendation import CreateRecommendationRequest, UpdateRecommendationRequest

class RecommendationService:

    async def get_all_published(self, db: AsyncSession, skip: int, limit: int):
        return await reco_repo.get_published(db, skip, limit)
    
    async def get_my_recommendations(self, db: AsyncSession, current_user: User):
        result = await db.execute(select(Analyst).where(Analyst.user_id == current_user.id))
        analyst = result.scalar_one_or_none()
        if not analyst:
            raise NotFoundException("Analyst profile not found")
        return await reco_repo.get_by_analyst(db, analyst.id)
    
    async def get_one(self, db: AsyncSession, reco_id: str, current_user: User) -> Recommendation:
        reco = await reco_repo.get_by_id(db, reco_id)
        if not reco: raise NotFoundException("Recommendation Not Found")
        if reco.status != RecoStatus.PUBLISHED:
            if current_user.role == UserRole.USER:
                raise NotFoundException("Recommendation not found")
        return reco
    
    async def create(self, db: AsyncSession, data: CreateRecommendationRequest, current_user: User) -> Recommendation:
        result = await db.execute(select(Analyst).where(Analyst.user_id == current_user.id))
        analyst = result.scalar_one_or_none()
        if not analyst: raise NotFoundException("Analyst profile not found, Contact Admin")
        return await reco_repo.create(db, analyst.id, data.model_dump())
    
    async def update(self, db: AsyncSession, reco_id: str, data: UpdateRecommendationRequest, current_user: User) -> Recommendation:
        reco = await reco_repo.get_by_id(db, reco_id)
        if not reco: raise NotFoundException("Recommendation Not Found")

        if current_user.role != UserRole.ADMIN:
            result = await db.execute(select(Analyst).where(Analyst.user_id == current_user.id))
            analyst = result.scalar_one_or_none()
            if not analyst or reco.analyst_id != analyst.id:
                raise ForbiddenException("You can only edit your own recommendations")
        update = data.model_dump(exclude_unset=True)
        return await reco_repo.update(db, reco, update)
    
    async def toggle_publish(self, db: AsyncSession, reco_id: str, current_user: User) -> Recommendation:
        reco = await reco_repo.get_by_id(db, reco_id)
        if not reco: raise NotFoundException("Recommendation Not Found")

        if current_user.role != UserRole.ADMIN:
            result = await db.execute(select(Analyst).where(Analyst.user_id == current_user.id))
            analyst = result.scalar_one_or_none()
            if not analyst or reco.analyst_id != analyst.id:
                raise ForbiddenException("You can only edit your own recommendations")
        
        if reco.status == RecoStatus.PUBLISHED:
            reco.status = RecoStatus.DRAFT
            reco.published_at = None
        else:
            reco.status = RecoStatus.PUBLISHED
            reco.published_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(reco)
        return reco
    
    async def delete(self, db: AsyncSession, reco_id: str):
        reco = await reco_repo.get_by_id(db, reco_id)
        if not reco: raise NotFoundException("Recommendation Not Found")
        await reco_repo.delete(db, reco)

reco_service = RecommendationService()
