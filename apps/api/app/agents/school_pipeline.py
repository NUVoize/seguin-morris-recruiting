"""School Pipeline Agent.

Simulates reaching out to Quebec DEP / DEC / AEC programs to surface finissants
ready to join the workforce. Real version will call school placement APIs +
parse public cohort calendars; this mock returns curated data tied to the
seven real DEP centers documented in the recruiting research.
"""

from __future__ import annotations

import random
from typing import AsyncIterator

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate
from app.models.enums import AgentType, PipelineStatus


# DEP centers from the Quebec recruiting research (real institutions).
_DEP_CENTERS = [
    ("CFP de Québec", "Québec", "DEP Réfrigération 5386"),
    ("CFP Vision 20 20", "Victoriaville", "DEP Réfrigération 5386"),
    ("CFP 24-Juin", "Sherbrooke", "DEP Réfrigération 5386"),
    ("École Polymécanique de Laval", "Laval", "DEP Réfrigération 5386"),
    ("CFP Pierre-Dupuy", "Longueuil", "DEP Réfrigération 5386"),
    ("CFP de Lachine", "Lachine", "DEP Réfrigération 5386"),
    ("CFP Jonquière", "Jonquière", "DEP Réfrigération 5386"),
]

# Mock finissant profiles - varying levels of readiness.
_MOCK_FINISSANTS = [
    {
        "full_name": "Léa Pelletier",
        "current_title": "Finissante DEP Réfrigération - cohorte 2026",
        "contact_email": "lea.pelletier@example.ca",
    },
    {
        "full_name": "Samuel Roy",
        "current_title": "Finissant DEP Réfrigération - stage en cours",
        "contact_email": "samuel.roy@example.ca",
    },
    {
        "full_name": "Charles Veillette",
        "current_title": "Finissant DEP - sortie prévue dans 90 jours",
        "contact_email": "charles.veillette@example.ca",
    },
    {
        "full_name": "Florence Hamel",
        "current_title": "Élève DEP Réfrigération - 2e session",
        "contact_email": "florence.hamel@example.ca",
    },
]


class SchoolPipelineAgent(Agent):
    agent_type = AgentType.SCHOOL_PIPELINE
    display_name = "School Pipeline"
    icon = "🎓"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        yield AgentStep(
            ts=self.now_iso(),
            icon="🎓",
            message="Mobilisation des centres DEP Réfrigération 5386 (fenêtre 90-180 jours avant fin de cohorte).",
        )
        await self.think(0.7)

        # Contact 2-3 schools
        contacted_schools = random.sample(_DEP_CENTERS, k=random.randint(2, 3))
        for school_name, city, program in contacted_schools:
            yield AgentStep(
                ts=self.now_iso(),
                icon="📞",
                message=f"Contact établi : {school_name} ({city}) — programme {program}.",
                detail={"increment": {"schools_contacted": 1}},
            )
            await self.think(0.8)

        # Get 2-3 finissants from those schools
        n_finissants = random.randint(2, 3)
        finissants = random.sample(_MOCK_FINISSANTS, n_finissants)

        for i, finissant in enumerate(finissants):
            school_name, city, _program = contacted_schools[i % len(contacted_schools)]
            yield AgentStep(
                ts=self.now_iso(),
                icon="🔎",
                message=f"Analyse du bottin {school_name} — finissant identifié : {finissant['full_name']}.",
            )
            await self.think(0.5)

            cand = Candidate(
                full_name=finissant["full_name"],
                current_title=finissant["current_title"],
                region=city,
                candidate_type="finissant",
                contact_email=finissant["contact_email"],
                profile_url=None,
                pipeline_status=PipelineStatus.NEW,
                source_confidence=85,
                consent_status="pending",
            )
            ctx.db.add(cand)
            ctx.db.commit()
            ctx.db.refresh(cand)
            ctx.remember_created(cand.id)

            yield AgentStep(
                ts=self.now_iso(),
                icon="➕",
                message=f"Finissant ajouté : {finissant['full_name']} — diplomation imminente.",
                detail={
                    "increment": {"candidates_created": 1},
                    "candidate_id": str(cand.id),
                    "school": school_name,
                },
            )
            await self.think(0.4)

        yield AgentStep(
            ts=self.now_iso(),
            icon="✅",
            message=f"Filière scolaire couverte — {len(finissants)} finissant(s) ajouté(s).",
        )