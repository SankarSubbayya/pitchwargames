"""End-to-end orchestrator: judge name + founder's pitch → Wargame."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from pitch_lens import apify_actors, synthesizer
from pitch_lens.briefing import Wargame

log = logging.getLogger(__name__)

ProgressFn = Callable[[str, int, int], None] | None


@dataclass
class WargameInput:
    judge_name: str
    pitch_text: str
    linkedin_url: str | None = None
    twitter_handle: str | None = None


def run_full(inp: WargameInput, on_progress: ProgressFn = None) -> Wargame:
    """Scrape the judge from 3 sources, then run the adversarial simulation."""
    total = 4

    _tick(on_progress, "Looking up the judge's LinkedIn…", 1, total)
    profile = apify_actors.linkedin_profile(inp.judge_name, inp.linkedin_url)

    _tick(on_progress, "Reading recent X posts…", 2, total)
    tweets = (
        apify_actors.recent_tweets(inp.twitter_handle)
        if inp.twitter_handle
        else []
    )

    _tick(on_progress, "Searching the web for articles & mentions…", 3, total)
    mentions = apify_actors.web_mentions(inp.judge_name)

    _tick(on_progress, "Running the adversarial simulation…", 4, total)
    return synthesizer.briefing(inp.judge_name, inp.pitch_text, profile, tweets, mentions)


def _tick(fn: ProgressFn, label: str, step: int, total: int) -> None:
    log.info("[%d/%d] %s", step, total, label)
    if fn:
        fn(label, step, total)
