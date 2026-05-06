"""Canned fixtures used when MOCK_APIFY=1 / MOCK_LLM=1.

Lets us iterate on the synthesizer + UI without burning Apify credits or waiting
for slow Actor cold-starts. The fixture target is Petros Hong (Apify DevRel),
chosen because he's the obvious live-demo subject for the hackathon."""

from pitch_lens.briefing import Article, ProfileData, Question, Source, Tweet, Wargame


def profile_for(name: str) -> ProfileData:
    return ProfileData(
        name=name or "Petros Hong",
        headline="Developer Community Manager at Apify",
        current_role="Developer Community Manager",
        current_company="Apify",
        location="San Francisco Bay Area",
        summary=(
            "Building developer community at Apify, the largest marketplace of web "
            "scraping and automation tools for AI agents. Previously at companies "
            "growing developer ecosystems through hackathons, technical content, "
            "and open-source contributions."
        ),
        experience=[
            {"title": "Developer Community Manager", "companyName": "Apify"},
        ],
        profile_url="https://linkedin.com/in/petroshong",
        raw={},
    )


def tweets_for(handle: str) -> list[Tweet]:
    return [
        Tweet(
            text="MCP is the fastest path to giving any agent live web data. Apify's MCP server now exposes 28k+ Actors.",
            url="https://x.com/example/status/1",
            created_at="2026-04-30",
            likes=120,
            retweets=24,
        ),
        Tweet(
            text="Hot take: most 'AI agents' are one-tool wrappers. Real agents compose multiple tools to make decisions.",
            url="https://x.com/example/status/2",
            created_at="2026-04-22",
            likes=89,
            retweets=12,
        ),
        Tweet(
            text="Hackathon hot tip: pick an obvious problem, ship in 4 hours, polish for 1. Don't invent a new vertical at 2pm.",
            url="https://x.com/example/status/3",
            created_at="2026-04-18",
            likes=210,
            retweets=43,
        ),
    ]


