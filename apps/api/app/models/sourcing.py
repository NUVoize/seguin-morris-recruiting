"""Source discovery — where candidates come from.

LeadSource = a job board, association, school, etc. that we look at.
SourceMention = a specific URL/excerpt linking a candidate to a source.
SchoolProgram = a DEP/DEC/AEC program at an institution (Quebec recruiting research).
RecruitingEvent = a career fair, trade show, etc.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessMethod, SourceType


class LeadSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A source of candidate leads. The `allowed_to_scrape` flag is the
    LAW of this table — agents must check it before doing any automated work."""

    __tablename__ = "lead_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    access_method: Mapped[AccessMethod] = mapped_column(
        Enum(AccessMethod, native_enum=False, length=32),
        nullable=False,
    )
    allowed_to_scrape: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    mentions: Mapped[list[SourceMention]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )


class SourceMention(Base, UUIDPrimaryKeyMixin):
    """A specific URL/excerpt linking a candidate to a source — provenance trail."""

    __tablename__ = "source_mentions"

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lead_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(nullable=True)

    source: Mapped[LeadSource] = relationship(back_populates="mentions")


class SchoolProgram(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A DEP, DEC, or AEC program at a Quebec institution.

    Seeded from the Refrigeration Specialist research — 7 DEP centers,
    7 cégeps with DEC 221.C0, plus targeted AECs at Collège Ahuntsic.
    """

    __tablename__ = "school_programs"

    institution_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    program_name: Mapped[str] = mapped_column(String(255), nullable=False)
    program_type: Mapped[str] = mapped_column(String(32), nullable=False)  # DEP / DEC / AEC
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    province: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Canada",
        server_default="Canada",
    )
    public_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    public_contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    public_contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cohort_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    cohort_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class RecruitingEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A career fair, trade show, association event, or open house we may attend."""

    __tablename__ = "recruiting_events"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    date_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    province: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    recruiting_value_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
