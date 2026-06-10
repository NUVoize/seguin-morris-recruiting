"""Operations — agent execution telemetry, outreach events, notes.

AgentRun = one execution of one agent against one campaign (with full traceability).
OutreachEvent = one communication touch (email/phone/SMS), with recruiter approval gate.
Note = freeform recruiter annotation attached to any entity (polymorphic).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    AgentRunStatus,
    AgentType,
    Language,
    OutreachChannel,
    OutreachDirection,
    OutreachStatus,
)


class AgentRun(Base, UUIDPrimaryKeyMixin):
    """One execution of one agent. Captures input, output summary, and any error log.

    Detailed traces / per-step telemetry will live elsewhere (Celery task records,
    structured logs) — this table is the recruiter-visible "what did the agent do" history.
    """

    __tablename__ = "agent_runs"

    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    agent_type: Mapped[AgentType] = mapped_column(
        Enum(AgentType, native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, native_enum=False, length=16),
        nullable=False,
        default=AgentRunStatus.PENDING,
        server_default=AgentRunStatus.PENDING.value,
        index=True,
    )
    input_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )


class OutreachEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single outbound or inbound communication touch.

    Outbound messages MUST pass through recruiter approval (status flows
    DRAFT -> PENDING_APPROVAL -> SENT). The Email/SMS/etc. provider is stored
    on the row so we can support multi-provider (Gmail v1, M365 v2) cleanly.
    """

    __tablename__ = "outreach_events"

    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    school_program_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("school_programs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel: Mapped[OutreachChannel] = mapped_column(
        Enum(OutreachChannel, native_enum=False, length=16),
        nullable=False,
    )
    direction: Mapped[OutreachDirection] = mapped_column(
        Enum(OutreachDirection, native_enum=False, length=16),
        nullable=False,
    )
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        nullable=False,
        default=Language.FR,
        server_default=Language.FR.value,
    )
    status: Mapped[OutreachStatus] = mapped_column(
        Enum(OutreachStatus, native_enum=False, length=24),
        nullable=False,
        default=OutreachStatus.DRAFT,
        server_default=OutreachStatus.DRAFT.value,
        index=True,
    )
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Note(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Freeform recruiter annotation attached polymorphically to any entity.

    `entity_type` + `entity_id` form a soft reference — we don't enforce a
    foreign key because notes attach to many table types. Application code
    is responsible for resolving these.
    """

    __tablename__ = "notes"

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
