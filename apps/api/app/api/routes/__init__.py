"""API router aggregator.

Phase 1 wired in health + auth placeholders.
Phase 2 added CRUD for campaigns, candidates, and sources (spec §9).
Phase 3 adds the agent_runs endpoint that powers the live agent theater UI.
Subsequent phases register additional routers (users, schools, events,
outreach, reports, assistant, settings).
"""

from fastapi import APIRouter

from app.api.routes import agent_runs, auth, campaigns, candidates, health, sources

api_router = APIRouter()

# Health endpoints sit at /api/health and /api/health/ready
api_router.include_router(health.router)

# Auth placeholders sit at /api/auth/*
api_router.include_router(auth.router)

# Phase 2 CRUD
api_router.include_router(campaigns.router)
api_router.include_router(candidates.router)
api_router.include_router(sources.router)

# Phase 3 - agent orchestration
api_router.include_router(agent_runs.router)