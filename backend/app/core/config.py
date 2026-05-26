from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TONEMIND AI"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://tonemind:tonemind@localhost:5432/tonemind"
    secret_key: str = "tonemind-local-dev-secret-9f1f2a5c5a4d4e0aa42af06f7c18d7b0"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    upload_dir: Path = Path("storage/uploads")
    export_dir: Path = Path("storage/exports")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    ffmpeg_bin: str = "ffmpeg"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            if value.strip() == "*":
                return ["*"]
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage()
    return settings
