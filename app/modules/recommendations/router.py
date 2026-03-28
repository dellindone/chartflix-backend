from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.modules.recommendations import controller
from app.schemas.recommendation import CreateRecommendationRequest, UpdateRecommendationRequest

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

@router.get("")
async def get_all(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.get_all(db, current_user, page, limit)

@router.get("/my")
async def get_my_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    return await controller.get_my_recommendations(db, current_user)

@router.get("/{alert_id}")
async def get_one(
    reco_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.get_one(db, reco_id, current_user)

@router.post("", status_code=201)
async def create(
    data: CreateRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    return await controller.create(db, data, current_user)


@router.patch("/{reco_id}")
async def update(
    reco_id: str,
    data: UpdateRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await controller.update(db, reco_id, data, current_user)


@router.patch("/{reco_id}/publish")
async def toggle_publish(
    reco_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("analyst", "admin"))
):
    return await controller.toggle_publish(db, reco_id, current_user)


@router.delete("/{reco_id}", status_code=204)
async def delete(
    reco_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin"))
):
    return await controller.delete(db, reco_id)
