from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base class for all exceptions in the application."""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content = {
            "success": False,
            "data": None,
            "message": exc.message,
            "error_code": exc.error_code
        }
    )

class BadRequestException(AppException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message=message, status_code=400, error_code="BAD_REQUEST")

class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401, error_code="UNAUTHORIZED")

class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403, error_code="FORBIDDEN")

class NotFoundException(AppException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message=message, status_code=404, error_code="NOT_FOUND")

class ConflictException(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409, error_code="CONFLICT")

