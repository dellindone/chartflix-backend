import uuid, enum

from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[UserRole] = mapped_column(String, nullable=False, default=UserRole.USER.value)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    analyst_profile: Mapped["Analyst"] = relationship("Analyst", back_populates="user", uselist=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")