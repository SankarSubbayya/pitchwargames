"""Tests for the synthesizer — schema stripping and mock mode."""

import os

import pytest

from pitch_lens import synthesizer
from pitch_lens.briefing import ProfileData, Wargame


class TestStripUnsupported:
    def test_inlines_defs_into_main_schema(self):
        """Pydantic emits $defs for nested models like Question. Anthropic's tool
        input_schema works without them, so we inline. Verify nothing breaks
        and the defs key is gone."""
        schema = Wargame.model_json_schema()
        assert "$defs" in schema, "precondition: pydantic emits $defs"

        stripped = synthesizer._strip_unsupported(schema)

        assert "$defs" not in stripped
        questions = stripped["properties"]["predicted_questions"]
        # After inlining, items must have full nested schema, not just a $ref
        assert "items" in questions
        assert "$ref" not in questions["items"]
        assert "properties" in questions["items"]
        # Question's `text` field should be reachable through the inlined schema
        assert "text" in questions["items"]["properties"]

    def test_passthrough_when_no_defs(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        assert synthesizer._strip_unsupported(schema) == schema


class TestMockLLM:
    def test_mock_mode_returns_wargame_without_anthropic_call(self, monkeypatch):
        monkeypatch.setenv("MOCK_LLM", "1")
        # Strip the API key to prove no network call happens
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        result = synthesizer.briefing(
            judge_name="Test Judge",
            pitch_text="A test pitch",
            profile=ProfileData(name="Test Judge"),
            tweets=[],
            articles=[],
        )

        assert isinstance(result, Wargame)
        assert result.judge_name == "Test Judge"
        assert len(result.predicted_questions) == 5
        # Mock should reflect the user's pitch in the summary
        assert "test pitch" in result.pitch_summary.lower() or "adversarial" in result.pitch_summary.lower()
