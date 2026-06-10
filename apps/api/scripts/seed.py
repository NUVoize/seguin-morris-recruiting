"""Idempotent seed of baseline data — default roles + brand settings.

Run this once after `alembic upgrade head`. Safe to re-run: uses upsert-style
checks so existing rows aren't duplicated.

Usage from apps/api/:
    python -m scripts.seed
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import BrandSettings, Role

# Default RBAC roles. Permissions are deliberately broad strokes for Phase 2;
# Phase 3+ will refine into per-resource policies.
DEFAULT_ROLES: list[dict] = [
    {
        "name": "admin",
        "permissions": {
            "can_manage_users": True,
            "can_manage_roles": True,
            "can_manage_settings": True,
            "can_manage_campaigns": True,
            "can_manage_candidates": True,
            "can_manage_sources": True,
            "can_send_outreach": True,
            "can_view_audit_logs": True,
            "can_run_agents": True,
        },
    },
    {
        "name": "recruiter",
        "permissions": {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_settings": False,
            "can_manage_campaigns": True,
            "can_manage_candidates": True,
            "can_manage_sources": True,
            "can_send_outreach": True,
            "can_view_audit_logs": False,
            "can_run_agents": True,
        },
    },
    {
        "name": "viewer",
        "permissions": {
            "can_manage_users": False,
            "can_manage_roles": False,
            "can_manage_settings": False,
            "can_manage_campaigns": False,
            "can_manage_candidates": False,
            "can_manage_sources": False,
            "can_send_outreach": False,
            "can_view_audit_logs": False,
            "can_run_agents": False,
        },
    },
]


# Temporary brand placeholders per spec §13. Replace primary/secondary/accent
# once the Seguin Morris brand book is finalized.
DEFAULT_BRAND = {
    "company_name": "Seguin Morris",
    "primary_color": "#1F2937",
    "secondary_color": "#0F766E",
    "accent_color": "#F97316",
    "designed_by_label": "Designed by CTRL Solutions",
}


def seed_roles(db: Session) -> None:
    for spec in DEFAULT_ROLES:
        existing = db.execute(select(Role).where(Role.name == spec["name"])).scalar_one_or_none()
        if existing is None:
            db.add(Role(name=spec["name"], permissions=spec["permissions"]))
            print(f"  + role: {spec['name']}")
        else:
            print(f"  = role: {spec['name']} (already present)")


def seed_brand(db: Session) -> None:
    existing = db.execute(select(BrandSettings).limit(1)).scalar_one_or_none()
    if existing is None:
        db.add(BrandSettings(**DEFAULT_BRAND))
        print(f"  + brand_settings: {DEFAULT_BRAND['company_name']}")
    else:
        print(f"  = brand_settings: already present ({existing.company_name})")


def main() -> None:
    print("Seeding baseline data into Railway Postgres...")
    with SessionLocal() as db:
        print("Roles:")
        seed_roles(db)
        print("Brand settings:")
        seed_brand(db)
        db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    main()
