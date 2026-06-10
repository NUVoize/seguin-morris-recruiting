"""Knowledge documents + assistant queries — backs the Phase 8 text assistant.

KnowledgeDocument = approved company knowledge the assistant can ground on.
AssistantQuery = a recorded Q&A exchange with source attribution.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import Language


class KnowledgeDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A piece of approved company knowledge the assistant may use.

    Status starts as 'active'; documents can be 'archived' or 'deprecated'
    without being deleted (preserves audit trail for past assistant answers).
    """

    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        nullable=False,
    )
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )


class AssistantQuery(Base, UUIDPrimaryKeyMixin):
    """A recorded Q&A exchange with the assistant. Used for analytics + audit."""

    __tablename__ = "assistant_queries"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[Language | None] = mapped_column(
        Enum(Language, native_enum=False, length=8),
        nullable=True,
    )
    sources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
