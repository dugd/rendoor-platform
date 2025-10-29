from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = "development"
    DEBUG: bool = True

    DB_URL: str  # postgresql connection string

    BROKER_URL: str  # e.g. redis://localhost:6379/0
    BOT_STORAGE_URL: str  # use redis

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_CHAT_ID: int

    SAVE_RAW_LISTINGS: bool = True

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"]) -> str:
        return self.DB_URL.replace("postgresql://", f"postgresql+{driver}://")


def get_settings() -> Settings:
    """Get application settings."""

    @lru_cache()
    def settings() -> Settings:
        return Settings()

    return settings()


__all__ = ["get_settings", "Settings"]
