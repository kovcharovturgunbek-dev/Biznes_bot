from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "bozorchi"
    environment: str = "development"
    debug: bool = False

    bot_token: str = Field(..., min_length=1)

    database_url: str = Field(..., min_length=1)
    redis_url: str = Field(..., min_length=1)

    secret_key: str = Field(..., min_length=32)

    director_telegram_id: int

    app_timezone: str = "Asia/Tashkent"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
