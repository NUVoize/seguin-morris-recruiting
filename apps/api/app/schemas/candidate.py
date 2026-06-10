"""Candidate schemas — Create / Update / Read."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import PipelineStatus


class CandidateBase(BaseModel):
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


class CandidateCreate(CandidateBase):
    """At minimum we need *something* to identify the candidate — name OR email OR url."""

    pipeline_status: PipelineStatus = PipelineStatus.NEW

    @field_validator("full_name", "contact_email", "profile_url")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        # Cross-field validation lives in model_validator — this is just a placeholder.
        # Real check is in the route layer for now (clearer error messages).
        return v


class CandidateUpdate(BaseModel):
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


class CandidateRead(CandidateBase):
    id: uuid.UUID
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
