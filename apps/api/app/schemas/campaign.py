"""Campaign schemas — Create / Update / Read."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CampaignStatus


class CampaignBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    division: str = Field(..., min_length=1, max_length=128)
    role_type: str = Field(..., min_length=1, max_length=128)
    region: str = Field(..., min_length=1, max_length=128)
    employment_type: str | None = Field(default=None, max_length=64)
    requirements: dict[str, Any] = Field(default_factory=dict)


class CampaignCreate(CampaignBase):
    """All required fields except status (which defaults to draft)."""

    status: CampaignStatus = CampaignStatus.DRAFT


class CampaignUpdate(BaseModel):
    """All fields optional — used for PATCH /campaigns/{id}."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    division: str | None = Field(default=None, min_length=1, max_length=128)
    role_type: str | None = Field(default=None, min_length=1, max_length=128)
    region: str | None = Field(default=None, min_length=1, max_length=128)
    employment_type: str | None = Field(default=None, max_length=64)
    requirements: dict[str, Any] | None = None
    status: CampaignStatus | None = None


class CampaignRead(CampaignBase):
    id: uuid.UUID
    status: CampaignStatus
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
