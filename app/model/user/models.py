import uuid
import enum

from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func

from app.db.base import Base

class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)

    role = Column(Enum(Role), default=Role.USER, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
