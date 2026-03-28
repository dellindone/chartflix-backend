from datetime import datetime
from pydantic import BaseModel
from app.models.alert import AlertCategory, AlertDirection, AlertStatus

class CreateAlertRequest(BaseModel):
    category: AlertCategory
    direction: AlertDirection
    exchange: str
    contract: str
    symbol: str
    ltp: float
    strike: float
    option_ltp: float
    lot_size: int
    investment: float

class UpdateAlertRequest(BaseModel):
    category: AlertCategory | None = None
    direction: AlertDirection | None = None
    exchange: str | None = None
    contract: str | None = None
    symbol: str | None = None
    ltp: float | None = None
    strike: float | None = None
    option_ltp: float | None = None
    lot_size: int | None = None
    investment: float | None = None

class AlertResponse(BaseModel):
    id: str
    analyst_id: str | None
    category: AlertCategory
    direction: AlertDirection
    exchange: str
    contract: str
    symbol: str
    ltp: float
    strike: float
    option_ltp: float
    lot_size: int
    investment: float
    status: AlertStatus
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}