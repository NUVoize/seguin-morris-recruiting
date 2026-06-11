"""Base class for all recruiting agents.

An Agent is one phase of the discovery -> enrichment -> ranking pipeline.
It writes its own AgentRun row, streams a step-by-step log into output_summary
(as JSON), produces side effects (candidates, qualifications, scores), and
never calls an LLM provider or email provider directly - only through adapters
(spec hard rule).

For Phase 3 demo, every concrete agent is a mock agent: it sleeps to simulate
work and produces realistic Quebec-recruiting data so the UI shows a believable
run. Real scrapers / LLM calls slot in later behind the same interface.
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AgentRun
from app.models.enums import AgentRunStatus, AgentType

logger = logging.getLogger(__name__)


@dataclass
class AgentStep:
    """One line of progress an agent emits as it works."""

    ts: str
    icon: str
    message: str
    detail: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"ts": self.ts, "icon": self.icon, "message": self.message}
        if self.detail is not None:
            out["detail"] = self.detail
        return out


@dataclass
class AgentContext:
    """Mutable state passed down a chain of agents in one orchestrator run.

    Each agent reads the campaign + previous outputs, appends its own steps,
    records counts, and may stash IDs of records it created.
    """

    campaign_id: UUID | None
    db: Session
    created_candidate_ids: list[UUID] = field(default_factory=list)
    enriched_candidate_ids: list[UUID] = field(default_factory=list)

    def remember_created(self, candidate_id: UUID) -> None:
        self.created_candidate_ids.append(candidate_id)
        self.enriched_candidate_ids.append(candidate_id)


class Agent(abc.ABC):
    """Abstract base for every named agent in the system."""

    agent_type: AgentType
    display_name: str = ""
    icon: str = "*"

    async def execute(self, ctx: AgentContext) -> AgentRun:
        """Run this agent end-to-end against the shared context.

        Persists an AgentRun row whose status goes PENDING -> RUNNING -> COMPLETED/FAILED.
        Streams its progress into output_summary so polling clients can render it.
        """

        steps: list[AgentStep] = []
        counts: dict[str, int] = {}
        run = AgentRun(
            campaign_id=ctx.campaign_id,
            agent_type=self.agent_type,
            status=AgentRunStatus.RUNNING,
            input_payload={"agent": self.agent_type.value},
            output_summary=json.dumps(self._snapshot(steps, counts, status="running")),
            started_at=datetime.now(timezone.utc),
        )
        ctx.db.add(run)
        ctx.db.commit()
        ctx.db.refresh(run)

        try:
            async for step in self.steps(ctx):
                steps.append(step)
                self._tally(step, counts)
                # Persist progress on every step so the UI polls mid-run.
                run.output_summary = json.dumps(self._snapshot(steps, counts, status="running"))
                ctx.db.commit()

            run.status = AgentRunStatus.COMPLETED
            run.completed_at = datetime.now(timezone.utc)
            run.output_summary = json.dumps(self._snapshot(steps, counts, status="completed"))
            ctx.db.commit()
            ctx.db.refresh(run)
            return run

        except Exception as exc:  # noqa: BLE001 - broad on purpose; surfaces in UI
            logger.exception("Agent %s crashed", self.agent_type)
            run.status = AgentRunStatus.FAILED
            run.completed_at = datetime.now(timezone.utc)
            run.error_log = {"type": type(exc).__name__, "message": str(exc)}
            run.output_summary = json.dumps(self._snapshot(steps, counts, status="failed"))
            ctx.db.commit()
            return run

    @abc.abstractmethod
    def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        """Async generator yielding AgentStep records as work happens."""
        raise NotImplementedError
        yield  # pragma: no cover - keeps the type checker happy

    # ---------- helpers ----------

    def _snapshot(
        self,
        steps: list[AgentStep],
        counts: dict[str, int],
        *,
        status: str,
    ) -> dict[str, Any]:
        return {
            "agent_type": self.agent_type.value,
            "display_name": self.display_name,
            "icon": self.icon,
            "status": status,
            "steps": [s.to_dict() for s in steps],
            "counts": counts,
        }

    def _tally(self, step: AgentStep, counts: dict[str, int]) -> None:
        if step.detail and "increment" in step.detail:
            for key, val in step.detail["increment"].items():
                counts[key] = counts.get(key, 0) + int(val)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    @staticmethod
    async def think(seconds: float) -> None:
        """Sleep - in the demo, this is the moment the UI watches."""
        await asyncio.sleep(seconds)