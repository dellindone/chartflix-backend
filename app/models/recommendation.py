import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RecoAction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class RecoStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    analyst_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("analysts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[RecoAction] = mapped_column(Enum(RecoAction), nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    cmp: Mapped[float] = mapped_column(Float, nullable=False)
    target: Mapped[float] = mapped_column(Float, nullable=False)     
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)  
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[RecoStatus] = mapped_column(
        Enum(RecoStatus),
        default=RecoStatus.DRAFT,
        nullable=False,)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analyst: Mapped["Analyst"] = relationship("Analyst", back_populates="recommendations")
