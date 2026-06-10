"""User and Role models — spec §7.

Note: spec doesn't list `password_hash` on `users`, but since auth is required
and we have no SSO setup, we add a nullable password_hash. If/when OAuth or
magic links land in v2, this column simply stays NULL for those users.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import Language

if TYPE_CHECKING:
    # Forward-declared to avoid circular imports at runtime; resolved by SQLAlchemy lazily.
    pass


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """RBAC role. Permissions stored as JSONB for flexibility while
    we figure out the exact permission taxonomy in early phases."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    permissions: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    users: Mapped[list[User]] = relationship(back_populates="role")


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Recruiter or admin user account."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    preferred_language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        nullable=False,
        default=Language.FR,
        server_default=Language.FR.value,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
    )

    role: Mapped[Role | None] = relationship(back_populates="users")
