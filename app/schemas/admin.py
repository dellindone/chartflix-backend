from pydantic import BaseModel
from app.models.user import UserRole


class UpdateRoleRequest(BaseModel):
    role: UserRole