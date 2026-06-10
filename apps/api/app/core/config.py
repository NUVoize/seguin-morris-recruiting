"""Application configuration. Reads from environment / .env via pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Top-level settings for the Seguin Morris API.

    Hard rule (spec): adapters (LLM, email) are configured here; no provider-specific
    logic lives inside agents or business code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application ---
    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "seguin-morris-recruiting"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_default_language: Literal["fr", "en"] = "fr"

    # --- Database / cache ---
    database_url: str = Field(
        default="postgresql+psycopg://seguin:dev_password_change_me@localhost:5433/seguin_morris"
    )
    redis_url: str = "redis://localhost:6380/0"
    celery_broker_url: str = "redis://localhost:6380/1"
    celery_result_backend: str = "redis://localhost:6380/2"

    # --- Security ---
    jwt_secret: str = "CHANGE_ME_GENERATE_A_LONG_RANDOM_STRING"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720  # 12 hours

    # --- LLM adapter (swappable per spec) ---
    llm_provider: Literal[
        "mock", "openai", "anthropic", "gemini", "azure_openai", "lm_studio"
    ] = "mock"
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""

    # --- Email adapter (Gmail v1, M365 v2) ---
    email_provider: Literal["mock", "gmail", "microsoft365"] = "mock"
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/api/auth/gmail/callback"
    microsoft365_client_id: str = ""
    microsoft365_client_secret: str = ""
    microsoft365_tenant_id: str = ""

    # --- Retention ---
    inactive_lead_retention_days: int = 365  # 12 months per spec

    # --- CORS (dev wide-open; production locks down to known origins) ---
    cors_allow_origins: list[str] = ["http://localhost:3000"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
