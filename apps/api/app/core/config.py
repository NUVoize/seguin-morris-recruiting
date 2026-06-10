"""Application configuration. Reads from environment / .env via pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Top-level settings for the Seguin Morris API.

    Hard rule (spec): adapters (LLM, email) are configured here; no provider-specific
    logic lives inside agents or business code.
    """

    model_config = SettingsConfigDict(
        # Look up the directory tree so a single .env at the project root
        # works whether you launch uvicorn from apps/api/ or from the repo root.
        # If both exist, the local apps/api/.env overrides the root one.
        env_file=("../../.env", ".env"),
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

    # --- CORS ---
    # Comma-separated list of allowed origins. Defaults to localhost dev URL.
    # In production on Railway, set to e.g.:
    #   "https://seguin-morris-web-production.up.railway.app,http://localhost:3000"
    cors_allow_origins: str = "http://localhost:3000"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        """Split the comma-separated CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Railway hands out plain postgresql:// URLs; SQLAlchemy needs the
        +psycopg driver prefix to use the modern psycopg 3 client."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        if v.startswith("postgres://"):  # older Heroku-style URLs
            return v.replace("postgres://", "postgresql+psycopg://", 1)
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
