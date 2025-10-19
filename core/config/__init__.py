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
    LOGGING_LEVEL: str = "INFO"

    SERVICE_NAME: str = "my-service"

    DB_URL: str

    BROKER_URL: str

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"]) -> str:
        return self.DB_URL.replace("postgresql://", f"postgresql+{driver}://")


def get_settings() -> Settings:
    """Get application settings."""

    @lru_cache()
    def settings() -> Settings:
        return Settings()

    return settings()


__all__ = ["get_settings", "Settings"]
