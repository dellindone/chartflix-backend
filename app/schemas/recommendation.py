from datetime import datetime
from typing import Any
from pydantic import BaseModel, model_validator
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
    analyst_name: str | None = None
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

    @model_validator(mode='before')
    @classmethod
    def extract_analyst_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        analyst_name = None
        try:
            if data.analyst and data.analyst.user:
                analyst_name = data.analyst.user.name
        except Exception:
            pass
        return {
            'id': data.id,
            'analyst_id': data.analyst_id,
            'analyst_name': analyst_name,
            'symbol': data.symbol,
            'name': data.name,
            'action': data.action,
            'sector': data.sector,
            'cmp': data.cmp,
            'target': data.target,
            'stop_loss': data.stop_loss,
            'note': data.note,
            'status': data.status,
            'published_at': data.published_at,
            'created_at': data.created_at,
            'updated_at': data.updated_at,
        }