from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.recommendations.service import reco_service
from app.utils.pagination import paginate, get_pagination_params
from app.utils.response import success
from app.schemas.recommendation import CreateRecommendationRequest, UpdateRecommendationRequest, RecommendationResponse

async def get_all(db: AsyncSession, current_user: User, page: int, limit: int) -> dict:
    skip = get_pagination_params(page, limit)
    recos, total = await reco_service.get_all_published(db, skip, limit)
    data = [RecommendationResponse.model_validate(r).model_dump() for r in recos]
    return success(
        data=data,
        message="Recommendations fetched",
        meta=paginate(total=total, page=page, limit=limit)
    )

async def get_my_recommendations(db: AsyncSession, current_user: User) -> dict:
    recos = await reco_service.get_my_recommendations(db, current_user)
    data = [RecommendationResponse.model_validate(r).model_dump() for r in recos]
    return success(data=data, message="My recommendations fetched")

async def get_one(db: AsyncSession, reco_id: str, current_user: User) -> dict:
    reco = await reco_service.get_one(db, reco_id, current_user)
    return success(data=RecommendationResponse.model_validate(reco).model_dump(), message="Recommendation fetched")

async def create(db:AsyncSession, data: CreateRecommendationRequest, current_user: User) -> dict:
    reco = await reco_service.create(db, data, current_user)
    return success(
        data=RecommendationResponse.model_validate(reco).model_dump(),
        message="Recommendation Created"
    )

async def update(db: AsyncSession, reco_id: str, data: UpdateRecommendationRequest, current_user: User) -> dict:
    reco = await reco_service.update(db, reco_id=reco_id, data=data, current_user=current_user)
    return success(
        data=RecommendationResponse.model_validate(reco).model_dump(),
        message="Recommendation Updated"
    )

async def toggle_publish(db: AsyncSession, reco_id: str, current_user: User) -> dict:
    reco = await reco_service.toggle_publish(db, reco_id, current_user)
    return success(
        data=RecommendationResponse.model_validate(reco).model_dump(),
        message="Recommendation publish status updated"
    )

async def delete(db: AsyncSession, reco_id: str):
    await reco_service.delete(db, reco_id)
    return success(data=None, message="Recommendations Deleted")
