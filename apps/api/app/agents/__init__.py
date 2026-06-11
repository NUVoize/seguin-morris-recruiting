"""Multi-agent recruiting intelligence package.

Exports the orchestrator and the agent classes. Concrete agents live in their
own modules and inherit from app.agents.base.Agent.
"""

from app.agents.base import Agent, AgentContext, AgentStep
from app.agents.candidate_vetting import CandidateVettingAgent
from app.agents.employment_source import EmploymentSourceAgent
from app.agents.fit_ranking import FitRankingAgent
from app.agents.lead_enrichment import LeadEnrichmentAgent
from app.agents.orchestrator import DEFAULT_PIPELINE, run_pipeline
from app.agents.school_pipeline import SchoolPipelineAgent

__all__ = [
    "Agent",
    "AgentContext",
    "AgentStep",
    "DEFAULT_PIPELINE",
    "run_pipeline",
    "EmploymentSourceAgent",
    "SchoolPipelineAgent",
    "LeadEnrichmentAgent",
    "CandidateVettingAgent",
    "FitRankingAgent",
]