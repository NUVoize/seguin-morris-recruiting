"""Seguin Morris Recruiting Intelligence Platform — FastAPI application entry point.

Designed by CTRL Solutions.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hooks for the API."""
    logger.info(
        "api.startup",
        env=settings.app_env,
        default_language=settings.app_default_language,
    )
    yield
    logger.info("api.shutdown")


app = FastAPI(
    title="Seguin Morris Recruiting Intelligence Platform",
    description="Internal bilingual multi-agent recruiting platform. Designed by CTRL Solutions.",
    version="0.1.0",
    docs_url="/api/docs" if settings.app_env != "production" else None,
    redoc_url="/api/redoc" if settings.app_env != "production" else None,
    openapi_url="/api/openapi.json" if settings.app_env != "production" else None,
    lifespan=lifespan,
)

# CORS — locked down for the internal tool; widen only if a separate front-end origin is added.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
