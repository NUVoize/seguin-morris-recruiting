"""Public model registry. Importing this module registers all models on Base.metadata,
which is what Alembic's autogenerate needs to detect schema changes.

Import order matters slightly — model files with foreign keys reference earlier ones.
"""

from app.models.audit import AuditLog, RetentionJob
from app.models.auth import Role, User
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.knowledge import AssistantQuery, KnowledgeDocument
from app.models.operations import AgentRun, Note, OutreachEvent
from app.models.recruiting import (
    Campaign,
    CampaignCandidate,
    Candidate,
    CandidateQualification,
)
from app.models.settings import BrandSettings, EmailSettings, LLMSettings
from app.models.sourcing import (
    LeadSource,
    RecruitingEvent,
    SchoolProgram,
    SourceMention,
)

__all__ = [
    # base
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    # auth
    "Role",
    "User",
    # recruiting
    "Campaign",
    "CampaignCandidate",
    "Candidate",
    "CandidateQualification",
    # sourcing
    "LeadSource",
    "RecruitingEvent",
    "SchoolProgram",
    "SourceMention",
    # operations
    "AgentRun",
    "Note",
    "OutreachEvent",
    # knowledge
    "AssistantQuery",
    "KnowledgeDocument",
    # settings
    "BrandSettings",
    "EmailSettings",
    "LLMSettings",
    # audit
    "AuditLog",
    "RetentionJob",
]
