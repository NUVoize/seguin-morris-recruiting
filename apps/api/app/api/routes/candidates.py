"""Candidate CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Candidate
from app.models.enums import PipelineStatus
from app.schemas import CandidateCreate, CandidateRead, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateRead, status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)) -> Candidate:
    # Need at least one identifier — name, email, or profile_url
    if not (payload.full_name or payload.contact_email or payload.profile_url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one of full_name, contact_email, or profile_url is required.",
        )

    data = payload.model_dump()
    if data.get("contact_email"):
        data["contact_email"] = str(data["contact_email"])
    candidate = Candidate(**data)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("", response_model=list[CandidateRead])
def list_candidates(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    pipeline_status: PipelineStatus | None = None,
    region: str | None = None,
) -> list[Candidate]:
    stmt = select(Candidate).order_by(Candidate.created_at.desc())
    if pipeline_status is not None:
        stmt = stmt.where(Candidate.pipeline_status == pipeline_status)
    if region is not None:
        stmt = stmt.where(Candidate.region == region)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: uuid.UUID, db: Session = Depends(get_db)) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}", response_model=CandidateRead)
def update_candidate(
    candidate_id: uuid.UUID,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    updates = payload.model_dump(exclude_unset=True)
    if "contact_email" in updates and updates["contact_email"] is not None:
        updates["contact_email"] = str(updates["contact_email"])
    for field, value in updates.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
