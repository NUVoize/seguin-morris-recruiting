"""Fit Ranking Agent.

Scores each candidate against the campaign requirements using the rubric from
the spec:
    cert_match              25
    refrigeration_relevance 20
    experience_fit          15
    region_fit              15
    service_industrial_fit  10
    contactability          10
    recency_source          5

Per spec hard rule: the score is advisory. The recruiter validates certifications
before any hiring decision. The fit_summary always reminds the recruiter what to
double-check.
"""

from __future__ import annotations

from typing import AsyncIterator

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate, CandidateQualification
from app.models.enums import AgentType, QualificationStatus, QualificationType


_RUBRIC_WEIGHTS = {
    "cert_match": 25,
    "refrigeration_relevance": 20,
    "experience_fit": 15,
    "region_fit": 15,
    "service_industrial_fit": 10,
    "contactability": 10,
    "recency_source": 5,
}

# Target Quebec regions for the demo campaign
_TARGET_REGIONS = {"Montréal", "Longueuil", "Laval", "Québec", "Sherbrooke", "Gatineau"}


def _score_candidate(cand: Candidate, quals: list[CandidateQualification]) -> tuple[int, str, str]:
    """Return (score, label, summary). Score is 0-100."""

    qtypes_confirmed = {
        q.qualification_type
        for q in quals
        if q.qualification_status in (QualificationStatus.CONFIRMED, QualificationStatus.CLAIMED)
    }
    qtypes_inferred = {q.qualification_type for q in quals if q.qualification_status == QualificationStatus.INFERRED}
    has_dep = QualificationType.DEP in qtypes_confirmed or QualificationType.DEP in qtypes_inferred
    has_ccq = any(
        t in qtypes_confirmed
        for t in (QualificationType.CCQ_APPRENTICE, QualificationType.CCQ_COMPANION)
    )
    has_companion = QualificationType.CCQ_COMPANION in qtypes_confirmed
    has_halo = QualificationType.HALOCARBURES in (qtypes_confirmed | qtypes_inferred)
    has_sf = (
        QualificationType.SF1 in (qtypes_confirmed | qtypes_inferred)
        or QualificationType.SF2 in (qtypes_confirmed | qtypes_inferred)
    )
    has_license = QualificationType.DRIVER_LICENSE in qtypes_confirmed

    breakdown: dict[str, int] = {}

    # Certification match
    cert_pts = 0
    if has_dep:
        cert_pts += 10
    if has_ccq:
        cert_pts += 8
    if has_halo:
        cert_pts += 4
    if has_sf:
        cert_pts += 3
    breakdown["cert_match"] = min(cert_pts, _RUBRIC_WEIGHTS["cert_match"])

    # Refrigeration relevance — implied by title / candidate_type
    title = (cand.current_title or "").lower()
    typ = (cand.candidate_type or "").lower()
    refrig_pts = 0
    if any(k in title for k in ("frigoriste", "réfrigération", "cvac-r")):
        refrig_pts = 20
    elif "finissant" in typ or "apprenti" in title:
        refrig_pts = 16
    elif "technicien" in title:
        refrig_pts = 14
    breakdown["refrigeration_relevance"] = refrig_pts

    # Experience fit
    if has_companion or "industriel" in title:
        breakdown["experience_fit"] = 15
    elif has_ccq or "compagnon" in title:
        breakdown["experience_fit"] = 13
    elif "apprenti" in title:
        breakdown["experience_fit"] = 9
    elif "finissant" in typ:
        breakdown["experience_fit"] = 6
    else:
        breakdown["experience_fit"] = 4

    # Region fit
    breakdown["region_fit"] = 15 if (cand.region in _TARGET_REGIONS) else 6

    # Service / commercial / industrial fit
    if "commercial" in title or "service" in title or "polyvalent" in title:
        breakdown["service_industrial_fit"] = 10
    elif "industriel" in title:
        breakdown["service_industrial_fit"] = 7
    else:
        breakdown["service_industrial_fit"] = 5

    # Contactability
    contact_pts = 0
    if cand.contact_email:
        contact_pts += 6
    if cand.contact_phone:
        contact_pts += 3
    if cand.profile_url:
        contact_pts += 1
    breakdown["contactability"] = contact_pts

    # Recency / source quality
    breakdown["recency_source"] = 4 if (cand.source_confidence or 0) >= 80 else 2

    total = sum(breakdown.values())
    total = min(total, 100)

    # Label
    if total >= 80:
        label = "Strong match"
    elif total >= 60:
        label = "Promising"
    elif total >= 40:
        label = "Needs review"
    else:
        label = "Off-profile"

    # Recruiter-facing summary - always advisory tone
    missing_checks: list[str] = []
    if not has_halo:
        missing_checks.append("halocarbures")
    if not has_sf and "industriel" not in title:
        missing_checks.append("SF-1/SF-2")
    if not has_license:
        missing_checks.append("permis classe 5")

    if missing_checks:
        summary = f"{label}. Le recruteur doit vérifier : {', '.join(missing_checks)}."
    else:
        summary = f"{label}. Profil aligné — vérification finale standard requise."

    return total, label, summary


class FitRankingAgent(Agent):
    agent_type = AgentType.FIT_RANKING
    display_name = "Fit Ranking"
    icon = "🎯"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        yield AgentStep(
            ts=self.now_iso(),
            icon="🎯",
            message="Application de la grille de pondération : certifications 25, pertinence 20, expérience 15, région 15, service/industriel 10, contactabilité 10, fraîcheur source 5.",
        )
        await self.think(0.7)

        if not ctx.enriched_candidate_ids:
            yield AgentStep(
                ts=self.now_iso(),
                icon="⚠",
                message="Aucun candidat à scorer.",
            )
            return

        scores_assigned = 0
        strong_matches = 0
        from sqlalchemy import select

        for cand_id in ctx.enriched_candidate_ids:
            cand = ctx.db.get(Candidate, cand_id)
            if cand is None:
                continue
            quals = list(
                ctx.db.execute(
                    select(CandidateQualification).where(CandidateQualification.candidate_id == cand.id)
                ).scalars()
            )
            score, label, summary = _score_candidate(cand, quals)
            cand.fit_score = score
            cand.fit_label = label
            cand.fit_summary = summary
            ctx.db.commit()
            scores_assigned += 1
            if label == "Strong match":
                strong_matches += 1

            yield AgentStep(
                ts=self.now_iso(),
                icon="📊",
                message=f"{cand.full_name} → {score}/100 — {label}.",
                detail={
                    "increment": {"scored": 1, "strong_matches": 1 if label == "Strong match" else 0},
                    "candidate_id": str(cand.id),
                    "score": score,
                    "label": label,
                },
            )
            await self.think(0.4)

        yield AgentStep(
            ts=self.now_iso(),
            icon="ℹ",
            message="Le score est consultatif. Le recruteur valide les certifications avant toute décision.",
        )
        await self.think(0.3)
        yield AgentStep(
            ts=self.now_iso(),
            icon="✅",
            message=f"Classement terminé — {scores_assigned} candidat(s) scoré(s), {strong_matches} 'Strong match'.",
        )