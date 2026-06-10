"""Idempotent seed of realistic sample candidates for local dev.

These are FICTIONAL records that exercise the various pipeline stages, fit-score
buckets, and Quebec recruiting regions so the Kanban UI looks alive in development.

Run from apps/api/:
    python -m scripts.seed_dev_candidates

Safe to re-run — uses email-based upsert. Deletes nothing.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Candidate
from app.models.enums import PipelineStatus

# Fictional candidates for local dev. Each row exercises a different pipeline stage
# and a different region from the Seguin Morris contact footprint.
DEV_CANDIDATES: list[dict] = [
    {
        "full_name": "Mathieu Tremblay",
        "current_title": "Frigoriste compagnon",
        "region": "Montréal",
        "candidate_type": "frigoriste",
        "contact_email": "mathieu.tremblay@example.test",
        "fit_score": 92,
        "fit_label": "Strong match",
        "fit_summary": "DEP + CCQ compagnon + halocarbures. Service commercial.",
        "pipeline_status": PipelineStatus.INTERVIEW,
        "consent_status": "obtained",
    },
    {
        "full_name": "Sophie Lavoie",
        "current_title": "Apprentie frigoriste — 3e année",
        "region": "Québec",
        "candidate_type": "frigoriste",
        "contact_email": "sophie.lavoie@example.test",
        "fit_score": 78,
        "fit_label": "Promising",
        "fit_summary": "DEP completed, CCQ apprentice. Recruiter must verify ASP 30h.",
        "pipeline_status": PipelineStatus.INTERESTED,
        "consent_status": "obtained",
    },
    {
        "full_name": "Jean-Philippe Côté",
        "current_title": "Technicien CVAC-R service",
        "region": "Longueuil",
        "candidate_type": "technician",
        "contact_email": "jp.cote@example.test",
        "fit_score": 84,
        "fit_label": "Strong match",
        "fit_summary": "SF-1 confirmed, halocarbures confirmed. Service hors construction.",
        "pipeline_status": PipelineStatus.CONTACTED,
        "consent_status": "obtained",
    },
    {
        "full_name": "Émilie Bouchard",
        "current_title": "Finissante DEP Réfrigération 5386",
        "region": "Sherbrooke",
        "candidate_type": "finissant",
        "contact_email": "emilie.bouchard@example.test",
        "fit_score": 65,
        "fit_label": "Junior",
        "fit_summary": "Finissante, prospection 90j avant fin de cohorte.",
        "pipeline_status": PipelineStatus.TO_REVIEW,
        "consent_status": "pending",
    },
    {
        "full_name": "Antoine Gauthier",
        "current_title": "DEC Technologie de la mécanique du bâtiment",
        "region": "Trois-Rivières",
        "candidate_type": "technician",
        "contact_email": "antoine.gauthier@example.test",
        "fit_score": 71,
        "fit_label": "Promising",
        "fit_summary": "DEC 221.C0 visé pour rôle mise en service / régulation.",
        "pipeline_status": PipelineStatus.NEW,
        "consent_status": "unknown",
    },
    {
        "full_name": "Karine Dubois",
        "current_title": "Frigoriste compagnon",
        "region": "Laval",
        "candidate_type": "frigoriste",
        "contact_email": "karine.dubois@example.test",
        "fit_score": 88,
        "fit_label": "Strong match",
        "fit_summary": "Compagnon CCQ, ASP 30h, expérience institutionnelle.",
        "pipeline_status": PipelineStatus.OFFER,
        "consent_status": "obtained",
    },
    {
        "full_name": "Nicolas Pelletier",
        "current_title": "Technicien froid commercial",
        "region": "Gatineau",
        "candidate_type": "technician",
        "contact_email": "nicolas.pelletier@example.test",
        "fit_score": 80,
        "fit_label": "Strong match",
        "fit_summary": "SF-2 + halocarbures. Service hors construction résidentiel/commercial léger.",
        "pipeline_status": PipelineStatus.NEW,
        "consent_status": "unknown",
    },
    {
        "full_name": "Geneviève Roy",
        "current_title": "Apprentie frigoriste — 1re année",
        "region": "Jonquière",
        "candidate_type": "frigoriste",
        "contact_email": "genevieve.roy@example.test",
        "fit_score": 58,
        "fit_label": "Junior",
        "fit_summary": "CCQ 1re période. Bonne posture, formation à compléter.",
        "pipeline_status": PipelineStatus.NEW,
        "consent_status": "unknown",
    },
    {
        "full_name": "Luc Bélanger",
        "current_title": "Frigoriste compagnon",
        "region": "Mississauga",
        "candidate_type": "frigoriste",
        "contact_email": "luc.belanger@example.test",
        "fit_score": 75,
        "fit_label": "Promising",
        "fit_summary": "Compagnon ON. Doit confirmer équivalence CCQ pour chantier QC.",
        "pipeline_status": PipelineStatus.TO_REVIEW,
        "consent_status": "pending",
    },
    {
        "full_name": "Maxime Beaulieu",
        "current_title": "Frigoriste industriel",
        "region": "Vancouver",
        "candidate_type": "frigoriste",
        "contact_email": "maxime.beaulieu@example.test",
        "fit_score": 90,
        "fit_label": "Strong match",
        "fit_summary": "Refrigeration mechanic, ammonia experience. Strong industrial profile.",
        "pipeline_status": PipelineStatus.HIRED,
        "consent_status": "obtained",
    },
    {
        "full_name": "Stéphanie Caron",
        "current_title": "Vendeuse technique CVAC-R",
        "region": "Ottawa",
        "candidate_type": "technical_sales",
        "contact_email": "stephanie.caron@example.test",
        "fit_score": 45,
        "fit_label": "Off-profile",
        "fit_summary": "Profil ventes, pas service terrain. Garder pour rôles techniques bureau.",
        "pipeline_status": PipelineStatus.ARCHIVED,
        "consent_status": "obtained",
    },
    {
        "full_name": "Sébastien Morin",
        "current_title": "Frigoriste compagnon",
        "region": "Montréal",
        "candidate_type": "frigoriste",
        "contact_email": "sebastien.morin@example.test",
        "fit_score": 72,
        "fit_label": "Promising",
        "fit_summary": "Refused offer — wanted higher base salary. Archive for future reach-out.",
        "pipeline_status": PipelineStatus.REJECTED,
        "consent_status": "obtained",
    },
]


def seed_dev_candidates(db: Session) -> int:
    added = 0
    for spec in DEV_CANDIDATES:
        existing = db.execute(
            select(Candidate).where(Candidate.contact_email == spec["contact_email"])
        ).scalar_one_or_none()
        if existing is None:
            db.add(Candidate(**spec))
            added += 1
    db.commit()
    return added


def main() -> None:
    print("Seeding sample candidates for local dev...")
    with SessionLocal() as db:
        added = seed_dev_candidates(db)
    print(f"Done. Added {added} new candidate(s) (existing rows untouched).")


if __name__ == "__main__":
    main()
