from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str
    meta: PaginationMeta | None = None
    error_code: str | None = None
