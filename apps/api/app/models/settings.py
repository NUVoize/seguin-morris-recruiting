"""Settings — brand, LLM provider, email provider.

These are singleton-ish tables: typically one active row per provider type,
but we support multiple historical rows so audit + rollback works cleanly.

Hard rule (spec): adapter business logic NEVER references provider names directly.
Reads happen through app.core.config and app.integrations.{llm,email} adapters.
"""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class BrandSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Per-tenant brand presentation. Today: one row (Seguin Morris)."""

    __tablename__ = "brand_settings"

    company_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="Seguin Morris",
        server_default="Seguin Morris",
    )
    primary_color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    accent_color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    designed_by_label: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="Designed by CTRL Solutions",
        server_default="Designed by CTRL Solutions",
    )


class LLMSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One configured LLM provider. Multiple rows allowed so an admin can
    flip the active provider without losing the previous configuration."""

    __tablename__ = "llm_settings"

    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # API keys NEVER live in this table. They live in env vars + secret manager.
    # This column stores the *name* of the secret to look up (e.g. "OPENAI_API_KEY").
    api_key_secret_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class EmailSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One configured email provider. Same pattern as LLMSettings — credentials
    never stored here, only the provider config and the secret name."""

    __tablename__ = "email_settings"

    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    account_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
