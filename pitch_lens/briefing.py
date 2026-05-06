"""Schemas for Pitch Wargames — adversarial pitch prep.

Given scraped data about a judge/investor + the founder's pitch, we predict the
questions the judge will ask and arm the founder with answers that land. The
output is a `Wargame` (not a profile recap)."""

from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    url: str
    title: str
    relevance: Literal["high", "medium", "low"] = "medium"


class Question(BaseModel):
    """One predicted question + the playbook for answering it."""

    text: str = Field(description="The exact question, phrased the way THIS judge would ask it (their tone, their vocabulary)")
    why_they_ask: str = Field(description="One sentence: what about THIS judge's background or recent posts makes this question likely")
    suggested_answer: str = Field(description="A 2-3 sentence response calibrated to what this judge values. Reference specifics from their portfolio/posts when possible.")
    trap_to_avoid: str = Field(description="The wrong-answer trap — the response a generic founder would give that this specific judge would dismiss")
    likelihood: Literal["killer", "very_likely", "likely"] = Field(
        description="`killer` = if you don't nail this you lose the room. `very_likely` = expect it. `likely` = prep but not certain."
    )


class Wargame(BaseModel):
    """The full adversarial briefing for one judge × one pitch."""

    judge_name: str
    judge_one_liner: str = Field(description="One sentence: who they are and what they fund/care about, grounded in scraped data")
    pitch_summary: str = Field(description="Echo back the founder's pitch in one sentence so they can see the model understood it")
    predicted_questions: list[Question] = Field(
        description="Exactly 5 questions, ordered by likelihood (killer first). Must be specific to BOTH this judge AND this pitch — not generic VC questions."
    )
    opening_hook: str = Field(description="One specific sentence the founder should open with that signals they did their homework on THIS judge")
    closing_ask: str = Field(description="The exact ask to make at the end of the pitch, calibrated to this judge's check size and stage focus")
    sources: list[Source] = Field(default_factory=list)


# ---------- Internal scrape result types (unchanged) ----------


class ProfileData(BaseModel):
    name: str = ""
    headline: str = ""
    current_role: str = ""
    current_company: str = ""
    location: str = ""
    summary: str = ""
    experience: list[dict] = Field(default_factory=list)
    profile_url: str = ""
    raw: dict = Field(default_factory=dict)


class Tweet(BaseModel):
    text: str = ""
    url: str = ""
    created_at: str = ""
    likes: int = 0
    retweets: int = 0


class Article(BaseModel):
    url: str
    title: str = ""
    snippet: str = ""
    body: str = ""
