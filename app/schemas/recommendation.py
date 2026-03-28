from datetime import datetime
from pydantic import BaseModel
from app.models.recommendation import RecoAction, RecoStatus

class CreateRecommendationRequest(BaseModel):
    symbol: str
    name: str
    action: RecoAction
    sector: str
    cmp: float
    target: float
    stop_loss: float
    note: str | None = None


class UpdateRecommendationRequest(BaseModel):
    symbol: str | None = None
    name: str | None = None
    action: RecoAction | None = None
    sector: str | None = None
    cmp: float | None = None
    target: float | None = None
    stop_loss: float | None = None
    note: str | None = None


class RecommendationResponse(BaseModel):
    id: str
    analyst_id: str
    symbol: str
    name: str
    action: RecoAction
    sector: str
    cmp: float
    target: float
    stop_loss: float
    note: str | None
    status: RecoStatus
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}