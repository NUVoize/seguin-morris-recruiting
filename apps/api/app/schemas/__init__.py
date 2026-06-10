"""Pydantic schemas — request/response shapes for the API.

Three patterns per resource:
  - {Resource}Base       : shared fields, used for Create + Update
  - {Resource}Create     : Base + required-on-create fields
  - {Resource}Update     : all-optional override of Base for PATCH
  - {Resource}Read       : Base + read-only metadata (id, timestamps)
"""

from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate
from app.schemas.source import LeadSourceCreate, LeadSourceRead, LeadSourceUpdate

__all__ = [
    "CampaignCreate",
    "CampaignRead",
    "CampaignUpdate",
    "CandidateCreate",
    "CandidateRead",
    "CandidateUpdate",
    "LeadSourceCreate",
    "LeadSourceRead",
    "LeadSourceUpdate",
]
