import uuid, enum

from datetime import datetime

from sqlalchemy import String, ForeignKey, Enum, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class AlertCategory(str, enum.Enum):
    INDEX = "INDEX"
    STOCK = "STOCK"
    COMMODITY = "COMMODITY"

class AlertDirection(str, enum.Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

class AlertStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT= "DRAFT"

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analyst_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[AlertCategory] = mapped_column(Enum(AlertCategory), nullable=False)
    direction: Mapped[AlertDirection] = mapped_column(Enum(AlertDirection), nullable=False)
    exchange: Mapped[str] = mapped_column(String, nullable=False)
    contract: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)

    ltp: Mapped[float] = mapped_column(Float, nullable=False)
    strike: Mapped[float] = mapped_column(Float, nullable=False)
    option_ltp: Mapped[float] = mapped_column(Float, nullable=False)
    lot_size: Mapped[int] = mapped_column(Integer, nullable=False)
    investment: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.DRAFT, nullable=False, server_default="DRAFT")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analyst: Mapped["User | None"] = relationship("User", foreign_keys=[analyst_id])
