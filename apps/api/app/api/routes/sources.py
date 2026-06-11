"""LeadSource CRUD endpoints — gates allowed_to_scrape per spec hard rule.

Changes to `allowed_to_scrape` are audit-logged (spec hard rule: never skip
audit logs on important actions). Flipping that flag is the legal gate for
all automated collection on a source.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import AuditLog, LeadSource
from app.models.enums import SourceType
from app.schemas import LeadSourceCreate, LeadSourceRead, LeadSourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


def _serialize_for_db(data: dict) -> dict:
    """HttpUrl pydantic instances need to be cast to string for the TEXT column."""
    if "url" in data and data["url"] is not None:
        data["url"] = str(data["url"])
    return data


@router.post("", response_model=LeadSourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: LeadSourceCreate, db: Session = Depends(get_db)) -> LeadSource:
    source = LeadSource(**_serialize_for_db(payload.model_dump()))
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("", response_model=list[LeadSourceRead])
def list_sources(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    source_type: SourceType | None = None,
    allowed_to_scrape: bool | None = None,
) -> list[LeadSource]:
    stmt = select(LeadSource).order_by(LeadSource.name.asc())
    if source_type is not None:
        stmt = stmt.where(LeadSource.source_type == source_type)
    if allowed_to_scrape is not None:
        stmt = stmt.where(LeadSource.allowed_to_scrape == allowed_to_scrape)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


@router.get("/{source_id}", response_model=LeadSourceRead)
def get_source(source_id: uuid.UUID, db: Session = Depends(get_db)) -> LeadSource:
    source = db.get(LeadSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.patch("/{source_id}", response_model=LeadSourceRead)
def update_source(
    source_id: uuid.UUID,
    payload: LeadSourceUpdate,
    db: Session = Depends(get_db),
) -> LeadSource:
    source = db.get(LeadSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    updates = _serialize_for_db(payload.model_dump(exclude_unset=True))

    # Audit the scrape-policy gate before applying — hard rule #6.
    if "allowed_to_scrape" in updates and updates["allowed_to_scrape"] != source.allowed_to_scrape:
        db.add(
            AuditLog(
                user_id=None,  # auth placeholder in v1; real user once login ships
                action="source.scrape_policy_changed",
                entity_type="lead_source",
                entity_id=source.id,
                audit_metadata={
                    "source_name": source.name,
                    "from": source.allowed_to_scrape,
                    "to": updates["allowed_to_scrape"],
                },
            )
        )

    for field, value in updates.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    source = db.get(LeadSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    db.delete(source)
    db.commit()
