"""SQLAlchemy engine, session, and Base. Used by app code and Alembic migrations."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

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


class Base(DeclarativeBase):
    """Declarative base for all ORM models. Phase 2 will register models against this."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and cleans up after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
