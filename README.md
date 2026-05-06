# 🎯 Pitch Wargames

> **Adversarial pitch coach.** Predicts the 5 hardest questions a *specific* judge / VC / interviewer will ask *your* pitch — and arms you with the answer that lands.

Built for the **All Things Agent** Apify hackathon · May 6, 2026.

---

## The 30-second pitch

Most "investor research" tools tell you what an investor likes. That's table stakes — every founder Googles before a meeting. **Pitch Wargames does the inverse:** it predicts the questions that investor will *ask you* and tells you how to answer.

Type a name + your pitch in 2-3 sentences. We compose **four Apify Actors** (LinkedIn, X, Google Search, Web Content Crawler) to pull live data on the target, then run an adversarial system prompt on **Claude Sonnet 4.6** that turns descriptive scraped data into *predictive* questions tied to your specific pitch. You walk into the room knowing the questions before they're asked.

## Why this is an Apify hackathon project

Apify's real differentiator is **Actor composition** — 28,000+ pre-built Actors for live web data. Most "AI agent" hackathon demos call one scraper. Pitch Wargames orchestrates **four diverse Actors across social, profile, search, and content**, normalizes their outputs, and feeds the merged context into an LLM for adversarial reasoning. It's a poster child for why you'd pick Apify over rolling your own Playwright.

## Live example — Karena Cai (real hackathon judge, real pipeline run)

We ran the live pipeline on judge **Karena Cai** (Caltech PhD, ex-Cruise Senior Applied Scientist, AI educator at DeepLearning.AI). The model produced (full output: [`cache/karena_cai.json`](cache/karena_cai.json)):

> **Killer question (her safety-engineering instinct):**
> *"You're scraping live data from LinkedIn, X, and the web right before a pitch — what happens when the scrape is incomplete, rate-limited, or just wrong? How do founders know they're not walking in with a hallucinated profile of me?"*
>
> **Why she'll ask it:** Karena's career at Cruise was about safety-critical evaluation — behavioral testing protocols catching 5x more regressions. She knows a confident wrong output is worse than no output.
>
> **The answer that lands:** "We show founders exactly what was scraped, source by source, before the simulation runs, so they can see gaps and override bad data. When a scrape is thin, we surface it explicitly and tighten the confidence framing rather than papering over it with false precision."
>
> **Trap to avoid:** Don't say "Claude handles it" — Karena built testing infrastructure specifically because models fail silently.

Every question is grounded in a *specific trigger* in her scraped data. That's the difference.

## Architecture

```
                         Streamlit demo (app.py) ────┐
                         judge name + pitch text     │
                                                     │ uses
                                                     ▼
       ┌───────────────────────────────────────────────────────────┐
       │  pitch_lens/ (shared Python core)                         │
       │                                                           │
       │  pipeline.run_full(WargameInput) ─► 4 Actor calls + LLM   │
       │       │                                                   │
       │       ├── linkedin_profile()   ⤷ dev_fusion (+2 fallbacks)│
       │       ├── recent_tweets()      ⤷ apidojo (+1 fallback)    │
       │       ├── web_mentions()       ⤷ apify/google-search-     │
       │       │                          scraper +                │
       │       │                          apify/website-content-   │
       │       │                          crawler                  │
       │       └── synthesizer.briefing() ⤷ Claude Sonnet 4.6      │
       │                                    (forced tool-use →     │
       │                                     structured Wargame)   │
       └───────────────────────────────────────────────────────────┘
                                                     ▲
                                                     │ called by
                          OpenClaw skill (skill/) ───┘
                          SKILL.md runbook
                          scripts/run_wargame.py
```

**Multi-Actor fallback pattern:** each capability has an ordered list of Actors. We try the first; if it errors or returns empty, we try the next. Lifted from `shopify-competitor-monitor`'s pattern, adapted for diverse sources.

**Output schema:** see [`pitch_lens/briefing.py`](pitch_lens/briefing.py). The `Wargame` Pydantic model is passed as Anthropic's `tool_use` schema for forced structured output — no parsing, no re-prompting.

