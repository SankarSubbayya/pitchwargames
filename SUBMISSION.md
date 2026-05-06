# Pitch Wargames — Apify Hackathon Submission Packet

Ready-to-paste answers for the [Apify submission Typeform](https://apify.typeform.com/to/JQSTyqBF). Open this side-by-side with the form and copy each section.

---

## 1. Project name

```
Pitch Wargames
```

## 2. One-liner / tagline

```
Adversarial pitch coach — predicts the 5 hardest questions a specific judge will ask your specific pitch, using 4 composed Apify Actors and Claude Sonnet 4.6.
```

## 3. Team members

```
Sankar Subbayya — sankara68@gmail.com — solo
```

## 4. Project description (long form)

```
Most "investor research" tools tell you what a VC likes. That's table stakes — every founder Googles before a meeting. Pitch Wargames does the inverse: it predicts the questions the investor will ASK YOU and arms you with the answer that lands.

Type a target's name + your pitch in 2-3 sentences. We compose four Apify Actors — LinkedIn profile, X recent posts, Google Search, and Website Content Crawler — to pull live data on the person, normalize the heterogeneous outputs into a single context payload, then run an adversarial system prompt on Claude Sonnet 4.6 with forced tool-use to produce a structured Wargame: 5 predicted questions (ranked killer / very_likely / likely), each with the question phrased in the judge's voice, why they'll ask it (tied to a specific trigger in the scraped data), the suggested answer calibrated to their values and portfolio, and the trap to avoid — the lazy answer this specific judge will dismiss.

We validated this live during the hackathon by running the full pipeline on a real judge — Karena Cai, Caltech PhD and ex-Cruise Senior Applied Scientist now at DeepLearning.AI. The model produced a killer question — "what happens when your scrape is wrong? how do founders know they're not walking in with a hallucinated profile of me?" — that was directly grounded in her safety-critical AV testing background. Every question cited specific public sources.

We ship Pitch Wargames in two surfaces: a Streamlit web app for live demos and an OpenClaw skill (SKILL.md + CLI wrappers) so any agent on the Apify ecosystem can invoke it as a composable capability. Same Python engine, two distribution paths.
```

## 5. What problem does it solve / who's it for

```
Founders walk into pitch meetings under-prepared. They Google the investor, skim LinkedIn, maybe read one of their tweets. None of that tells them which question will end the meeting on slide 4.

Primary users: founders pitching VCs, especially in pre-seed / seed where every meeting is high-leverage. Secondary: hackathon contestants pitching judges (today!), salespeople pitching enterprise buyers, candidates interviewing at companies where the interviewer's preferences shape the loop.

Buyer: accelerators (YC, Techstars) running pre-demo-day workflows. They have 100-200 founders per batch, every batch is fresh, and the cohort organizer has budget + incentive to improve outcomes.
```

## 6. Tech stack

```
- Apify Platform (4 composed Actors via apify-client Python SDK)
  - dev_fusion/Linkedin-Profile-Scraper (with fallbacks: apimaestro, bebity)
  - apidojo/tweet-scraper (with fallback: apify/twitter-scraper-lite)
  - apify/google-search-scraper
  - apify/website-content-crawler
- Anthropic Claude Sonnet 4.6 with forced tool_use for structured output
- Pydantic 2 for the Wargame / Question / Source schemas
- Streamlit for the demo UI
- OpenClaw skill packaging (SKILL.md runbook + Python CLI scripts)
- Python 3.12 + uv for dependency management
- pytest with custom integration marker (25 unit tests, 1 gated live test)
```

## 7. ⭐ How did you use Apify? (sponsor-specific)

```
Apify is the core data layer of Pitch Wargames. We use four diverse Actors composed into a single pipeline — this is the Apify story we wanted to demonstrate: the value isn't ANY single Actor, it's that 28,000+ Actors across every conceivable source can be composed.

Specifically:

1. dev_fusion/Linkedin-Profile-Scraper for the target's professional background, with apimaestro/linkedin-profile-detail and bebity/linkedin-premium-actor as runtime fallbacks if the primary errors or returns empty (pattern lifted from the shopify-competitor-monitor reference design).

2. apidojo/tweet-scraper to pull the target's last ~20 X/Twitter posts. Their recent obsessions are the strongest signal for question prediction.

3. apify/google-search-scraper for canonical web mentions — articles, podcast appearances, blog posts they've written or been quoted in.

4. apify/website-content-crawler to get the full body text of the top 5 search results — without this, we have headlines and snippets, not the substance Claude needs to predict adversarial questions.

The merged, normalized context (typically ~8,000-15,000 characters) then feeds Claude Sonnet 4.6 via forced tool_use with a Pydantic-derived JSON schema. We get structured Wargames back deterministically — no JSON repair, no retries.

We also use the $100 hackathon credit (ALL_THINGS_AGENT coupon) which covers ~2,000 full wargame runs at our current cost profile (~$0.05 of Apify usage per run).

The OpenClaw skill packaging is the second Apify integration — by shipping Pitch Wargames as a SKILL.md + CLI runbook, any OpenClaw agent on the platform can invoke it as a composable capability via Apify's promoted Agent Skills pattern.
```

## 8. GitHub repo URL

```
https://github.com/SankarSubbayya/pitchwargames
```
*Note: create the repo and push before submitting. From the project root: `gh repo create pitchwargames --public --source=. --push`*

## 9. Demo video URL (Loom recommended)

```
[record a 90-second demo and paste URL here]
```

**Demo video script (90 seconds):**

> 0:00 — *(camera on you)* "How many of you, in the last 24 hours, looked up someone you were about to pitch — and gave up after three LinkedIn tabs?"
>
> 0:08 — *(screen share Streamlit)* "This is Pitch Wargames. I'm going to type a real hackathon judge — Karena Cai. Then my pitch."
>
> 0:18 — *(click Run)* "Behind the scenes, four Apify Actors are running in parallel — LinkedIn profile, X recent posts, Google search, website content crawler. Twelve seconds later..."
>
> 0:35 — *(briefing renders)* "Five predicted questions. Look at the killer one — *what happens when your scrape is wrong?* That's directly tied to Karena's three years at Cruise building safety-critical AV testing. Click to reveal..."
>
> 0:55 — *(expand killer Q)* "...the answer that lands. Cited from her actual public profile. Plus the trap to avoid."
>
> 1:10 — "Same engine ships as an OpenClaw skill — any agent on the Apify ecosystem can invoke it. Built today on Apify and Claude. Demo's live."
>
> 1:25 — *(end card)* "github.com/SankarSubbayya/pitchwargames — try it on me."

## 10. Live demo URL

```
http://localhost:8501 (running locally during judging)
```
*Optional stretch: deploy to Streamlit Community Cloud — `streamlit deploy` from the GitHub repo.*

## 11. What would you build next

```
1. Judge corpus — every wargame run enriches a structured investor profile that compounds. By the 1,000th run we'll have a network-effect dataset of "what do thesis-driven Series A leads ask vs portfolio-pattern Series B leads."
2. Slack bot — paste a Calendly invite, get the wargame in your DMs the morning of.
3. Post-pitch debrief — record the actual meeting (with consent), compare predicted to actual questions, learn.
4. Accelerator distribution — embed in YC / Techstars pre-demo-day prep workflows. Cohort customer, not individual founder.
5. Apify Store listing — publish the underlying engine as a paid Apify Actor for users who'd rather paste a name into Apify Console than install an OpenClaw skill.
```

## 12. Contact email

```
sankara68@gmail.com
```

## 13. Permission to publicize

```
Yes — please tag @SankarSubbayya on LinkedIn / X if you share. I'll do the same.
```

---

## Pre-submission checklist

- [ ] Apply `ALL_THINGS_AGENT` coupon at console.apify.com → Billing
- [ ] Push code to GitHub: `gh repo create pitchwargames --public --source=. --push`
- [ ] Record 90s Loom demo (script above)
- [ ] Run `uv run pytest` one more time — all green
- [ ] One final live wargame on a real judge (Karena, Petros, Saurav) to confirm pipeline is healthy
- [ ] Submit at https://apify.typeform.com/to/JQSTyqBF before 4:00pm
- [ ] Tag `@apify` on LinkedIn / X with screenshot
