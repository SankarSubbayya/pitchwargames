"""Tests for apify_actors normalizers and mock mode."""

import pytest

from pitch_lens import apify_actors
from pitch_lens.briefing import Article, ProfileData, Tweet


class TestNormalizers:
    def test_normalize_profile_dev_fusion_shape(self):
        """dev_fusion/Linkedin-Profile-Scraper returns headline + experience list."""
        raw = {
            "fullName": "Petros Hong",
            "headline": "Developer Community Manager at Apify",
            "location": "San Francisco Bay Area",
            "about": "Building dev community.",
            "experience": [
                {"title": "Developer Community Manager", "companyName": "Apify"},
                {"title": "Past Role", "companyName": "PrevCo"},
            ],
        }
        p = apify_actors._normalize_profile(raw, fallback_name="Petros", profile_url="https://linkedin.com/in/petroshong")
        assert p.name == "Petros Hong"
        assert p.current_role == "Developer Community Manager"
        assert p.current_company == "Apify"
        assert p.summary == "Building dev community."
        assert p.profile_url == "https://linkedin.com/in/petroshong"

    def test_normalize_profile_apimaestro_shape(self):
        """apimaestro/linkedin-profile-detail uses 'positions' instead of 'experience'."""
        raw = {
            "name": "Jane Doe",
            "subtitle": "VP Product",
            "positions": [{"position": "VP Product", "company": "Acme"}],
        }
        p = apify_actors._normalize_profile(raw, fallback_name="Jane", profile_url="https://linkedin.com/in/janedoe")
        assert p.name == "Jane Doe"
        assert p.headline == "VP Product"
        assert p.current_role == "VP Product"
        assert p.current_company == "Acme"

    def test_normalize_profile_falls_back_to_input_name(self):
        p = apify_actors._normalize_profile({}, fallback_name="Unknown", profile_url="https://linkedin.com/in/unknown")
        assert p.name == "Unknown"

    def test_normalize_tweet_apidojo_shape(self):
        raw = {
            "text": "MCP is composable.",
            "url": "https://x.com/abc/status/1",
            "createdAt": "2026-04-30",
            "likeCount": 120,
            "retweetCount": 24,
        }
        t = apify_actors._normalize_tweet(raw)
        assert t.text == "MCP is composable."
        assert t.likes == 120
        assert t.retweets == 24

    def test_normalize_tweet_alt_field_names(self):
        """Some Twitter actors use snake_case / fullText."""
        raw = {"fullText": "alt format", "twitterUrl": "https://x.com/x/2", "likes": "5"}
        t = apify_actors._normalize_tweet(raw)
        assert t.text == "alt format"
        assert t.url == "https://x.com/x/2"
        assert t.likes == 5  # coerced from string

    def test_handle_from_url(self):
        assert apify_actors._handle_from_url("https://linkedin.com/in/petroshong") == "petroshong"
        assert apify_actors._handle_from_url("https://linkedin.com/in/petroshong/") == "petroshong"


class TestMockMode:
    def test_linkedin_profile_uses_mocks_when_flag_set(self, monkeypatch):
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
        p = apify_actors.linkedin_profile("Whoever")
        assert isinstance(p, ProfileData)
        assert p.current_company == "Apify"

    def test_recent_tweets_uses_mocks_when_flag_set(self, monkeypatch):
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
        tweets = apify_actors.recent_tweets("petroshong")
        assert len(tweets) >= 1
        assert isinstance(tweets[0], Tweet)

    def test_web_mentions_uses_mocks_when_flag_set(self, monkeypatch):
        monkeypatch.setenv("MOCK_APIFY", "1")
        monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
        mentions = apify_actors.web_mentions("Petros Hong")
        assert len(mentions) >= 1
        assert isinstance(mentions[0], Article)


class TestRealModeRequiresToken:
    def test_no_token_raises_clear_error(self, monkeypatch):
        monkeypatch.delenv("MOCK_APIFY", raising=False)
        monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
        with pytest.raises(RuntimeError, match="APIFY_API_TOKEN missing"):
            apify_actors.linkedin_profile("Anyone", "https://linkedin.com/in/anyone")
