// TypeScript mirror of pitch_lens/briefing.py (Wargame, Question, Source).
// Keep in sync when the Pydantic schema changes.

export type Likelihood = "killer" | "very_likely" | "likely";
export type Relevance = "high" | "medium" | "low";

export type Source = {
  url: string;
  title: string;
  relevance: Relevance;
};

export type Question = {
  text: string;
  why_they_ask: string;
  suggested_answer: string;
  trap_to_avoid: string;
  likelihood: Likelihood;
};

export type Wargame = {
  judge_name: string;
  judge_one_liner: string;
  pitch_summary: string;
  predicted_questions: Question[];
  opening_hook: string;
  closing_ask: string;
  sources: Source[];
};

export type WargameRequest = {
  judge_name: string;
  pitch_text: string;
  linkedin_url?: string;
  twitter_handle?: string;
};
