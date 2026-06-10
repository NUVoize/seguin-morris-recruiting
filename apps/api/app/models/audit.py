"""Audit log + retention job tracking.

AuditLog = immutable record of important actions (per spec hard rule).
RetentionJob = trace of the 12-month inactive lead cleanup runs.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """Immutable audit trail. Spec hard rule: every important action gets logged here.

    `action` is a short string ("user.login", "campaign.created",
    "outreach.sent", "candidate.deleted", etc.) — kept as TEXT rather than enum
    so we don't need a migration every time a new action is added.

    `entity_type` + `entity_id` are a soft reference to whatever was acted upon.
    """

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    audit_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # `created_at` only — audit rows are never updated. No `updated_at`.
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default="now()",
    )


class RetentionJob(Base, UUIDPrimaryKeyMixin):
    """Trace of a retention job execution. Spec §4: 12-month inactive lead retention."""

    __tablename__ = "retention_jobs"

    job_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    records_affected: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
