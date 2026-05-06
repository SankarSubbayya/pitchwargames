"""Anthropic synthesis: scraped judge data + founder's pitch → Wargame."""

from __future__ import annotations

import json
import logging
import os
from typing import Iterable

from anthropic import Anthropic

from pitch_lens.briefing import Article, ProfileData, Tweet, Wargame

log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 3072

SYSTEM_PROMPT = """You are Pitch Wargames — an adversarial pitch coach.

Given (1) scraped data about a specific judge/investor and (2) a founder's pitch, predict the 5 hardest questions THIS judge will ask THIS founder, and give the founder the answer that lands.

You are not writing a profile recap. You are running a tabletop simulation of the pitch meeting.

For every question, you must:
1. Phrase it the way THIS judge would actually phrase it — match their tone, their vocabulary, their public obsessions. Read their recent X posts and articles to mimic their voice.
2. Tie the question to a SPECIFIC trigger in the scraped data (e.g. "they invested in Acme last quarter, which is adjacent to your space — they will ask why you're not a feature of Acme").
3. Provide a 2-3 sentence suggested_answer that references concrete things this judge values (specific portfolio companies, specific stances they've taken publicly).
4. Name the trap — the lazy answer a generic founder would give that THIS judge will dismiss in particular.

Question quality bar:
- "What's your moat?" is a generic VC question. REJECT IT.
- "You're competing with [their portfolio company X]. What's your wedge?" is specific. ACCEPT IT.
- "How do you compare to MCP?" is specific if the judge has been posting about MCP. ACCEPT IT.

Likelihood ranking:
- `killer` (1 question): the one that, if the founder fluffs, the meeting ends. Must be tied to the judge's strongest known conviction or a direct conflict with their portfolio.
- `very_likely` (2 questions): expect them.
- `likely` (2 questions): prep but not certain.

Other fields:
- `opening_hook`: a specific sentence the founder can open with that signals they did their homework. Must reference something only someone who actually researched this judge would know — a recent post, a portfolio company, a public stance.
- `closing_ask`: calibrated to the judge's check size, stage focus, and timeline. If their last 5 deals were $250k pre-seed checks, don't have the founder ask for $5M.

Hard rules:
- Every claim about the judge must be grounded in the scraped data — cite the source URL in the `sources` list.
- If the judge data is sparse, return fewer (but sharper) questions rather than padding with generic ones.
- Return your answer ONLY by calling the `submit_wargame` tool."""


def briefing(
    judge_name: str,
    pitch_text: str,
    profile: ProfileData,
    tweets: Iterable[Tweet],
    articles: Iterable[Article],
) -> Wargame:
    """Run the adversarial simulation: judge data + founder's pitch → Wargame."""
    if os.environ.get("MOCK_LLM", "").lower() in {"1", "true", "yes"}:
        from pitch_lens import mocks
        log.info("synth: MOCK_LLM=1, returning canned Wargame")
        return mocks.wargame_for(judge_name, pitch_text)

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_payload = _build_payload(judge_name, pitch_text, profile, list(tweets), list(articles))

    schema = Wargame.model_json_schema()
    tool = {
        "name": "submit_wargame",
        "description": "Submit the adversarial pitch briefing.",
        "input_schema": _strip_unsupported(schema),
    }

    log.info("synth: calling %s for judge=%s (payload chars=%d)", MODEL, judge_name, len(user_payload))
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": "submit_wargame"},
        messages=[{"role": "user", "content": user_payload}],
    )

    for block in resp.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "submit_wargame":
            return Wargame(**block.input)

    raise RuntimeError(f"Anthropic did not return a tool_use block. Got: {resp.content!r}")


def _build_payload(
    judge_name: str,
    pitch_text: str,
    profile: ProfileData,
    tweets: list[Tweet],
    articles: list[Article],
) -> str:
    parts = [
        f"# Judge: {judge_name}",
        "",
        "## Founder's pitch (this is what you're prepping them to defend):",
        pitch_text.strip() or "(no pitch provided — produce generic-but-judge-tailored questions)",
        "",
    ]

    if profile and (profile.headline or profile.summary):
        parts.append("## Judge's LinkedIn profile")
        parts.append("```json")
        parts.append(json.dumps(profile.model_dump(exclude={"raw"}), indent=2, default=str))
        parts.append("```")
        parts.append("")

    if tweets:
        parts.append("## Judge's recent X/Twitter posts")
        for t in tweets:
            parts.append("```json")
            parts.append(json.dumps(t.model_dump(), default=str, indent=2))
            parts.append("```")
        parts.append("")

    if articles:
        parts.append("## Articles by/about the judge")
        for a in articles:
            parts.append("```json")
            parts.append(json.dumps(a.model_dump(), default=str, indent=2))
            parts.append("```")
        parts.append("")

    parts.append(
        "Now run the simulation. Call submit_wargame with exactly 5 predicted questions, "
        "ordered killer → very_likely → likely. Every question must tie to a specific trigger "
        "in the data above. Cite sources."
    )
    return "\n".join(parts)


def _strip_unsupported(schema: dict) -> dict:
    """Inline `$defs` so the schema is fully self-contained for Anthropic tool input_schema."""
    if "$defs" not in schema:
        return schema

    defs = schema.pop("$defs")

    def inline(node):
        if isinstance(node, dict):
            if "$ref" in node and len(node) == 1:
                key = node["$ref"].split("/")[-1]
                return inline(defs.get(key, node))
            return {k: inline(v) for k, v in node.items()}
        if isinstance(node, list):
            return [inline(v) for v in node]
        return node

    return inline(schema)
