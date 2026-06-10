"""Recruiting core — Campaign, Candidate, qualifications, join table.

This is the heart of the data model. A Campaign defines what we're hiring for.
Candidates are people. CampaignCandidate is the M:N join with per-assignment state.
CandidateQualification tracks the regulatory/credential signals per candidate.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    CampaignStatus,
    PipelineStatus,
    QualificationStatus,
    QualificationType,
)


class Campaign(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A recruiting campaign — what we're hiring for, where, and what's required."""

    __tablename__ = "campaigns"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    division: Mapped[str] = mapped_column(String(128), nullable=False)
    role_type: Mapped[str] = mapped_column(String(128), nullable=False)
    region: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    employment_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requirements: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, native_enum=False, length=16),
        nullable=False,
        default=CampaignStatus.DRAFT,
        server_default=CampaignStatus.DRAFT.value,
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    candidates: Mapped[list[CampaignCandidate]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class Candidate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A person we might recruit. Sparse by design — many fields will be NULL
    for leads discovered via scraping where we only have a name and a URL."""

    __tablename__ = "candidates"

    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    current_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    candidate_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    profile_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    fit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fit_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fit_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pipeline_status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus, native_enum=False, length=16),
        nullable=False,
        default=PipelineStatus.NEW,
        server_default=PipelineStatus.NEW.value,
        index=True,
    )
    consent_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="unknown",
        server_default="unknown",
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(nullable=True)

    qualifications: Mapped[list[CandidateQualification]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    campaign_assignments: Mapped[list[CampaignCandidate]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )


class CampaignCandidate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """M:N join between Campaign and Candidate with per-assignment status."""

    __tablename__ = "campaign_candidates"
    __table_args__ = (
        UniqueConstraint("campaign_id", "candidate_id", name="campaign_candidate"),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
    )

    campaign: Mapped[Campaign] = relationship(back_populates="candidates")
    candidate: Mapped[Candidate] = relationship(back_populates="campaign_assignments")


class CandidateQualification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A regulatory / educational / certification signal for a candidate.

    Each row captures one (qualification_type, qualification_status) observation
    with optional supporting evidence. A candidate can have multiple rows for the
    same type if our confidence in it has evolved over time.
    """

    __tablename__ = "candidate_qualifications"

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    qualification_type: Mapped[QualificationType] = mapped_column(
        Enum(QualificationType, native_enum=False, length=32),
        nullable=False,
    )
    qualification_status: Mapped[QualificationStatus] = mapped_column(
        Enum(QualificationStatus, native_enum=False, length=16),
        nullable=False,
    )
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    candidate: Mapped[Candidate] = relationship(back_populates="qualifications")
