"""Apify Actor wrappers with fallback chains.

Pattern lifted from `shopify-competitor-monitor/scripts/scrape_store.py` (multi-Actor
fallback) and `agent_toolkit/scraper.py:8-17` (apify-client SDK call shape).

Each capability has an ordered list of Actor IDs. We try each in turn; the first
one that returns a non-empty dataset wins. When `MOCK_APIFY=1` is set in the
environment, all calls return canned fixtures from `mocks.py` instead of hitting
the platform — useful while iterating on the synthesizer/UI without burning
credits.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable

from apify_client import ApifyClient

from pitch_lens.briefing import Article, ProfileData, Tweet

log = logging.getLogger(__name__)

# Actor fallback chains — primary first.
LINKEDIN_ACTORS: list[tuple[str, dict]] = [
    # dev_fusion/Linkedin-Profile-Scraper — pay-per-result, profileUrls input
    ("dev_fusion~Linkedin-Profile-Scraper", {"profileUrls": []}),
    # apimaestro/linkedin-profile-detail — username input
    ("apimaestro~linkedin-profile-detail", {"usernames": []}),
    # bebity/linkedin-premium-actor — multi-input; we'll only use profile URL
    ("bebity~linkedin-premium-actor", {"action": "profile-search", "profileUrls": []}),
]

TWITTER_ACTORS: list[tuple[str, dict]] = [
    # apidojo/tweet-scraper — searchTerms accepts handle "from:user"
    ("apidojo~tweet-scraper", {"searchTerms": [], "maxItems": 20}),
    # apify/twitter-scraper-lite
    ("apify~twitter-scraper-lite", {"searchTerms": [], "maxItems": 20}),
]

SEARCH_ACTOR = "apify~google-search-scraper"
CRAWLER_ACTOR = "apify~website-content-crawler"


def _client() -> ApifyClient:
    token = os.environ.get("APIFY_API_TOKEN", "")
    if not token:
        raise RuntimeError(
            "APIFY_API_TOKEN missing. Apply coupon ALL_THINGS_AGENT at console.apify.com "
            "then paste the token from console.apify.com/settings/integrations into .env."
        )
    return ApifyClient(token)


def _is_mock() -> bool:
    return os.environ.get("MOCK_APIFY", "").lower() in {"1", "true", "yes"}


def _run(actor_id: str, run_input: dict, *, timeout_secs: int = 120) -> list[dict]:
    """Call an Actor and return the dataset items as a list of dicts.

    Mirrors the agent_toolkit pattern: client.actor(id).call(run_input=...) →
    client.dataset(run["defaultDatasetId"]).iterate_items().
    """
    client = _client()
    log.info("apify: calling %s with %s", actor_id, _short(run_input))
    run = client.actor(actor_id).call(run_input=run_input, timeout_secs=timeout_secs)
    if not run or not run.get("defaultDatasetId"):
        return []
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    log.info("apify: %s returned %d items", actor_id, len(items))
    return items


def _short(d: dict) -> str:
    s = str(d)
    return s if len(s) < 200 else s[:200] + "…"


def _try_chain(chain: Iterable[tuple[str, dict]], merge: dict) -> tuple[str, list[dict]]:
    """Try Actors in order, returning the first non-empty (actor_id, items) pair."""
    last_err: Exception | None = None
    for actor_id, base_input in chain:
        run_input = {**base_input, **merge}
        try:
            items = _run(actor_id, run_input)
            if items:
                return actor_id, items
            log.warning("apify: %s returned empty, trying next", actor_id)
        except Exception as e:
            log.warning("apify: %s failed (%s), trying next", actor_id, e)
            last_err = e
    if last_err:
        raise last_err
    return "", []


# ---------- Public capability functions ----------


def linkedin_profile(name: str, linkedin_url: str | None = None) -> ProfileData:
    """Look up a LinkedIn profile. Requires either the linkedin_url or that
    `name` is uniquely searchable (we only use the URL here for reliability).
    """
    if _is_mock():
        from pitch_lens import mocks
        return mocks.profile_for(name)

    if not linkedin_url:
        # Without a URL we'd need a search Actor first. Out of scope for v0.
        log.warning("linkedin_profile called without URL for %s — returning empty", name)
        return ProfileData(name=name)

    # Each Actor wants the URL in a different field; we inject it per chain item.
    chain = [
        ("dev_fusion~Linkedin-Profile-Scraper", {"profileUrls": [linkedin_url]}),
        ("apimaestro~linkedin-profile-detail", {"usernames": [_handle_from_url(linkedin_url)]}),
        ("bebity~linkedin-premium-actor", {"action": "profile-search", "profileUrls": [linkedin_url]}),
    ]
    actor_id, items = _try_chain(chain, merge={})
    if not items:
        return ProfileData(name=name, profile_url=linkedin_url)
    return _normalize_profile(items[0], fallback_name=name, profile_url=linkedin_url)


def recent_tweets(handle: str, max_items: int = 20) -> list[Tweet]:
    """Fetch recent tweets for `handle` (without the leading @)."""
    if _is_mock():
        from pitch_lens import mocks
        return mocks.tweets_for(handle)

    handle = handle.lstrip("@")
    chain = [
        ("apidojo~tweet-scraper", {"searchTerms": [f"from:{handle}"], "maxItems": max_items}),
        ("apify~twitter-scraper-lite", {"searchTerms": [f"from:{handle}"], "maxItems": max_items}),
    ]
    _, items = _try_chain(chain, merge={})
    return [_normalize_tweet(it) for it in items][:max_items]


def web_mentions(name: str, max_results: int = 5) -> list[Article]:
    """Search Google for the name, then crawl the top results for full article text."""
    if _is_mock():
        from pitch_lens import mocks
        return mocks.mentions_for(name)

    search_input = {"queries": f'"{name}"', "resultsPerPage": max_results, "maxPagesPerQuery": 1}
    items = _run(SEARCH_ACTOR, search_input)
    organic: list[dict] = []
    for page in items:
        organic.extend(page.get("organicResults", []))
    organic = organic[:max_results]
    if not organic:
        return []

    urls = [r.get("url") for r in organic if r.get("url")]
    crawl_input = {
        "startUrls": [{"url": u} for u in urls],
        "maxCrawlPages": len(urls),
        "crawlerType": "cheerio",
    }
    crawled = _run(CRAWLER_ACTOR, crawl_input, timeout_secs=180)
    body_by_url = {c.get("url"): (c.get("text") or "")[:4000] for c in crawled}

    return [
        Article(
            url=r["url"],
            title=r.get("title", ""),
            snippet=r.get("description", ""),
            body=body_by_url.get(r["url"], ""),
        )
        for r in organic
        if r.get("url")
    ]


# ---------- Normalizers ----------


def _normalize_profile(raw: dict, *, fallback_name: str, profile_url: str) -> ProfileData:
    """Coerce different Actors' shapes into ProfileData."""
    return ProfileData(
        name=raw.get("fullName") or raw.get("name") or fallback_name,
        headline=raw.get("headline") or raw.get("subtitle") or "",
        current_role=_first_role(raw),
        current_company=_first_company(raw),
        location=raw.get("location") or raw.get("locationName") or "",
        summary=raw.get("about") or raw.get("summary") or "",
        experience=raw.get("experience") or raw.get("positions") or [],
        profile_url=raw.get("publicIdentifier") and f"https://linkedin.com/in/{raw['publicIdentifier']}" or profile_url,
        raw=raw,
    )


def _first_role(raw: dict) -> str:
    exp = raw.get("experience") or raw.get("positions") or []
    if isinstance(exp, list) and exp:
        first = exp[0]
        return first.get("title") or first.get("position") or ""
    return raw.get("currentTitle") or raw.get("jobTitle") or ""


def _first_company(raw: dict) -> str:
    exp = raw.get("experience") or raw.get("positions") or []
    if isinstance(exp, list) and exp:
        first = exp[0]
        return first.get("companyName") or first.get("company") or ""
    return raw.get("currentCompany") or ""


def _normalize_tweet(raw: dict) -> Tweet:
    return Tweet(
        text=raw.get("text") or raw.get("fullText") or "",
        url=raw.get("url") or raw.get("twitterUrl") or "",
        created_at=str(raw.get("createdAt") or raw.get("created_at") or ""),
        likes=int(raw.get("likeCount") or raw.get("likes") or 0),
        retweets=int(raw.get("retweetCount") or raw.get("retweets") or 0),
    )


def _handle_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]
