"""Smoke tests for Phase 1 health endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "seguin-morris-recruiting"
    assert body["version"] == "0.1.0"
    assert body["environment"] in {"development", "staging", "production"}


def test_health_ready_returns_payload() -> None:
    """Readiness should always respond, even if the DB is down (status reflects that)."""
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert "checks" in body
    assert "database" in body["checks"]


def test_auth_login_is_placeholder() -> None:
    """Phase 1 contract: auth endpoints exist but return 501 until Phase 2."""
    response = client.post("/api/auth/login")
    assert response.status_code == 501
