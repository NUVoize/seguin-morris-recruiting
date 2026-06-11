"""Employment Source Agent.

Simulates scraping multiple Quebec job boards / public profile sources to discover
new frigoriste leads. In v1 this is a mock that returns curated, realistic data;
the real version will use Playwright behind the source-policy gate
(allowed_to_scrape == True) and an LLM extractor through the LLM adapter.
"""

from __future__ import annotations

import random
from typing import AsyncIterator

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate
from app.models.enums import AgentType, PipelineStatus


# Curated mock results - representative of what a real scraper would find.
# Names, titles, regions, and source URLs are realistic for the Quebec market.
_MOCK_LEADS = [
    {
        "full_name": "Olivier Beaupré",
        "current_title": "Frigoriste compagnon",
        "region": "Montréal",
        "contact_email": "o.beaupre@example.ca",
        "profile_url": "https://www.jobillico.com/profil/olivier-beaupre",
        "source_label": "Jobillico",
    },
    {
        "full_name": "Marie-Claude Fortin",
        "current_title": "Technicienne CVAC-R",
        "region": "Québec",
        "contact_email": "mc.fortin@example.ca",
        "profile_url": "https://ca.indeed.com/cv/marie-claude-fortin",
        "source_label": "Indeed",
    },
    {
        "full_name": "Hugo Lefebvre",
        "current_title": "Apprenti frigoriste - 2e année",
        "region": "Laval",
        "contact_email": "hugo.lefebvre@example.ca",
        "profile_url": "https://www.jobboom.com/profil/hugo-lefebvre",
        "source_label": "Jobboom",
    },
    {
        "full_name": "Vincent Therrien",
        "current_title": "Frigoriste industriel",
        "region": "Saguenay",
        "contact_email": "v.therrien@example.ca",
        "profile_url": "https://www.linkedin.com/in/vincent-therrien-frigoriste",
        "source_label": "LinkedIn",
    },
    {
        "full_name": "Audrey Boisvert",
        "current_title": "Technicienne en réfrigération commerciale",
        "region": "Longueuil",
        "contact_email": "audrey.boisvert@example.ca",
        "profile_url": "https://www.jobillico.com/profil/audrey-boisvert",
        "source_label": "Jobillico",
    },
]


class EmploymentSourceAgent(Agent):
    agent_type = AgentType.EMPLOYMENT_SOURCE
    display_name = "Employment Source"
    icon = "🔍"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        yield AgentStep(
            ts=self.now_iso(),
            icon="🔍",
            message="Initialisation — vérification de la politique de sources (allowed_to_scrape).",
        )
        await self.think(0.8)

        yield AgentStep(
            ts=self.now_iso(),
            icon="🌐",
            message="Connexion à Jobillico — recherche : 'frigoriste OR \"technicien en réfrigération\" Québec'.",
        )
        await self.think(1.2)

        # Pick a random subset of 3-4 leads per run so it doesn't look identical every time
        n = random.randint(3, 4)
        leads = random.sample(_MOCK_LEADS, n)

        # Group by source for nicer log lines
        by_source: dict[str, list[dict]] = {}
        for lead in leads:
            by_source.setdefault(lead["source_label"], []).append(lead)

        for source_label, source_leads in by_source.items():
            yield AgentStep(
                ts=self.now_iso(),
                icon="📡",
                message=f"Source {source_label} — {len(source_leads)} profil(s) pertinent(s) détecté(s).",
            )
            await self.think(0.6)
            for lead in source_leads:
                # Persist as Candidate with default pipeline status NEW
                cand = Candidate(
                    full_name=lead["full_name"],
                    current_title=lead["current_title"],
                    region=lead["region"],
                    candidate_type="frigoriste",
                    contact_email=lead["contact_email"],
                    profile_url=lead["profile_url"],
                    pipeline_status=PipelineStatus.NEW,
                    source_confidence=70,
                    consent_status="unknown",
                )
                ctx.db.add(cand)
                ctx.db.commit()
                ctx.db.refresh(cand)
                ctx.remember_created(cand.id)

                yield AgentStep(
                    ts=self.now_iso(),
                    icon="➕",
                    message=f"Lead ajouté : {lead['full_name']} ({lead['region']}) via {source_label}.",
                    detail={
                        "increment": {"candidates_created": 1, "sources_visited": 0},
                        "candidate_id": str(cand.id),
                        "source_url": lead["profile_url"],
                    },
                )
                await self.think(0.5)

            yield AgentStep(
                ts=self.now_iso(),
                icon="✔",
                message=f"{source_label} : exploration terminée.",
                detail={"increment": {"sources_visited": 1}},
            )
            await self.think(0.3)

        yield AgentStep(
            ts=self.now_iso(),
            icon="✅",
            message=f"Phase de découverte terminée — {len(leads)} candidat(s) ajouté(s) au pipeline.",
        )