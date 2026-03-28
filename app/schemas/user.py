from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str
    photo_url: str | None = None

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

    model_config = {"from_attributes": True}