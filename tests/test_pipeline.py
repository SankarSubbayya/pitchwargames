"""End-to-end pipeline tests.

Unit tests use both mock flags so they never hit the network. The integration
test is gated by the `integration` marker — run with `pytest -m integration`
and real env vars set to verify the live wiring."""

import os

import pytest

from pitch_lens.briefing import Wargame
from pitch_lens.pipeline import WargameInput, run_full


class TestPipelineMocked:
    def test_full_pipeline_with_mocks_returns_valid_wargame(self, monkeypatch):
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.setenv("MOCK_LLM", "1")

        result = run_full(
            WargameInput(
                judge_name="Petros Hong",
                pitch_text="Pitch Wargames is an adversarial pitch coach.",
                linkedin_url="https://linkedin.com/in/petroshong",
                twitter_handle="petroshong",
            )
        )

        assert isinstance(result, Wargame)
        assert result.judge_name == "Petros Hong"
        assert len(result.predicted_questions) == 5
        # Killer must come first per system prompt contract
        assert result.predicted_questions[0].likelihood == "killer"

    def test_progress_callback_fires_for_each_step(self, monkeypatch):
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.setenv("MOCK_LLM", "1")

        events: list[tuple[str, int, int]] = []

        run_full(
            WargameInput(judge_name="X", pitch_text="Y"),
            on_progress=lambda label, step, total: events.append((label, step, total)),
        )

        # 4 steps: linkedin, twitter, web, synth
        assert len(events) == 4
        assert events[0][1] == 1
        assert events[-1][1] == 4
        assert all(e[2] == 4 for e in events)

    def test_pipeline_handles_no_twitter_handle(self, monkeypatch):
        """Without a twitter handle, the pipeline should still complete."""
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.setenv("MOCK_LLM", "1")

        result = run_full(
            WargameInput(
                judge_name="Petros Hong",
                pitch_text="Anything",
                linkedin_url=None,
                twitter_handle=None,
            )
        )
        assert isinstance(result, Wargame)


@pytest.mark.integration
class TestPipelineLive:
    """Hits real Apify + Anthropic. Run via `pytest -m integration`. Costs <$0.10."""

    def test_real_synthesis_with_minimal_apify_calls(self):
        """Smoke-test the live wiring: real Apify Google search + real Claude call."""
        if not os.environ.get("APIFY_API_TOKEN"):
            pytest.skip("APIFY_API_TOKEN not set")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        # Use Petros as the live target — public, low-risk profile
        result = run_full(
            WargameInput(
                judge_name="Petros Hong",
                pitch_text=(
                    "Pitch Wargames — adversarial pitch coach. Predicts 5 hardest "
                    "questions a specific judge will ask, using Apify-scraped data."
                ),
                linkedin_url="https://www.linkedin.com/in/petroshong/",
                twitter_handle=None,  # skip Twitter to keep cost down
            )
        )
        assert isinstance(result, Wargame)
        assert len(result.predicted_questions) >= 1
        assert result.judge_name == "Petros Hong"
