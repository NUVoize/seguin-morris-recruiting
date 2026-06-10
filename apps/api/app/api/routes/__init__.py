"""API router aggregator.

Phase 1 wires in health + auth placeholders. Subsequent phases register additional
routers (users, campaigns, candidates, sources, schools, events, agent_runs, outreach,
reports, assistant, settings) per spec §9.
"""

from fastapi import APIRouter

from app.api.routes import auth, health

api_router = APIRouter()

# Health endpoints sit at /api/health and /api/health/ready
api_router.include_router(health.router)

# Auth placeholders sit at /api/auth/* (Phase 2 fills them in)
api_router.include_router(auth.router)
