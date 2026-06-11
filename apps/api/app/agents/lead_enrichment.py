"""Lead Enrichment Agent.

Operates on candidates created earlier in this run (or pre-existing) to:
- normalize titles / regions
- mark consent / source confidence based on heuristics
- detect candidate type when missing

This mock does cosmetic updates with believable log messages; the real version
will call the LLM adapter to do entity normalization at scale.
"""

from __future__ import annotations

from typing import AsyncIterator

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate
from app.models.enums import AgentType


_TITLE_NORMALIZATIONS = {
    "Frigoriste compagnon": "Frigoriste — compagnon CCQ",
    "Frigoriste industriel": "Frigoriste industriel (ammoniaque / CO₂)",
    "Technicienne en réfrigération commerciale": "Technicienne en réfrigération commerciale",
    "Technicienne CVAC-R": "Technicienne CVAC-R polyvalente",
    "Apprenti frigoriste - 2e année": "Apprenti CCQ — 2e période (2 000 h complétées)",
}


class LeadEnrichmentAgent(Agent):
    agent_type = AgentType.LEAD_ENRICHMENT
    display_name = "Lead Enrichment"
    icon = "🧹"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        yield AgentStep(
            ts=self.now_iso(),
            icon="🧹",
            message="Démarrage de l'enrichissement — normalisation, déduplication, confiance source.",
        )
        await self.think(0.5)

        if not ctx.created_candidate_ids:
            yield AgentStep(
                ts=self.now_iso(),
                icon="⚠",
                message="Aucun lead à enrichir dans ce run.",
            )
            return

        # Dedupe pass (simulated: count, no-op for the demo data we just created)
        yield AgentStep(
            ts=self.now_iso(),
            icon="🔁",
            message=f"Comparaison des {len(ctx.created_candidate_ids)} nouveaux leads contre la base existante (clé : nom + courriel).",
        )
        await self.think(0.8)
        yield AgentStep(
            ts=self.now_iso(),
            icon="✔",
            message="Aucun doublon détecté.",
        )
        await self.think(0.3)

        enriched_count = 0
        for cand_id in ctx.created_candidate_ids:
            cand = ctx.db.get(Candidate, cand_id)
            if cand is None:
                continue

            actions: list[str] = []

            # Normalize title
            if cand.current_title and cand.current_title in _TITLE_NORMALIZATIONS:
                new_title = _TITLE_NORMALIZATIONS[cand.current_title]
                cand.current_title = new_title
                actions.append("titre normalisé")

            # Promote source confidence for candidates with email + URL
            if cand.contact_email and cand.profile_url and (cand.source_confidence or 0) < 85:
                cand.source_confidence = 85
                actions.append("confiance source ↑ 85")

            # Mark consent intent based on where they came from
            if cand.candidate_type == "finissant" and cand.consent_status == "pending":
                cand.consent_status = "consent_request_sent"
                actions.append("demande de consentement créée")

            if actions:
                ctx.db.commit()
                ctx.db.refresh(cand)
                enriched_count += 1
                yield AgentStep(
                    ts=self.now_iso(),
                    icon="✨",
                    message=f"{cand.full_name} — {', '.join(actions)}.",
                    detail={
                        "increment": {"candidates_enriched": 1},
                        "candidate_id": str(cand.id),
                    },
                )
                await self.think(0.3)

        yield AgentStep(
            ts=self.now_iso(),
            icon="✅",
            message=f"Enrichissement terminé — {enriched_count} fiche(s) raffinée(s).",
        )