"""API router aggregator.

Phase 1 wired in health + auth placeholders.
Phase 2 adds CRUD for campaigns, candidates, and sources (spec §9).
Subsequent phases register additional routers (users, schools, events,
agent_runs, outreach, reports, assistant, settings).
"""

from fastapi import APIRouter

from app.api.routes import auth, campaigns, candidates, health, sources

api_router = APIRouter()

# Health endpoints sit at /api/health and /api/health/ready
api_router.include_router(health.router)

# Auth placeholders sit at /api/auth/* (Phase 2 still placeholders; real auth in Phase 3)
api_router.include_router(auth.router)

# Phase 2 CRUD
api_router.include_router(campaigns.router)
api_router.include_router(candidates.router)
api_router.include_router(sources.router)
