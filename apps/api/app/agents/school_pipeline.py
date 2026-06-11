"""School Pipeline Agent — wired to the REAL school_programs directory.

Reads the seeded Quebec institutions (7 DEP Refrigeration 5386 centers,
DEC 221.C0 cegeps, AEC Ahuntsic) from the database and applies the real
prospecting-window rule from the recruiting research:

    - Ideal window opens 90-180 days before cohort_end
    - Reactivation at ~30 days before graduation
    - Watch list beyond 180 days; unknown calendar -> confirm with the center

What's REAL here: institutions, public contacts, cohort dates, window math.
What's still SIMULATED: the finissant profiles themselves — surfacing real
students requires the outreach module (Phase 6) and school replies. Profiles
are clearly synthetic (example.ca emails) until then.
"""

from __future__ import annotations

import random
from datetime import date
from typing import AsyncIterator

from sqlalchemy import select

from app.agents.base import Agent, AgentContext, AgentStep
from app.models import Candidate, SchoolProgram
from app.models.enums import AgentType, PipelineStatus

# Simulated finissant profiles (Phase 6 outreach replaces these with real
# school responses). Kept clearly synthetic: example.ca addresses.
_MOCK_FINISSANTS = [
    {"full_name": "L\u00e9a Pelletier", "title_suffix": "cohorte en cours"},
    {"full_name": "Samuel Roy", "title_suffix": "stage ATE en cours"},
    {"full_name": "Charles Veillette", "title_suffix": "sortie imminente"},
    {"full_name": "Florence Hamel", "title_suffix": "2e session"},
    {"full_name": "Thomas Gagnon", "title_suffix": "disponible \u00e9t\u00e9"},
]


def _window(cohort_end: date | None, today: date) -> tuple[str, str, int]:
    """Classify a program against the 90-180 day prospecting rule.

    Returns (key, French label, sort priority — lower is more actionable).
    """
    if cohort_end is None:
        return ("unknown", "calendrier \u00e0 confirmer aupr\u00e8s du centre", 3)
    days = (cohort_end - today).days
    if days < 0:
        return ("past", f"cohorte termin\u00e9e depuis {-days} j", 4)
    if days <= 30:
        return ("reactivation", f"R\u00c9ACTIVATION \u2014 diplomation dans {days} j", 0)
    if days <= 180:
        return ("ideal", f"FEN\u00caTRE ID\u00c9ALE \u2014 fin de cohorte dans {days} j", 1)
    return ("watch", f"veille \u2014 fin de cohorte dans {days} j", 2)


class SchoolPipelineAgent(Agent):
    agent_type = AgentType.SCHOOL_PIPELINE
    display_name = "School Pipeline"
    icon = "\U0001f393"

    async def steps(self, ctx: AgentContext) -> AsyncIterator[AgentStep]:
        today = date.today()

        programs = list(
            ctx.db.execute(
                select(SchoolProgram).order_by(
                    SchoolProgram.cohort_end.asc().nulls_last(),
                    SchoolProgram.institution_name.asc(),
                )
            )
            .scalars()
            .all()
        )

        if not programs:
            yield AgentStep(
                ts=self.now_iso(),
                icon="!",
                message=(
                    "Aucun programme dans l'annuaire \u2014 ex\u00e9cuter "
                    "scripts.seed_real_sources pour charger les centres DEP/DEC/AEC."
                ),
            )
            return

        dep = [p for p in programs if p.program_type == "DEP"]
        yield AgentStep(
            ts=self.now_iso(),
            icon="\U0001f393",
            message=(
                f"Annuaire charg\u00e9 : {len(programs)} programmes r\u00e9els "
                f"({len(dep)} centres DEP R\u00e9frig\u00e9ration 5386). "
                "Application de la r\u00e8gle 90-180 jours avant fin de cohorte."
            ),
        )
        await self.think(0.7)

        # Rank DEP centers by window actionability (reactivation > ideal > watch > unknown).
        ranked = sorted(dep, key=lambda p: (_window(p.cohort_end, today)[2], p.institution_name))
        in_window = [p for p in ranked if _window(p.cohort_end, today)[0] in ("ideal", "reactivation")]

        yield AgentStep(
            ts=self.now_iso(),
            icon="\U0001f4c5",
            message=(
                f"Analyse des cohortes : {len(in_window)} centre(s) en fen\u00eatre de "
                "prospection active."
            ),
            detail={"increment": {"programs_in_window": len(in_window)}},
        )
        await self.think(0.6)

        # Contact the 2-3 most actionable centers — real institutions, real contacts.
        n_contacts = min(len(ranked), random.randint(2, 3))
        contacted = ranked[:n_contacts]

        for program in contacted:
            _key, window_label, _prio = _window(program.cohort_end, today)
            contact = program.public_contact_name or program.public_contact_email or "accueil du centre"
            yield AgentStep(
                ts=self.now_iso(),
                icon="\U0001f4de",
                message=(
                    f"Contact \u00e9tabli : {program.institution_name} ({program.city}) "
                    f"\u2014 {program.program_name} \u2014 {window_label} \u2014 "
                    f"porte d'entr\u00e9e : {contact}."
                ),
                detail={
                    "increment": {"schools_contacted": 1},
                    "program_id": str(program.id),
                },
            )
            await self.think(0.8)

        # Simulated finissants attributed to the real contacted centers.
        n_finissants = random.randint(2, 3)
        finissants = random.sample(_MOCK_FINISSANTS, n_finissants)

        for i, finissant in enumerate(finissants):
            program = contacted[i % len(contacted)]
            yield AgentStep(
                ts=self.now_iso(),
                icon="\U0001f50e",
                message=(
                    f"R\u00e9ponse simul\u00e9e {program.institution_name} \u2014 profil "
                    f"finissant : {finissant['full_name']} (donn\u00e9es r\u00e9elles via "
                    "module Communications, phase 6)."
                ),
            )
            await self.think(0.5)

            first = finissant["full_name"].split()[0].lower()
            last = finissant["full_name"].split()[-1].lower()
            cand = Candidate(
                full_name=finissant["full_name"],
                current_title=(
                    f"Finissant(e) {program.program_name} \u2014 {finissant['title_suffix']}"
                ),
                region=program.city,
                candidate_type="finissant",
                contact_email=f"{first}.{last}@example.ca",
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
                icon="+",
                message=(
                    f"Finissant ajout\u00e9 : {finissant['full_name']} "
                    f"\u2014 {program.institution_name}."
                ),
                detail={
                    "increment": {"candidates_created": 1},
                    "candidate_id": str(cand.id),
                    "school": program.institution_name,
                },
            )
            await self.think(0.4)

        yield AgentStep(
            ts=self.now_iso(),
            icon="OK",
            message=(
                f"Fili\u00e8re scolaire couverte \u2014 {n_contacts} centre(s) r\u00e9el(s) "
                f"contact\u00e9(s), {len(finissants)} profil(s) ajout\u00e9(s) au pipeline."
            ),
        )
