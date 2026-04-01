from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str | None = None
    photo_url: str | None = None
    role: str
    is_approved: bool = False

    model_config = {"from_attributes": True}

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    location: str | None = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None
    location: str | None
    photo_url: str | None
    role: str
    is_approved: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}