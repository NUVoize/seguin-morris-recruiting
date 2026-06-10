"""LeadSource schemas — Create / Update / Read.

HttpUrl validation enforced on input only; Read returns plain str for permissive
serialization of historical data.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import AccessMethod, SourceType


class _LeadSourceMutableFields(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_type: SourceType
    url: HttpUrl
    access_method: AccessMethod
    allowed_to_scrape: bool = False
    notes: str | None = None


class LeadSourceCreate(_LeadSourceMutableFields):
    pass


class LeadSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: SourceType | None = None
    url: HttpUrl | None = None
    access_method: AccessMethod | None = None
    allowed_to_scrape: bool | None = None
    notes: str | None = None
    last_checked_at: datetime | None = None


class LeadSourceRead(BaseModel):
    id: uuid.UUID
    name: str
    source_type: SourceType
    url: str  # plain string on output — DB may have URLs that don't re-validate
    access_method: AccessMethod
    allowed_to_scrape: bool
    notes: str | None
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
