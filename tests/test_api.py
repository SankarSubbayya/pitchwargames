"""Tests for the FastAPI wrapper used by the Next.js frontend.

Unit tests use FastAPI's TestClient + monkeypatched run_full so they don't
hit Apify or Anthropic. The integration test (gated) does a real round trip."""

import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from pitch_lens.briefing import Question, Source, Wargame


def _fake_wargame() -> Wargame:
    return Wargame(
        judge_name="Test Judge",
        judge_one_liner="A judge.",
        pitch_summary="A pitch.",
        opening_hook="Hi.",
        closing_ask="Bye.",
        predicted_questions=[
            Question(
                text=f"Q{i}",
                why_they_ask="Reason.",
                suggested_answer="Answer.",
                trap_to_avoid="Trap.",
                likelihood="killer" if i == 1 else ("very_likely" if i <= 3 else "likely"),
            )
            for i in range(1, 6)
        ],
        sources=[Source(url="https://example.com", title="Example", relevance="high")],
    )


@pytest.fixture
def client(monkeypatch):
    """Build a TestClient with run_full monkeypatched to return a fixture."""
    fake = MagicMock(return_value=_fake_wargame())
    # Patch the symbol on the module that api.py imports from.
    monkeypatch.setattr("api.run_full", fake)

    from api import app  # imported after monkeypatch so the fake is in place
    return TestClient(app), fake


class TestHealth:
    def test_health_endpoint_returns_ok(self, client):
        c, _ = client
        resp = c.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True, "service": "pitch-wargames-api"}


class TestWargameEndpoint:
    def test_returns_full_wargame_for_valid_request(self, client):
        c, fake = client
        resp = c.post(
            "/api/wargame",
            json={
                "judge_name": "Karena Cai",
                "pitch_text": "We help X solve Y by doing Z.",
                "linkedin_url": "https://linkedin.com/in/karena-cai-8208a336",
                "twitter_handle": "karenaCai",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["judge_name"] == "Test Judge"
        assert len(body["predicted_questions"]) == 5
        assert body["predicted_questions"][0]["likelihood"] == "killer"

        # Verify the WargameInput we built was clean (trimmed, optionals preserved)
        called_with = fake.call_args[0][0]
        assert called_with.judge_name == "Karena Cai"
        assert called_with.pitch_text == "We help X solve Y by doing Z."
        assert called_with.linkedin_url == "https://linkedin.com/in/karena-cai-8208a336"
        assert called_with.twitter_handle == "karenaCai"

    def test_strips_whitespace_from_inputs(self, client):
        c, fake = client
        resp = c.post(
            "/api/wargame",
            json={"judge_name": "  Karena  ", "pitch_text": "  pitch  "},
        )
        assert resp.status_code == 200
        called_with = fake.call_args[0][0]
        assert called_with.judge_name == "Karena"
        assert called_with.pitch_text == "pitch"

    def test_blank_optional_fields_become_none(self, client):
        c, fake = client
        resp = c.post(
            "/api/wargame",
            json={
                "judge_name": "X",
                "pitch_text": "Y",
                "linkedin_url": "",
                "twitter_handle": "   ",
            },
        )
        assert resp.status_code == 200
        called_with = fake.call_args[0][0]
        assert called_with.linkedin_url is None
        assert called_with.twitter_handle is None

    def test_rejects_empty_judge_name(self, client):
        c, _ = client
        resp = c.post("/api/wargame", json={"judge_name": "", "pitch_text": "Y"})
        assert resp.status_code == 422  # FastAPI Pydantic validation error

    def test_rejects_empty_pitch_text(self, client):
        c, _ = client
        resp = c.post("/api/wargame", json={"judge_name": "X", "pitch_text": ""})
        assert resp.status_code == 422

    def test_pipeline_exception_returns_500_with_detail(self, client, monkeypatch):
        c, _ = client
        # Override the fake to raise
        from api import app  # noqa: F401
        monkeypatch.setattr("api.run_full", MagicMock(side_effect=RuntimeError("boom")))

        # Need a fresh client to pick up the new patched fn
        from api import app as fresh_app
        fresh = TestClient(fresh_app)
        resp = fresh.post("/api/wargame", json={"judge_name": "X", "pitch_text": "Y"})
        assert resp.status_code == 500
        assert "boom" in resp.json()["detail"]


class TestCORS:
    def test_localhost_3000_origin_allowed(self, client):
        c, _ = client
        resp = c.options(
            "/api/wargame",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        # Preflight should pass
        assert resp.status_code in (200, 204)
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.integration
class TestApiLiveSmoke:
    """One real round-trip through the API → real Apify + Anthropic. ~$0.05."""

    def test_real_wargame_via_api(self):
        if not os.environ.get("APIFY_API_TOKEN"):
            pytest.skip("APIFY_API_TOKEN not set")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        # Reload api module so its run_full reference is the real one (in case
        # an earlier test in the same session monkeypatched it).
        import importlib
        import api as api_module
        importlib.reload(api_module)

        c = TestClient(api_module.app)
        resp = c.post(
            "/api/wargame",
            json={
                "judge_name": "Karena Cai",
                "pitch_text": (
                    "Pitch Wargames — adversarial pitch coach. Predicts the 5 hardest "
                    "questions a specific judge will ask, using Apify-scraped data."
                ),
                "linkedin_url": "https://www.linkedin.com/in/karena-cai-8208a336",
                # Skip twitter to keep the cost down
            },
            timeout=180,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["judge_name"] == "Karena Cai"
        assert len(body["predicted_questions"]) >= 1
