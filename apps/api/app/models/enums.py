"""Enum types for the Seguin Morris recruiting domain.

Per spec §7. Using Python StrEnum + SQLAlchemy Enum(native_enum=False) so the
DB column is VARCHAR + CHECK constraint — much easier to migrate when we add
new enum values than Postgres native ENUM types (which require ALTER TYPE).
"""

import enum


class QualificationType(str, enum.Enum):
    """Recognized professional qualifications tracked per candidate.

    Quebec refrigeration / HVAC-R domain — see Refrigeration Specialist research PDF.
    """

    DEP = "DEP"  # Diplôme d'études professionnelles — frigoriste
    DEC = "DEC"  # Diplôme d'études collégiales — mécanique du bâtiment
    AEC = "AEC"  # Attestation d'études collégiales
    CCQ_APPRENTICE = "CCQ_APPRENTICE"  # Carte d'apprenti construction
    CCQ_COMPANION = "CCQ_COMPANION"  # Carte de compagnon construction
    ASP_30H = "ASP_30H"  # Carte ASP Construction 30h
    SF1 = "SF1"  # Système frigorifique classe 1 (non-construction)
    SF2 = "SF2"  # Système frigorifique classe 2 (non-construction)
    HALOCARBURES = "HALOCARBURES"  # Qualification environnementale halocarbures
    RBQ = "RBQ"  # Licence entrepreneur (15.10)
    DRIVER_LICENSE = "DRIVER_LICENSE"
    UNKNOWN = "UNKNOWN"


class QualificationStatus(str, enum.Enum):
    """How confident we are that the candidate actually holds a qualification."""

    CONFIRMED = "confirmed"  # verified by recruiter against an authoritative source
    CLAIMED = "claimed"  # candidate self-asserts (CV, profile)
    INFERRED = "inferred"  # deduced from job title, employer, school
    MISSING = "missing"  # confirmed not held
    UNKNOWN = "unknown"  # not yet checked


class SourceType(str, enum.Enum):
    """Category of a lead source."""

    JOB_BOARD = "job_board"
    SCHOOL = "school"
    ASSOCIATION = "association"
    EVENT = "event"
    SOCIAL = "social"
    COMPANY_SITE = "company_site"
    GOVERNMENT = "government"
    MANUAL = "manual"


class AccessMethod(str, enum.Enum):
    """How we can pull data from this source — gates automated scraping."""

    API = "api"  # proper API integration
    PUBLIC_PAGE = "public_page"  # static fetch
    BROWSER_AUTOMATION = "browser_automation"  # Playwright, only if allowed_to_scrape
    MANUAL_IMPORT = "manual_import"  # recruiter pastes / uploads
    BROWSER_CAPTURE = "browser_capture"  # extension-assisted, recruiter-driven


class AgentType(str, enum.Enum):
    """The ten agents per spec §3."""

    EMPLOYMENT_SOURCE = "employment_source"
    SCHOOL_PIPELINE = "school_pipeline"
    EVENT_DISCOVERY = "event_discovery"
    LEAD_ENRICHMENT = "lead_enrichment"
    CANDIDATE_VETTING = "candidate_vetting"
    FIT_RANKING = "fit_ranking"
    OUTREACH = "outreach"
    EMAIL_SYNC = "email_sync"
    ASSISTANT_KNOWLEDGE = "assistant_knowledge"
    REPORTING = "reporting"


class PipelineStatus(str, enum.Enum):
    """Kanban pipeline stages per spec §6 (Candidate Pipeline screen)."""

    NEW = "new"
    TO_REVIEW = "to_review"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class AgentRunStatus(str, enum.Enum):
    """Lifecycle of an agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutreachChannel(str, enum.Enum):
    """Communication channel for an outreach event."""

    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    LINKEDIN = "linkedin"
    IN_PERSON = "in_person"


class OutreachDirection(str, enum.Enum):
    """Inbound or outbound communication."""

    OUTBOUND = "outbound"
    INBOUND = "inbound"


class OutreachStatus(str, enum.Enum):
    """Lifecycle of an outreach message."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class Language(str, enum.Enum):
    """Supported UI / content languages per spec §11."""

    FR = "fr"
    EN = "en"


class CampaignStatus(str, enum.Enum):
    """Lifecycle of a recruiting campaign."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
