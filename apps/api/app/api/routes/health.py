"""Health check endpoint. Used by Railway and local docker-compose smoke checks."""

from typing import Any

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["health"])
logger = structlog.get_logger(__name__)


@router.get("/health", summary="Liveness probe")
def health() -> dict[str, Any]:
    """Liveness — process is up and responding."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env,
    }


@router.get("/health/ready", summary="Readiness probe (checks DB)")
def health_ready(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Readiness — process is up *and* the database responds to SELECT 1."""
    db_status = "ok"
    db_error: str | None = None
    try:
        db.execute(text("SELECT 1")).scalar_one()
    except Exception as exc:  # noqa: BLE001 - readiness reports any failure
        db_status = "down"
        db_error = str(exc)
        logger.warning("health.db.unavailable", error=str(exc))

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "service": settings.app_name,
        "checks": {
            "database": {"status": db_status, "error": db_error},
        },
    }
