"""Seed the REAL Quebec recruiting universe from the research document.

This is the first step of moving from mockup to production data:
  - 7 DEP Refrigeration 5386 centers (real public contacts + cohort dates)
  - 7 cegeps offering DEC 221.C0 + 2 targeted AECs at College Ahuntsic
  - The full sourcing-channel directory as LeadSource rows
  - Key recruiting events (MCEE, SETC, Foire de l'emploi, Olympiades)

SOURCE POLICY LAW: every LeadSource is seeded with allowed_to_scrape=False.
Flipping that flag is a deliberate human decision per source, after reviewing
its terms of service. Indeed and LinkedIn prohibit scraping outright; they are
seeded with manual_import / browser_capture access methods accordingly.

Idempotent: safe to re-run; matches on natural keys and skips existing rows.

Usage from apps/api/:
    python -m scripts.seed_real_sources
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import LeadSource, RecruitingEvent, SchoolProgram
from app.models.enums import AccessMethod, SourceType

# ---------------------------------------------------------------------------
# DEP Refrigeration 5386 — the 7 centers (primary hiring pool)
# Contacts and cohort dates are from the May 2026 research document.
# ---------------------------------------------------------------------------

DEP = "DEP R\u00e9frig\u00e9ration 5386"

SCHOOL_PROGRAMS: list[dict] = [
    {
        "institution_name": "CFP de Qu\u00e9bec",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Qu\u00e9bec",
        "province": "QC",
        "public_contact_name": "Nathalie Baron",
        "public_contact_email": "nathalie.baron@cssc.gouv.qc.ca",
        "public_contact_phone": "418-686-4674 p. 401781",
        "cohort_start": date(2026, 1, 30),
        "cohort_end": date(2027, 6, 25),
        "notes": "1 800 h. Autre cohorte ao\u00fbt 2026 visible. Canal Services aux entreprises disponible.",
    },
    {
        "institution_name": "CFP Vision 20 20",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Victoriaville",
        "province": "QC",
        "public_contact_email": "admissionfp@cssbf.gouv.qc.ca",
        "public_contact_phone": "819-751-2020",
        "cohort_start": date(2026, 8, 17),
        "cohort_end": date(2028, 1, 31),
        "notes": "1 800 h, enseignement individualis\u00e9, 32,5 h/sem. Cohorte suivante : 8 mars 2027 \u2192 30 sept. 2028.",
    },
    {
        "institution_name": "CFP 24-Juin",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Sherbrooke",
        "province": "QC",
        "public_contact_name": "Bureau d'admission",
        "public_contact_email": "BureauDesAdmissions@cssrs.gouv.qc.ca",
        "public_contact_phone": "819-822-5420 x17061",
        "cohort_start": date(2026, 8, 31),
        "cohort_end": date(2028, 6, 14),
        "notes": "Accepte explicitement stages, emplois, visites d'entreprise et conf\u00e9rences \u2014 porte d'entr\u00e9e employeur prioritaire.",
    },
    {
        "institution_name": "\u00c9cole Polym\u00e9canique de Laval",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Laval",
        "province": "QC",
        "public_contact_email": "polymecanique@csslaval.gouv.qc.ca",
        "public_contact_phone": "450-662-7000 p. 2600",
        "notes": "1 800 h, groupes jour/soir. Calendrier variable \u2014 demander les dates de fin au centre. R\u00e9pertoire d'offres d'emploi affich\u00e9.",
    },
    {
        "institution_name": "CFP Pierre-Dupuy",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Longueuil",
        "province": "QC",
        "public_contact_email": "centre_pierredupuy@csmv.qc.ca",
        "public_contact_phone": "450-468-4000 p. 2825",
        "cohort_start": date(2026, 8, 28),
        "notes": "1 800 h. Fin de cohorte non publi\u00e9e \u2014 \u00e0 confirmer localement.",
    },
    {
        "institution_name": "CFP de Lachine",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Lachine",
        "province": "QC",
        "public_contact_email": "info@cfplachine.ca",
        "public_contact_phone": "514-855-4185 poste 2",
        "notes": "Environ 16 mois, 1 800 h, horaire de jour. Formulaire officiel pour soumettre une offre d'emploi.",
    },
    {
        "institution_name": "CFP Jonqui\u00e8re",
        "program_name": DEP,
        "program_type": "DEP",
        "city": "Jonqui\u00e8re",
        "province": "QC",
        "public_contact_name": "Nadia Thibeault",
        "public_contact_email": "nadia.thibeault@cssdlj.gouv.qc.ca",
        "public_contact_phone": "418-695-5195 p. 5229",
        "cohort_start": date(2026, 11, 9),
        "cohort_end": date(2028, 6, 16),
        "notes": "1 800 h, 32,5 h/sem. RAC et concomitance visibles.",
    },
    # ---- DEC 221.C0 Technologie de la m\u00e9canique du b\u00e2timent (complementary pool)
    {
        "institution_name": "C\u00e9gep de Jonqui\u00e8re",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Jonqui\u00e8re",
        "province": "QC",
        "public_contact_email": "info@cegepjonquiere.ca",
        "public_contact_phone": "418-547-2191",
        "notes": "Rel\u00e8ve technique ; ATE publi\u00e9e.",
    },
    {
        "institution_name": "C\u00e9gep de l'Outaouais",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Gatineau",
        "province": "QC",
        "public_contact_name": "Sylvain Lapointe",
        "public_contact_email": "sylvain.lapointe@cegepoutaouais.qc.ca",
        "public_contact_phone": "819-770-4012 p. 3295",
        "notes": "Rel\u00e8ve technique ; ATE publi\u00e9e. R\u00e9gion strat\u00e9gique (bureau Gatineau).",
    },
    {
        "institution_name": "C\u00e9gep de Rimouski",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Rimouski",
        "province": "QC",
        "public_contact_email": "info@cegep-rimouski.qc.ca",
        "public_contact_phone": "418-723-1880 p. 2158",
        "notes": "Rel\u00e8ve technique ; ATE publi\u00e9e.",
    },
    {
        "institution_name": "C\u00e9gep de Saint-Hyacinthe",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Saint-Hyacinthe",
        "province": "QC",
        "public_contact_email": "info@cegepsth.qc.ca",
        "public_contact_phone": "450-773-6800 p. 2208",
        "notes": "Rel\u00e8ve technique ; ATE publi\u00e9e.",
    },
    {
        "institution_name": "C\u00e9gep de Trois-Rivi\u00e8res",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Trois-Rivi\u00e8res",
        "province": "QC",
        "public_contact_email": "info@cegeptr.qc.ca",
        "public_contact_phone": "819-376-1721",
        "notes": "Rel\u00e8ve technique.",
    },
    {
        "institution_name": "C\u00e9gep Limoilou",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Qu\u00e9bec",
        "province": "QC",
        "public_contact_email": "infolimoilou@cegeplimoilou.ca",
        "public_contact_phone": "418-647-6604",
        "notes": "Rel\u00e8ve technique ; ATE et DEC-BAC publi\u00e9s.",
    },
    {
        "institution_name": "Coll\u00e8ge Ahuntsic",
        "program_name": "DEC Technologie de la m\u00e9canique du b\u00e2timent 221.C0",
        "program_type": "DEC",
        "city": "Montr\u00e9al",
        "province": "QC",
        "public_contact_email": "information@collegeahuntsic.qc.ca",
        "public_contact_phone": "514-389-5921",
        "notes": "Rel\u00e8ve technique ; ATE publi\u00e9e.",
    },
    # ---- AEC at College Ahuntsic (requalification / upskilling pool)
    {
        "institution_name": "Coll\u00e8ge Ahuntsic",
        "program_name": "AEC Syst\u00e8mes de m\u00e9canique du b\u00e2timent",
        "program_type": "AEC",
        "city": "Montr\u00e9al",
        "province": "QC",
        "public_contact_name": "Denis Simard",
        "public_contact_email": "denis.simard@collegeahuntsic.qc.ca",
        "public_contact_phone": "514-389-5921 p. 2222",
        "notes": "Requalification / techniciens d\u00e9j\u00e0 en emploi.",
    },
    {
        "institution_name": "Coll\u00e8ge Ahuntsic",
        "program_name": "AEC Conception de base en m\u00e9canique du b\u00e2timent",
        "program_type": "AEC",
        "city": "Montr\u00e9al",
        "province": "QC",
        "public_contact_name": "Chantal Archambault",
        "public_contact_email": "chantal.archambault@collegeahuntsic.qc.ca",
        "public_contact_phone": "514-389-5921 p. 2604",
        "notes": "Estimation, dessin, support technique.",
    },
]


# ---------------------------------------------------------------------------
# Sourcing channels — the LeadSource directory with the policy law applied.
# ALL allowed_to_scrape=False. Flipping a flag is a human, per-source decision.
# ---------------------------------------------------------------------------

LEAD_SOURCES: list[dict] = [
    {
        "name": "Qu\u00e9bec emploi",
        "source_type": SourceType.GOVERNMENT,
        "url": "https://www.quebec.ca/emploi",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "Plateforme gouvernementale. Priorit\u00e9 haute : publier en fran\u00e7ais, jumelage et crit\u00e8res de s\u00e9lection. V\u00e9rifier conditions avant toute automatisation.",
    },
    {
        "name": "Guichet-Emplois Canada",
        "source_type": SourceType.GOVERNMENT,
        "url": "https://www.guichetemplois.gc.ca",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "Port\u00e9e pancanadienne, alertes, jumelage, voie recrutement international (EIMT). Offre des flux/outils employeur officiels \u2014 voie API \u00e0 \u00e9valuer.",
    },
    {
        "name": "Jobillico",
        "source_type": SourceType.JOB_BOARD,
        "url": "https://www.jobillico.com",
        "access_method": AccessMethod.MANUAL_IMPORT,
        "notes": "Priorit\u00e9 haute au Qu\u00e9bec. Variantes de titres : frigoriste, technicien en r\u00e9frig\u00e9ration, apprenti frigoriste, frigoriste CCQ. Import manuel / produits employeur seulement.",
    },
    {
        "name": "Indeed",
        "source_type": SourceType.JOB_BOARD,
        "url": "https://emplois.ca.indeed.com",
        "access_method": AccessMethod.MANUAL_IMPORT,
        "notes": "INTERDICTION ToS : pas de scraping. Acc\u00e8s CV via produits employeur payants (Indeed Resume) uniquement.",
    },
    {
        "name": "Jobboom",
        "source_type": SourceType.JOB_BOARD,
        "url": "https://www.jobboom.com",
        "access_method": AccessMethod.MANUAL_IMPORT,
        "notes": "Excellent volume Qu\u00e9bec ; apprentis, compagnons, profils institutionnels/commerciaux. Base CV = abonnement employeur.",
    },
    {
        "name": "Workopolis",
        "source_type": SourceType.JOB_BOARD,
        "url": "https://www.workopolis.com",
        "access_method": AccessMethod.MANUAL_IMPORT,
        "notes": "Priorit\u00e9 moyenne \u2014 visibilit\u00e9 de marque employeur au Qu\u00e9bec.",
    },
    {
        "name": "LinkedIn",
        "source_type": SourceType.SOCIAL,
        "url": "https://www.linkedin.com",
        "access_method": AccessMethod.BROWSER_CAPTURE,
        "notes": "INTERDICTION ToS stricte : aucun scraping. Recherche bool\u00e9enne + capture assist\u00e9e par recruteur uniquement.",
    },
    {
        "name": "Groupes Facebook du m\u00e9tier",
        "source_type": SourceType.SOCIAL,
        "url": "https://www.facebook.com",
        "access_method": AccessMethod.BROWSER_CAPTURE,
        "notes": "Canaux communautaires : publier offre courte, locale, avec fourchette salariale. Capture assist\u00e9e seulement \u2014 activit\u00e9 et mod\u00e9ration changeantes.",
    },
    {
        "name": "CCQ \u2014 Commission de la construction du Qu\u00e9bec",
        "source_type": SourceType.ASSOCIATION,
        "url": "https://www.ccq.org",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "R\u00e9f\u00e9rence r\u00e9glementaire chantier : certificats apprenti/compagnon, \u00e9tat des bassins de main-d'\u0153uvre, garantie d'emploi 150 h.",
    },
    {
        "name": "CMMTQ \u2014 Corporation des ma\u00eetres m\u00e9caniciens en tuyauterie",
        "source_type": SourceType.ASSOCIATION,
        "url": "https://www.cmmtq.org",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "R\u00e9pertoire de membres pour cartographier les employeurs, r\u00e9f\u00e9rences, diffusion cibl\u00e9e.",
    },
    {
        "name": "CETAF \u2014 Corporation des entreprises de traitement de l'air et du froid",
        "source_type": SourceType.ASSOCIATION,
        "url": "https://www.cetaf.qc.ca",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "R\u00e9seau CVAC-R d'environ 350 entreprises. Diffusion membre, Forum R\u00e9frig\u00e9ration, bourses et rel\u00e8ve comme porte d'entr\u00e9e vers les \u00e9coles.",
    },
    {
        "name": "ASP Construction",
        "source_type": SourceType.GOVERNMENT,
        "url": "https://www.asp-construction.org",
        "access_method": AccessMethod.PUBLIC_PAGE,
        "notes": "R\u00e9f\u00e9rence SST chantier \u2014 cours SSGCC 30 h obligatoire. Crit\u00e8re de pr\u00e9s\u00e9lection chantier.",
    },
]


# ---------------------------------------------------------------------------
# Recruiting events from the research document.
# ---------------------------------------------------------------------------

RECRUITING_EVENTS: list[dict] = [
    {
        "name": "Salon MCEE \u2014 M\u00e9canique, Climatisation, \u00c9lectricit\u00e9, \u00c9clairage",
        "event_type": "trade_show",
        "date_start": date(2027, 4, 14),
        "date_end": date(2027, 4, 15),
        "city": "Montr\u00e9al",
        "province": "QC",
        "country": "Canada",
        "audience": "Sp\u00e9cialistes CVAC-R, exposants, employeurs \u2014 commercial / industriel / r\u00e9frig\u00e9ration technique",
        "source_url": "https://mcee.ca",
        "recruiting_value_score": 85,
        "recommended_action": "Planifier t\u00f4t (kiosque ou visite). Priorit\u00e9 haute pour profils commercial/industriel.",
    },
    {
        "name": "SETC \u2014 Salon de l'emploi des technologies en construction",
        "event_type": "career_fair",
        "city": "Montr\u00e9al",
        "province": "QC",
        "country": "Canada",
        "audience": "Techniciens, jeunes professionnels, profils techno-b\u00e2timent \u2014 compl\u00e9ment aux bassins DEC/AEC",
        "source_url": "https://www.bimquebec.org/setc-2026-montreal",
        "recruiting_value_score": 70,
        "recommended_action": "Excellent compl\u00e9ment aux bassins DEC/AEC. V\u00e9rifier dates 2026 et r\u00e9server.",
    },
    {
        "name": "Foire de l'emploi Qu\u00e9bec",
        "event_type": "career_fair",
        "city": "Qu\u00e9bec",
        "province": "QC",
        "country": "Canada",
        "audience": "Grand public r\u00e9gional \u2014 Capitale-Nationale / Chaudi\u00e8re-Appalaches",
        "source_url": "https://foireemploi.com",
        "recruiting_value_score": 65,
        "recommended_action": "Int\u00e9ressant pour volume local dans la r\u00e9gion de Qu\u00e9bec.",
    },
    {
        "name": "Olympiades qu\u00e9b\u00e9coises des m\u00e9tiers et des technologies",
        "event_type": "competition",
        "province": "QC",
        "country": "Canada",
        "audience": "Rel\u00e8ve la plus engag\u00e9e des m\u00e9tiers \u2014 comp\u00e9titeurs en r\u00e9frig\u00e9ration",
        "source_url": "https://olympiadesmetiers.quebec",
        "recruiting_value_score": 60,
        "recommended_action": "Chercher commandite, jury, ou rep\u00e9rage des comp\u00e9titeurs en r\u00e9frig\u00e9ration.",
    },
]


# ---------------------------------------------------------------------------
# Idempotent seeding — natural-key matching, never duplicates.
# ---------------------------------------------------------------------------


def seed_school_programs(db: Session) -> None:
    for spec in SCHOOL_PROGRAMS:
        existing = db.execute(
            select(SchoolProgram).where(
                SchoolProgram.institution_name == spec["institution_name"],
                SchoolProgram.program_name == spec["program_name"],
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(SchoolProgram(**spec))
            print(f"  + program: {spec['institution_name']} \u2014 {spec['program_type']}")
        else:
            print(f"  = program: {spec['institution_name']} \u2014 {spec['program_type']} (present)")


def seed_lead_sources(db: Session) -> None:
    for spec in LEAD_SOURCES:
        existing = db.execute(
            select(LeadSource).where(LeadSource.name == spec["name"])
        ).scalar_one_or_none()
        if existing is None:
            # allowed_to_scrape intentionally NOT in the specs above:
            # it relies on the model default (False). The flag is flipped
            # per-source by a human after ToS review. Hard rule #3.
            db.add(LeadSource(**spec))
            print(f"  + source: {spec['name']} [{spec['access_method'].value}]")
        else:
            print(f"  = source: {spec['name']} (present)")


def seed_events(db: Session) -> None:
    for spec in RECRUITING_EVENTS:
        existing = db.execute(
            select(RecruitingEvent).where(RecruitingEvent.name == spec["name"])
        ).scalar_one_or_none()
        if existing is None:
            db.add(RecruitingEvent(**spec))
            print(f"  + event: {spec['name']}")
        else:
            print(f"  = event: {spec['name']} (present)")


def main() -> None:
    print("Seeding REAL Quebec recruiting universe (schools, sources, events)...")
    with SessionLocal() as db:
        print("School programs (7 DEP + 7 DEC + 2 AEC):")
        seed_school_programs(db)
        print("Lead sources (policy: allowed_to_scrape=False everywhere):")
        seed_lead_sources(db)
        print("Recruiting events:")
        seed_events(db)
        db.commit()
    print("Seed complete. Flip allowed_to_scrape per-source only after ToS review.")


if __name__ == "__main__":
    main()
