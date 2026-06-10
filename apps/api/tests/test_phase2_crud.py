"""End-to-end CRUD smoke tests for Phase 2 — campaigns, candidates, sources.

These run against the live Railway dev Postgres via the app's normal config.
Each test cleans up its own data so they're safe to re-run.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------- Campaigns ----------


def test_campaign_crud_roundtrip() -> None:
    # Create
    payload = {
        "title": f"Test Campaign {uuid.uuid4().hex[:8]}",
        "division": "Mechanical Construction",
        "role_type": "Frigoriste",
        "region": "Montréal",
        "employment_type": "full_time",
        "requirements": {"min_qualifications": ["DEP", "SF1"]},
    }
    create = client.post("/api/campaigns", json=payload)
    assert create.status_code == 201, create.text
    body = create.json()
    cid = body["id"]
    assert body["title"] == payload["title"]
    assert body["status"] == "draft"

    # Read
    read = client.get(f"/api/campaigns/{cid}")
    assert read.status_code == 200
    assert read.json()["title"] == payload["title"]

    # Update
    upd = client.patch(f"/api/campaigns/{cid}", json={"status": "active"})
    assert upd.status_code == 200
    assert upd.json()["status"] == "active"

    # List should include it
    lst = client.get("/api/campaigns?limit=200")
    assert lst.status_code == 200
    assert any(c["id"] == cid for c in lst.json())

    # Delete
    delete = client.delete(f"/api/campaigns/{cid}")
    assert delete.status_code == 204

    # Confirm gone
    gone = client.get(f"/api/campaigns/{cid}")
    assert gone.status_code == 404


# ---------- Candidates ----------


def test_candidate_requires_identifier() -> None:
    """Spec rule: at least one of name/email/url required to create a candidate."""
    response = client.post("/api/candidates", json={"candidate_type": "frigoriste"})
    assert response.status_code == 422


def test_candidate_crud_roundtrip() -> None:
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "full_name": f"Test Frigoriste {suffix}",
        "contact_email": f"test+{suffix}@example.com",
        "region": "Québec",
        "candidate_type": "frigoriste",
    }
    create = client.post("/api/candidates", json=payload)
    assert create.status_code == 201, create.text
    cid = create.json()["id"]
    assert create.json()["pipeline_status"] == "new"

    # Patch into 'contacted' stage
    upd = client.patch(f"/api/candidates/{cid}", json={"pipeline_status": "contacted"})
    assert upd.status_code == 200
    assert upd.json()["pipeline_status"] == "contacted"

    # Filter list by pipeline_status
    lst = client.get("/api/candidates?pipeline_status=contacted&limit=200")
    assert lst.status_code == 200
    assert any(c["id"] == cid for c in lst.json())

    # Cleanup
    assert client.delete(f"/api/candidates/{cid}").status_code == 204


# ---------- Sources ----------


def test_source_crud_roundtrip_and_scrape_flag_defaults_false() -> None:
    """Sources default to allowed_to_scrape=False per spec hard rule."""
    payload = {
        "name": f"Test Job Board {uuid.uuid4().hex[:8]}",
        "source_type": "job_board",
        "url": "https://example.com/jobs",
        "access_method": "public_page",
        # Deliberately omitting allowed_to_scrape — must default to False
    }
    create = client.post("/api/sources", json=payload)
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    assert create.json()["allowed_to_scrape"] is False, "Spec rule: defaults to False"

    # Filter by allowed_to_scrape
    safe = client.get("/api/sources?allowed_to_scrape=false&limit=200")
    assert safe.status_code == 200
    assert any(s["id"] == sid for s in safe.json())

    # Enable scraping, then verify
    upd = client.patch(f"/api/sources/{sid}", json={"allowed_to_scrape": True})
    assert upd.status_code == 200
    assert upd.json()["allowed_to_scrape"] is True

    # Cleanup
    assert client.delete(f"/api/sources/{sid}").status_code == 204


# ---------- 404 paths ----------


@pytest.mark.parametrize("resource", ["campaigns", "candidates", "sources"])
def test_get_unknown_id_returns_404(resource: str) -> None:
    fake_id = uuid.uuid4()
    response = client.get(f"/api/{resource}/{fake_id}")
    assert response.status_code == 404
