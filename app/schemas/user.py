from pydantic import BaseModel

class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str
    photo_url: str | None = None
