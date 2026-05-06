---
name: pitch-wargames
description: Adversarial pitch coach. Given the name of a person you're about to pitch (investor, hackathon judge, sales buyer, interviewer) and your pitch in 2-3 sentences, predicts the 5 hardest questions THIS person will ask THIS pitch and provides the answer that lands plus the trap to avoid. Composes Apify Actors (LinkedIn profile, X/Twitter posts, Google Search, website content crawler) for live data and Claude Sonnet 4.6 for adversarial reasoning. Use when the user says "prep me for my pitch", "predict their questions", "investor pitch coach", "interview prep", "what will they ask me", "research a judge / VC / investor / interviewer", or names a specific person they're about to meet for a high-stakes conversation.
version: 0.1.0
metadata:
  openclaw:
    requires:
      env:
        - APIFY_API_TOKEN
        - ANTHROPIC_API_KEY
      bins:
        - python3
      primaryEnv: APIFY_API_TOKEN
    emoji: "🎯"
---

# Pitch Wargames

Predict the questions a specific person will ask in a specific pitch — and arm the user with the answer that lands. Built with Apify (live web data) and Claude (adversarial reasoning).

## When to use

Trigger when the user is about to pitch, interview with, or sell to a specific named person and wants to prepare. Examples:
- "I'm pitching Marc Andreessen on Tuesday — prep me"
- "What will Petros Hong ask about my hackathon project?"
- "Help me prep for my interview with Stripe's CTO"
- "Run the wargames for this investor"

Do NOT trigger for generic "give me good pitch advice" requests — this skill needs a specific named target.

## Setup

Ensure dependencies are installed:

```bash
pip install -r {baseDir}/requirements.txt
```

Required env vars:
- `APIFY_API_TOKEN` — from console.apify.com/settings/integrations
- `ANTHROPIC_API_KEY` — from console.anthropic.com/settings/keys

## Workflow

### Step 1: Gather inputs

Ask the user for:
1. The full name of the person they're pitching (required)
2. Their pitch in 2-3 sentences (required)
3. The person's LinkedIn URL (optional but strongly improves quality — strongly recommend the user paste it)
4. The person's X/Twitter handle (optional)

If only the name is provided and quality matters, suggest the user grab the LinkedIn URL by Googling `"<name>" linkedin` and pasting the first result.

### Step 2: Run the wargame

Run the orchestrator script with the gathered inputs:

```bash
python3 {baseDir}/scripts/run_wargame.py \
  --name "<NAME>" \
  --pitch "<PITCH_TEXT>" \
  --linkedin "<LINKEDIN_URL or empty>" \
  --twitter "<HANDLE or empty>"
```

This will:
1. Scrape the person's LinkedIn profile (if URL provided) via the dev_fusion LinkedIn Actor
2. Pull their last ~20 X/Twitter posts (if handle provided) via the apidojo tweet-scraper
3. Search Google for articles about / by them via apify/google-search-scraper
4. Crawl the top 5 articles for full text via apify/website-content-crawler
5. Pass everything to Claude Sonnet 4.6 with an adversarial system prompt
6. Return a JSON `Wargame` object with 5 predicted questions, each with:
   - `text` — the question, in their voice
   - `why_they_ask` — the specific trigger in the data
   - `suggested_answer` — the response calibrated to their values
   - `trap_to_avoid` — the lazy answer they'll dismiss
   - `likelihood` — `killer`, `very_likely`, or `likely`

The script prints the JSON to stdout. Pretty-print it for the user, leading with the `killer` question.

### Step 3: Present to the user

Render the result as a markdown briefing with these sections:
1. The opening hook (one specific sentence to open the pitch with)
2. The 5 predicted questions, ordered killer → very_likely → likely. For each: question → answer → trap.
3. The closing ask
4. Sources

Highlight the killer question prominently — it's the one that, if fluffed, ends the meeting.

### Step 4: Offer follow-ups

After presenting, offer:
- "Want me to drill you on the killer question? I'll role-play the judge."
- "Want me to refine any answer?"
- "Run wargames against another judge?"