## Sponsor stack

| Sponsor | What we use it for |
|---|---|
| **Apify** | 4 composed Actors for live web data: `dev_fusion/Linkedin-Profile-Scraper`, `apidojo/tweet-scraper`, `apify/google-search-scraper`, `apify/website-content-crawler`. Plus the `apify-client` Python SDK for orchestration. $100 hackathon credit (`ALL_THINGS_AGENT`) covers ~2,000 wargames. |
| **Anthropic Claude Sonnet 4.6** | Adversarial reasoning. Forced `tool_use` for structured Wargame output. ~$0.05 per wargame. |
| **OpenClaw** | Skill packaging — `skill/SKILL.md` + CLI scripts let any OpenClaw agent invoke Pitch Wargames as a composable capability. |

## Quick start

```bash
# 1. Install
uv sync

# 2. Configure .env
# Add APIFY_API_TOKEN (apply coupon ALL_THINGS_AGENT first at console.apify.com)
# Add ANTHROPIC_API_KEY

# 3. Run the Streamlit demo
uv run streamlit run app.py
# → http://localhost:8501

# 4. Run via the CLI / OpenClaw skill
uv run python skill/scripts/run_wargame.py \
  --name "Karena Cai" \
  --pitch "Your pitch in 2-3 sentences..." \
  --linkedin "https://linkedin.com/in/karena-cai-8208a336" \
  --twitter "karenaCai"
```

## Develop without burning credits

Two env flags let you iterate offline:

```bash
# Mock the Apify Actors (returns canned fixtures, no platform calls)
MOCK_APIFY=1 uv run streamlit run app.py

# Mock the LLM too (returns a hardcoded Wargame, zero API spend)
MOCK_APIFY=1 MOCK_LLM=1 uv run streamlit run app.py
```

The Streamlit "Load cached demo" expander also reads JSON files from `cache/` — handy as a wifi-outage fallback during the live demo.

## Tests

```bash
# Unit tests (no network, ~0.4s)
uv run pytest

# Integration tests (real Apify + Anthropic, ~$0.05)
uv run pytest -m integration
```

25 unit tests cover Pydantic schemas, Actor-output normalizers (multiple LinkedIn / Twitter shapes), the schema-stripper that prepares the Wargame model for Anthropic tool-use, mock-mode behavior, the missing-token error path, and end-to-end pipeline orchestration.

## File map

```
apify_may6/
├── app.py                          # Streamlit demo
├── pitch_lens/
│   ├── briefing.py                 # Wargame, Question, Source, ProfileData, Tweet, Article schemas
│   ├── apify_actors.py             # 4 Actor wrappers + fallback chains + normalizers
│   ├── synthesizer.py              # Claude Sonnet 4.6 with forced tool_use
│   ├── pipeline.py                 # run_full() orchestrator + progress callback
│   └── mocks.py                    # MOCK_APIFY / MOCK_LLM fixtures
├── skill/
│   ├── SKILL.md                    # OpenClaw skill runbook
│   ├── requirements.txt
│   └── scripts/run_wargame.py      # CLI entrypoint
├── tests/                          # 25 unit + 1 integration
├── cache/karena_cai.json           # offline demo fallback
└── pyproject.toml
```

## What we'd build next

1. **Judge corpus** — every wargame run enriches a structured profile that gets richer over time. By the 1,000th run, we know what kinds of questions a thesis-investor asks vs. a portfolio-pattern investor.
2. **Slack bot** — paste a calendar invite, get the wargame the morning of the meeting.
3. **Post-pitch debrief** — record the actual meeting, compare predicted questions to actual, learn.
4. **Accelerator distribution** — embed in YC / Techstars / a16z pre-demo-day workflows.

## Built by

[Sankar Subbayya](https://github.com/SankarSubbayya) · [sankara68@gmail.com](mailto:sankara68@gmail.com)