def wargame_for(judge_name: str, pitch_text: str) -> Wargame:
    """Hardcoded Wargame for UI preview when MOCK_LLM=1. Tuned to look realistic
    when the judge is Petros (Apify DevRel) and the pitch is Pitch Wargames."""
    name = judge_name or "Petros Hong"
    return Wargame(
        judge_name=name,
        judge_one_liner=(
            f"{name} runs developer community at Apify; obsessed with MCP, "
            "agent skill composition, and shipping fast at hackathons."
        ),
        pitch_summary=(
            (pitch_text[:140] + "…") if len(pitch_text) > 140
            else (pitch_text or "Pitch Wargames — adversarial pitch coach predicting investor questions from Apify-scraped data.")
        ),
        opening_hook=(
            f"\"{name}, your post last week about composing multiple Actors "
            "rather than one-tool wrappers — that's literally the architecture "
            "of what I'm about to show you. We compose four.\""
        ),
        closing_ask=(
            "Ask for 15 minutes after the hackathon to walk through the "
            "OpenClaw skill version and a co-marketing post on the Apify blog "
            "— that's the right size of ask for a DevRel-led intro, not capital."
        ),
        predicted_questions=[
            Question(
                text=(
                    "How is this different from just running the Apify MCP server "
                    "and asking Claude to do the research itself? You're charging "
                    "for orchestration that mcpc already does for free."
                ),
                why_they_ask=(
                    "Petros literally launched mcpc and has been posting about how "
                    "MCP collapses bespoke integration layers. He'll see your "
                    "synthesizer as a thin wrapper unless you defend its added value."
                ),
                suggested_answer=(
                    "MCP gives the agent tools; Pitch Wargames gives the agent a "
                    "*tactical objective*. The synthesis layer isn't tool-routing — "
                    "it's an adversarial system prompt that turns descriptive data "
                    "into predictive questions tied to a specific pitch. That's a "
                    "task-shaped prompt, not a tool. It's complementary to mcpc, "
                    "not competing — we'd happily run on top of it."
                ),
                trap_to_avoid=(
                    "DON'T say 'we're easier to use than MCP.' Petros built MCP. "
                    "Frame it as a layer ON TOP of MCP, not a replacement."
                ),
                likelihood="killer",
            ),
            Question(
                text=(
                    "Four Actors is fine for a demo, but how do you keep the cost "
                    "per query under a dollar at scale? The LinkedIn Actor alone "
                    "is $5 per profile."
                ),
                why_they_ask=(
                    "He posts about Apify pricing constantly and writes monetization "
                    "guides. He'll test whether you've actually thought about unit "
                    "economics or just bolted things together."
                ),
                suggested_answer=(
                    "We tier the scrape: free Google + cached LinkedIn snippets for "
                    "the freemium plan, full LinkedIn Actor only on the $19 'pre-"
                    "meeting' plan. We also cache aggressively — most users prep "
                    "for the same 50 VCs. At 80% cache hit, marginal cost drops to "
                    "$0.30 per query."
                ),
                trap_to_avoid=(
                    "DON'T hand-wave with 'we'll scale costs later.' He'll lose "
                    "interest. Have specific numbers."
                ),
                likelihood="very_likely",
            ),
            Question(
                text=(
                    "Can you actually predict what *I* will ask before this meeting "
                    "started? Run it on me right now. I'll wait."
                ),
                why_they_ask=(
                    "He runs hackathons. He knows demos work better with a real-"
                    "time stunt. He WILL test the product live if it's plausibly "
                    "ready."
                ),
                suggested_answer=(
                    "Pull up the wargame report you ran on him this morning. Show "
                    "him the question he just asked, on screen, with a screenshot "
                    "timestamp. That's the close."
                ),
                trap_to_avoid=(
                    "DON'T say 'we'd need to scrape you first.' If you can't "
                    "demo on him live, you've lost the bit."
                ),
                likelihood="very_likely",
            ),
            Question(
                text=(
                    "Why an OpenClaw skill instead of just publishing as another "
                    "Apify Actor? You'd reach more users in our store."
                ),
                why_they_ask=(
                    "DevRel concern: he's measured on Actor-store growth and may "
                    "view a non-Actor agent product as off-strategy."
                ),
                suggested_answer=(
                    "Both, eventually. The OpenClaw skill is the agent-native "
                    "interface; we'll mirror it as a paid Apify Actor for users "
                    "who'd rather paste a name into the Apify console. The skill "
                    "drives our distribution to agent builders; the Actor drives "
                    "discovery in the Apify Store. Same engine."
                ),
                trap_to_avoid=(
                    "DON'T say 'OpenClaw is the future.' That implies Actors are "
                    "the past. Position both as channels."
                ),
                likelihood="likely",
            ),
            Question(
                text=(
                    "What stops an investor from just pasting a LinkedIn URL into "
                    "Claude themselves? Why is this a product?"
                ),
                why_they_ask=(
                    "Standard 'GPT wrapper' objection. He'll ask it because it's "
                    "the cheap-shot question that filters serious teams from demos."
                ),
                suggested_answer=(
                    "Three things Claude alone can't do: (1) live web data via "
                    "composed Actors that update post-knowledge-cutoff, (2) the "
                    "adversarial system prompt that turns descriptive scraping "
                    "into predictive questions — that's months of prompt iteration "
                    "and eval data, and (3) the integration surface — slack bot "
                    "before meetings, calendar scan, post-call follow-ups. The "
                    "wrapper IS the product."
                ),
                trap_to_avoid=(
                    "DON'T say 'we have a better prompt.' Everyone says that. "
                    "Lead with the live data composition and the workflow surface."
                ),
                likelihood="likely",
            ),
        ],
        sources=[
            Source(url="https://blog.apify.com/introducing-mcpc", title="Introducing mcpc — universal MCP CLI", relevance="high"),
            Source(url="https://docs.apify.com/platform/integrations/openclaw", title="Apify OpenClaw integration", relevance="high"),
            Source(url="https://x.com/example/status/1", title="Tweet on MCP composition (Apr 30)", relevance="medium"),
            Source(url="https://x.com/example/status/3", title="Hackathon hot tip tweet (Apr 18)", relevance="medium"),
        ],
    )


def mentions_for(name: str) -> list[Article]:
    return [
        Article(
            url="https://blog.apify.com/introducing-mcpc",
            title="Introducing mcpc — universal MCP CLI client",
            snippet="A lightweight MCP client that loads tool definitions on-demand for token efficiency.",
            body=(
                f"In this post, {name} introduces mcpc, a universal MCP CLI client built "
                "to solve context bloat when agents have access to thousands of tools. "
                "Rather than loading every tool definition into the prompt, mcpc loads "
                "them on-demand based on the agent's intent. Especially useful when "
                "connecting to Apify's MCP server with 28,000+ Actors."
            ),
        ),
        Article(
            url="https://docs.apify.com/platform/integrations/openclaw",
            title="Apify OpenClaw integration — workshop",
            snippet="Build composable agent skills that chain Apify Actors together.",
            body=(
                "OpenClaw skills let agents learn pre-built workflows. Pair them with "
                "Apify Actors and one skill's output feeds the next — turning data "
                "extraction into a reusable agent capability."
            ),
        ),
    ]
