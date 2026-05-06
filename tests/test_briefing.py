"""Schema tests for the Wargame output type."""

import pytest
from pydantic import ValidationError

from pitch_lens.briefing import Article, ProfileData, Question, Source, Tweet, Wargame


def _valid_question(**overrides) -> dict:
    data = {
        "text": "How is this different from MCP?",
        "why_they_ask": "They built MCP last quarter.",
        "suggested_answer": "We're complementary; MCP gives tools, we give a tactical objective.",
        "trap_to_avoid": "Don't position as MCP-replacement.",
        "likelihood": "killer",
    }
    data.update(overrides)
    return data


def _valid_wargame(**overrides) -> dict:
    data = {
        "judge_name": "Petros",
        "judge_one_liner": "Apify DevRel; obsessed with MCP.",
        "pitch_summary": "Adversarial pitch coach.",
        "predicted_questions": [_valid_question() for _ in range(5)],
        "opening_hook": "Your post on MCP composition...",
        "closing_ask": "15 minutes after the hackathon.",
        "sources": [],
    }
    data.update(overrides)
    return data


class TestWargameSchema:
    def test_valid_wargame_constructs(self):
        w = Wargame(**_valid_wargame())
        assert w.judge_name == "Petros"
        assert len(w.predicted_questions) == 5
        assert w.predicted_questions[0].likelihood == "killer"

    def test_likelihood_must_be_valid_literal(self):
        with pytest.raises(ValidationError):
            Question(**_valid_question(likelihood="maybe"))

    def test_question_requires_all_playbook_fields(self):
        with pytest.raises(ValidationError):
            Question(text="Q?", why_they_ask="...", suggested_answer="...")  # missing trap, likelihood

    def test_wargame_round_trips_through_json(self):
        w = Wargame(**_valid_wargame())
        revived = Wargame.model_validate_json(w.model_dump_json())
        assert revived == w

    def test_sources_default_empty(self):
        w = Wargame(**_valid_wargame())
        assert w.sources == []

    def test_source_relevance_defaults_to_medium(self):
        s = Source(url="https://x.com/abc", title="Tweet")
        assert s.relevance == "medium"


class TestSupportingSchemas:
    def test_profile_data_has_safe_defaults(self):
        p = ProfileData()
        assert p.name == ""
        assert p.experience == []

    def test_tweet_likes_coerce_int(self):
        t = Tweet(likes=42)
        assert t.likes == 42

    def test_article_requires_url(self):
        with pytest.raises(ValidationError):
            Article(title="No URL")
