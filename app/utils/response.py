from typing import Any
from app.schemas.common import PaginationMeta

def success(data: Any, message: str, meta: PaginationMeta | None = None) -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "meta": meta,
        "error_code": None
    }

def error(message: str, error_code: str = "ERROR") -> dict:
    return {
        "success": False,
        "data": None,
        "message": message,
        "meta": None,
        "error_code": error_code
    }