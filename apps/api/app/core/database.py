"""SQLAlchemy engine, session, and Base.

The declarative `Base` lives in `app.models.base` (where the models do).
We re-export it here so existing imports `from app.core.database import Base`
continue to work — useful for Alembic env.py and any future utilities.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # re-export for backwards compatibility

engine = create_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    future=True,
    # Fail-fast on DB unavailability — keeps readiness probes from hanging in tests
    # and gives clear "degraded" status to load balancers.
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    future=True,
)


# Re-export Base so `from app.core.database import Base` still works.
__all__ = ["Base", "SessionLocal", "engine", "get_db"]


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and cleans up after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
