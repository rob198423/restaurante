from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "ToneMind AI"
    environment: str = "development"
    secret_key: str = Field(default="change-me-before-production", min_length=16)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+psycopg://tonemind:tonemind@localhost:5432/tonemind"
    upload_dir: Path = Path("../storage/uploads")
    processed_dir: Path = Path("../storage/processed")
    max_upload_mb: int = 80


@lru_cache
def get_settings() -> Settings:
    return Settings()
