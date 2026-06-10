"""Candidate schemas — Create / Update / Read.

Email validation is enforced on CREATE only (EmailStr).
READ schemas use plain `str` so historical/imported data with weird-but-valid
addresses (e.g. .test TLDs in dev seed) doesn't crash response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import PipelineStatus


class _CandidateMutableFields(BaseModel):
    """Fields shared between Create and Update — input shape, strict validation."""

    full_name: str | None = Field(default=None, max_length=255)
    current_title: str | None = Field(default=None, max_length=255)
    region: str | None = Field(default=None, max_length=128)
    candidate_type: str = Field(default="unknown", max_length=32)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=64)
    profile_url: str | None = None

    @field_validator("contact_email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        """Treat empty string as null so the EmailStr validator doesn't trip on ''."""
        return v or None


class CandidateCreate(_CandidateMutableFields):
    """Strict input — at least one identifier required (checked in route layer)."""

    pipeline_status: PipelineStatus = PipelineStatus.NEW


class CandidateUpdate(BaseModel):
    """PATCH input — every field optional, EmailStr where present."""

    full_name: str | None = Field(default=None, max_length=255)
    current_title: str | None = Field(default=None, max_length=255)
    region: str | None = Field(default=None, max_length=128)
    candidate_type: str | None = Field(default=None, max_length=32)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=64)
    profile_url: str | None = None
    pipeline_status: PipelineStatus | None = None
    fit_score: int | None = Field(default=None, ge=0, le=100)
    fit_label: str | None = Field(default=None, max_length=64)
    fit_summary: str | None = None
    consent_status: str | None = Field(default=None, max_length=32)

    @field_validator("contact_email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        return v or None


class CandidateRead(BaseModel):
    """Output shape — permissive on string fields. No re-validation of stored data."""

    id: uuid.UUID
    full_name: str | None
    current_title: str | None
    region: str | None
    candidate_type: str
    contact_email: str | None
    contact_phone: str | None
    profile_url: str | None
    pipeline_status: PipelineStatus
    fit_score: int | None
    fit_label: str | None
    fit_summary: str | None
    source_confidence: int | None
    consent_status: str
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
