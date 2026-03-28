from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Chartflix APIs"
    DESCRIPTION: str="Trading alert and stock recommendation platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    SECRET_KEY: str = "/rV2tCnTuGeLniRTQKNgcbVzDwa4uxsxM/u0KTonUug="
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}

settings = Settings()