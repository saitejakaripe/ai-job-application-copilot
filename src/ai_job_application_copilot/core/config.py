from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Job Application Copilot"
    environment: str = "local"
    database_url: str = "sqlite:///./data/copilot.db"
    llm_provider: str = "deterministic"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_prefix="AI_COPILOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

