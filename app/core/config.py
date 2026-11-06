from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Bozorchi loyihasining markaziy konfiguratsiyasi.

    Maxfiy ma'lumotlar .env yoki server muhit
    o'zgaruvchilari orqali olinadi.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    # Umumiy dastur sozlamalari
    app_name: str = "Bozorchi"
    environment: str = "development"
    debug: bool = False

    # Telegram bot
    bot_token: str = Field(
        ...,
        min_length=1,
    )

    # Asosiy ma'lumotlar bazasi
    database_url: str = Field(
        ...,
        min_length=1,
    )

    # Redis yordamchi xizmati
    redis_url: str = Field(
        ...,
        min_length=1,
    )

    # Ichki xavfsizlik kaliti
    secret_key: str = Field(
        ...,
        min_length=32,
    )

    # Direktorning yagona Telegram ID raqami
    director_telegram_id: int = Field(
        ...,
        gt=0,
    )

    # Dastur vaqt mintaqasi
    app_timezone: str = "Asia/Tashkent"

    @field_validator("app_timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        """
        Vaqt mintaqasi mavjudligini tekshiradi.
        """
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(
                f"Noto'g'ri vaqt mintaqasi: {value}"
            ) from exc

        return value

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        """
        Ishlash muhitini standartlashtiradi.
        """
        value = value.strip().lower()

        allowed = {
            "development",
            "testing",
            "staging",
            "production",
        }

        if value not in allowed:
            raise ValueError(
                "environment quyidagilardan biri bo'lishi kerak: "
                "development, testing, staging, production"
            )

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Konfiguratsiyani bir marta yuklaydi va keshlaydi.
    """
    return Settings()


def clear_settings_cache() -> None:
    """
    Zarur holatda konfiguratsiya keshini tozalaydi.
    """
    get_settings.cache_clear()


settings = get_settings()
