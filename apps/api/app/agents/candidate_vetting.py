"""Candidate Vetting Agent.

For each candidate created in this run, infers and records qualifications:
DEP, DEC, AEC, CCQ apprentice/companion, ASP 30h, SF-1, SF-2, halocarbures,
driver license. Writes CandidateQualification rows with status ranging from
'inferred' to 'claimed' (recruiter still verifies, per the spec hard rule:
the AI does not make hiring decisions).

Mock infers from job title + candidate_type using simple rules; real version
will use the LLM adapter to extract from full profile text.
"""

from __future__ import annotations

import random
from typing import AsyncIterator

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate, CandidateQualification
from app.models.enums import AgentType, QualificationStatus, QualificationType


def _infer_qualifications(cand: Candidate) -> list[tuple[QualificationType, QualificationStatus, str]]:
    """Return (type, status, evidence) tuples. Rules are intentionally simple."""

    title = (cand.current_title or "").lower()
    typ = (cand.candidate_type or "").lower()
    out: list[tuple[QualificationType, QualificationStatus, str]] = []

    # DEP is implied for finissants and most frigoristes
    if "finissant" in typ or "dep" in title or "frigoriste" in title or "réfrigération" in title:
        out.append((
            QualificationType.DEP,
            QualificationStatus.INFERRED if "finissant" in typ else QualificationStatus.CLAIMED,
            "Mentionné dans le titre / type de candidat",
        ))

    # CCQ apprentice / companion
    if "apprenti" in title or "2e période" in title:
        out.append((
            QualificationType.CCQ_APPRENTICE,
            QualificationStatus.CLAIMED,
            "Mention 'apprenti' dans le titre",
        ))
    elif "compagnon" in title:
        out.append((
            QualificationType.CCQ_COMPANION,
            QualificationStatus.CLAIMED,
            "Mention 'compagnon' dans le titre",
        ))

    # Halocarbures - infer for any frigoriste actively working
    if "compagnon" in title or "industriel" in title or "commercial" in title:
        out.append((
            QualificationType.HALOCARBURES,
            QualificationStatus.INFERRED,
            "Métier exige la qualification environnementale halocarbures",
        ))

    # SF-1 for industrial profiles
    if "industriel" in title:
        out.append((
            QualificationType.SF1,
            QualificationStatus.INFERRED,
            "Profil industriel - SF-1 probable",
        ))

    # SF-2 for service / commercial
    if "service" in title or "commercial" in title or "polyvalent" in title:
        out.append((
            QualificationType.SF2,
            QualificationStatus.INFERRED,
            "Profil service hors construction - SF-2 probable",
        ))

    # ASP 30h - random claim rate for the demo
    if "compagnon" in title or "industriel" in title:
        if random.random() < 0.6:
            out.append((
                QualificationType.ASP_30H,
                QualificationStatus.CLAIMED,
                "Carte ASP Construction 30 h déclarée",
            ))

    # Driver license - common
    if random.random() < 0.85:
        out.append((
            QualificationType.DRIVER_LICENSE,
            QualificationStatus.CLAIMED,
            "Permis classe 5 mentionné",
        ))

    return out


class CandidateVettingAgent(Agent):
    agent_type = AgentType.CANDIDATE_VETTING
    display_name = "Candidate Vetting"
    icon = "🛡"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        yield AgentStep(
            ts=self.now_iso(),
            icon="🛡",
            message="Démarrage du dépistage — détection DEP, CCQ, ASP 30 h, SF-1, SF-2, halocarbures, permis.",
        )
        await self.think(0.6)

        if not ctx.enriched_candidate_ids:
            yield AgentStep(
                ts=self.now_iso(),
                icon="⚠",
                message="Aucun candidat à dépister.",
            )
            return

        for cand_id in ctx.enriched_candidate_ids:
            cand = ctx.db.get(Candidate, cand_id)
            if cand is None:
                continue

            inferred = _infer_qualifications(cand)
            for qtype, qstatus, evidence in inferred:
                qual = CandidateQualification(
                    candidate_id=cand.id,
                    qualification_type=qtype,
                    qualification_status=qstatus,
                    evidence_text=evidence,
                )
                ctx.db.add(qual)
            ctx.db.commit()

            qtypes_str = ", ".join(q[0].value for q in inferred) or "aucune"
            yield AgentStep(
                ts=self.now_iso(),
                icon="🔬",
                message=f"{cand.full_name} → {len(inferred)} qualification(s) : {qtypes_str}.",
                detail={
                    "increment": {"qualifications_added": len(inferred)},
                    "candidate_id": str(cand.id),
                },
            )
            await self.think(0.4)

        yield AgentStep(
            ts=self.now_iso(),
            icon="ℹ",
            message="Rappel : ces qualifications sont consultatives. Le recruteur valide avant toute décision.",
        )
        await self.think(0.3)
        yield AgentStep(
            ts=self.now_iso(),
            icon="✅",
            message="Dépistage terminé.",
        )