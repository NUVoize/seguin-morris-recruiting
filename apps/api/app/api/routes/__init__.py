"""API router aggregator.

Phase 1 wired in health + auth placeholders.
Phase 2 added CRUD for campaigns, candidates, and sources (spec §9).
Phase 3 added the agent_runs endpoint powering the live agent theater UI.
Real-data track added the school program directory.
Auth milestone: every business router now requires a signed-in user
(spec hard rule: never skip role-based access). Health + login stay open.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.routes import agent_runs, auth, campaigns, candidates, health, schools, sources

api_router = APIRouter()

# Open endpoints: liveness probes + the login flow itself.
api_router.include_router(health.router)
api_router.include_router(auth.router)

# Everything below requires authentication. Per-endpoint permission gates
# (e.g. can_manage_sources on the scrape-policy flip) layer on top.
_authed = [Depends(get_current_user)]

api_router.include_router(campaigns.router, dependencies=_authed)
api_router.include_router(candidates.router, dependencies=_authed)
api_router.include_router(sources.router, dependencies=_authed)
api_router.include_router(agent_runs.router, dependencies=_authed)
api_router.include_router(schools.router, dependencies=_authed)
