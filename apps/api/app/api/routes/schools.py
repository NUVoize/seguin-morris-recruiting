"""School program directory endpoints — spec §9 (/api/programs).

Read-only in this phase: the directory is seeded from the recruiting research
(scripts.seed_real_sources). Sorted so the most actionable cohorts surface
first (soonest cohort_end, nulls last).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SchoolProgram
from app.schemas import SchoolProgramRead

router = APIRouter(prefix="/programs", tags=["schools"])


@router.get("", response_model=list[SchoolProgramRead])
def list_programs(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    program_type: str | None = Query(default=None, pattern="^(DEP|DEC|AEC)$"),
) -> list[SchoolProgram]:
    stmt = select(SchoolProgram).order_by(
        SchoolProgram.cohort_end.asc().nulls_last(),
        SchoolProgram.institution_name.asc(),
    )
    if program_type is not None:
        stmt = stmt.where(SchoolProgram.program_type == program_type)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


@router.get("/{program_id}", response_model=SchoolProgramRead)
def get_program(program_id: uuid.UUID, db: Session = Depends(get_db)) -> SchoolProgram:
    program = db.get(SchoolProgram, program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program
