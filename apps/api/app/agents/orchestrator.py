"""Agent Orchestrator.

Runs the agent pipeline against a campaign:
    EmploymentSourceAgent
    SchoolPipelineAgent
    LeadEnrichmentAgent
    CandidateVettingAgent
    FitRankingAgent

Each agent writes its own AgentRun row and shares state via AgentContext.
The orchestrator is a thin coordinator - no business logic of its own, no
LLM calls (the agents themselves go through the LLM adapter).

For the v1 demo this runs as a FastAPI BackgroundTask. Phase 8+ will route
through Celery/Redis for queueing, retries, and multi-process workers.
"""

from __future__ import annotations

import logging
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.base import Agent, AgentContext
from app.agents.candidate_vetting import CandidateVettingAgent
from app.agents.employment_source import EmploymentSourceAgent
from app.agents.fit_ranking import FitRankingAgent
from app.agents.lead_enrichment import LeadEnrichmentAgent
from app.agents.school_pipeline import SchoolPipelineAgent
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


# Canonical pipeline order. Discovery agents come first (parallel-safe in
# practice; we run sequentially for visual clarity in the demo), then the
# enrichment / vetting / ranking chain which depends on prior results.
DEFAULT_PIPELINE: Sequence[type[Agent]] = (
    EmploymentSourceAgent,
    SchoolPipelineAgent,
    LeadEnrichmentAgent,
    CandidateVettingAgent,
    FitRankingAgent,
)


async def run_pipeline(campaign_id: UUID | None = None) -> AgentContext:
    """Run every agent in DEFAULT_PIPELINE against the given campaign.

    Opens its own DB session so it can be called from a BackgroundTask without
    interfering with the request-scoped session.
    """

    db: Session = SessionLocal()
    try:
        ctx = AgentContext(campaign_id=campaign_id, db=db)
        logger.info("Starting agent pipeline for campaign %s", campaign_id)
        for agent_cls in DEFAULT_PIPELINE:
            agent = agent_cls()
            logger.info("Running %s", agent.agent_type)
            await agent.execute(ctx)
        logger.info(
            "Pipeline finished. created=%d enriched=%d",
            len(ctx.created_candidate_ids),
            len(ctx.enriched_candidate_ids),
        )
        return ctx
    finally:
        db.close()