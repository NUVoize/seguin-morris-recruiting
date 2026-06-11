"""Agent run endpoints.

POST /api/agent-runs                Kick off a pipeline run (returns immediately).
GET  /api/agent-runs                List recent runs (UI polls this every ~1s).
GET  /api/agent-runs/{id}           One run with full step log.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents import DEFAULT_PIPELINE, run_pipeline
from app.core.database import get_db
from app.models import AgentRun
from app.schemas.agent_run import AgentRunRead, TriggerAgentRunResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent-runs", tags=["agent-runs"])


@router.post(
    "",
    response_model=TriggerAgentRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a pipeline run",
)
async def trigger_run(campaign_id: UUID | None = None) -> TriggerAgentRunResponse:
    """Kick off the agent pipeline as a fire-and-forget asyncio task.

    Returns 202 immediately. The UI is expected to poll GET /api/agent-runs
    to watch progress as each agent records its steps.

    For mockup mode the orchestrator runs in-process via asyncio.create_task.
    Production deployment moves this to Celery + Redis (Phase 6+).
    """

    # Fire-and-forget; the orchestrator opens its own DB session.
    task = asyncio.create_task(run_pipeline(campaign_id=campaign_id))
    # Keep a reference so the GC doesn't drop the task before it finishes.
    _pending_tasks.add(task)
    task.add_done_callback(_pending_tasks.discard)

    return TriggerAgentRunResponse(
        started_at=datetime.utcnow(),
        campaign_id=campaign_id,
        agents=[agent_cls.agent_type.value for agent_cls in DEFAULT_PIPELINE],
        message="Pipeline started. Poll /api/agent-runs to follow progress.",
    )


# Hold strong references to background tasks until they complete.
_pending_tasks: set[asyncio.Task] = set()


@router.get(
    "",
    response_model=list[AgentRunRead],
    summary="List recent agent runs",
)
def list_runs(
    campaign_id: UUID | None = Query(None),
    since: datetime | None = Query(
        None,
        description="Return only runs started at or after this ISO timestamp.",
    ),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[AgentRun]:
    stmt = select(AgentRun).order_by(AgentRun.started_at.asc()).limit(limit)
    if campaign_id is not None:
        stmt = stmt.where(AgentRun.campaign_id == campaign_id)
    if since is not None:
        stmt = stmt.where(AgentRun.started_at >= since)
    return list(db.execute(stmt).scalars())


@router.get(
    "/{run_id}",
    response_model=AgentRunRead,
    summary="Get one agent run",
)
def get_run(run_id: UUID, db: Session = Depends(get_db)) -> AgentRun:
    run = db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
    return run