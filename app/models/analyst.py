import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class Analyst(Base, TimestampMixin):
    __tablename__ = "analysts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id",ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    tag: Mapped[str] = mapped_column(String, nullable=False)

    avatar_bg: Mapped[str] = mapped_column(String, nullable=False, default="#388bfd")
    user: Mapped["User"] = relationship("User", back_populates="analyst_profile")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="analyst", passive_deletes=True)
