"""SchoolProgram schemas — read-only for now (seeded data, managed via scripts).

Write endpoints arrive with the admin module; v1 recruiters consume the
directory and contact institutions through the outreach module (Phase 6).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SchoolProgramRead(BaseModel):
    id: uuid.UUID
    institution_name: str
    program_name: str
    program_type: str
    city: str | None
    province: str | None
    country: str
    public_contact_name: str | None
    public_contact_email: str | None
    public_contact_phone: str | None
    cohort_start: date | None
    cohort_end: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
