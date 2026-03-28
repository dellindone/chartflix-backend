from app.schemas.common import PaginationMeta

def get_pagination_params(page: int = 1, limit: int = 20) -> tuple[int, int]:
    offset = (page - 1) * limit
    return offset

def paginate(total: int, page: int, limit: int) -> PaginationMeta:
    return PaginationMeta(
        page=page,
        limit=limit,
        total=total
    )
