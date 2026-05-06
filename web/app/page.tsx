"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { Wargame, WargameRequest } from "./types";
import { WargameResult } from "./components/WargameResult";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const SAVED_RUNS_KEY = "pitch-wargames:saved-runs";

const PROGRESS_STEPS = [
  "Profile sweep: LinkedIn and public bio signals",
  "Social scan: recent X posts and language patterns",
  "Web crawl: articles, mentions, and topical triggers",
  "Simulation: adversarial questions and answer prep",
];

const TARGET_PROFILES = [
  {
    label: "Karena Cai",
    role: "AI safety judge",
    detail: "Safety-critical AI, evals, robotics, and model reliability.",
    judgeName: "Karena Cai",
    linkedinUrl: "https://www.linkedin.com/in/karena-cai-8208a336",
    twitterHandle: "",
  },
  {
    label: "Aileen Lee",
    role: "Seed investor",
    detail:
      "Early-stage markets, category creation, defensibility, and founder-market fit.",
    judgeName: "Aileen Lee",
    linkedinUrl: "",
    twitterHandle: "",
  },
  {
    label: "Marc Andreessen",
    role: "Technical VC",
    detail: "Big markets, technical leverage, distribution, and contrarian ambition.",
    judgeName: "Marc Andreessen",
    linkedinUrl: "",
    twitterHandle: "",
  },
  {
    label: "Enterprise CIO",
    role: "Budget owner",
    detail: "Security, integration risk, procurement, ROI, and operational rollout.",
    judgeName: "CIO at a Fortune 500 retailer",
    linkedinUrl: "",
    twitterHandle: "",
  },
  {
    label: "Accelerator Partner",
    role: "Demo day judge",
    detail: "Clarity, speed, customer pull, founder insight, and why now.",
    judgeName: "Partner at a top startup accelerator",
    linkedinUrl: "",
    twitterHandle: "",
  },
  {
    label: "AI Product Lead",
    role: "Design partner",
    detail: "Workflow fit, user trust, model quality, adoption, and measurable lift.",
    judgeName: "Head of AI Products at a B2B SaaS company",
    linkedinUrl: "",
    twitterHandle: "",
  },
];

const PITCH_EXAMPLES = [
  {
    label: "Pitch Wargames",
    pitchText:
      "Pitch Wargames is an adversarial pitch coach that predicts the hardest questions a specific judge will ask, using Apify-scraped profile, social, and web data.",
  },
  {
    label: "Dev tools GTM",
    pitchText:
      "We help developer-tool startups discover high-intent buyers by monitoring public hiring, GitHub, and community signals, then ranking accounts that are ready for outbound.",
  },
  {
    label: "Support QA",
    pitchText:
      "We automate support quality audits for enterprise contact centers by reviewing every customer interaction, flagging compliance risks, and coaching agents with evidence-backed feedback.",
  },
  {
    label: "Healthcare ops",
    pitchText:
      "We help specialty clinics reduce denied insurance claims by checking every chart against payer rules before submission and routing risky claims to the right biller.",
  },
  {
    label: "Climate finance",
    pitchText:
      "We help commercial building owners find profitable energy retrofits by combining utility data, incentive programs, and contractor bids into a ranked financing plan.",
  },
  {
    label: "Recruiting agent",
    pitchText:
      "We give recruiting teams an AI sourcer that monitors role changes, open-source activity, and public writing to identify candidates who are likely to switch jobs soon.",
  },
];

type SavedRun = {
  id: string;
  judgeName: string;
  pitchText: string;
  createdAt: string;
  wargame: Wargame;
};

export default function Home() {
  const [judgeName, setJudgeName] = useState("");
  const [pitchText, setPitchText] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [twitterHandle, setTwitterHandle] = useState("");

  const [running, setRunning] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [resolveNote, setResolveNote] = useState<string | null>(null);
  const [wargame, setWargame] = useState<Wargame | null>(null);
  const [savedRuns, setSavedRuns] = useState<SavedRun[]>([]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(SAVED_RUNS_KEY);
      if (raw) setSavedRuns(JSON.parse(raw) as SavedRun[]);
    } catch {
      setSavedRuns([]);
    }
  }, []);

  function friendlyError(err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    const lower = message.toLowerCase();

    if (message.includes("Failed to fetch")) {
      return `Could not reach the FastAPI backend at ${API_BASE}. Start it with "uv run uvicorn api:app --reload --port 8000" and try again.`;
    }

    if (lower.includes("api key") || lower.includes("token")) {
      return `${message} Check APIFY_API_TOKEN and ANTHROPIC_API_KEY in .env, or run with MOCK_APIFY=1 MOCK_LLM=1 for a dry demo.`;
    }

    return message;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setWargame(null);

    if (!judgeName.trim() || !pitchText.trim()) {
      setError("Choose a target profile and a pitch, or type both manually.");
      return;
    }

    setRunning(true);
    setProgressStep(0);

    const ticker = setInterval(() => {
      setProgressStep((s) => Math.min(s + 1, PROGRESS_STEPS.length - 1));
    }, 18000);

    try {
      const req: WargameRequest = {
        judge_name: judgeName.trim(),
        pitch_text: pitchText.trim(),
        linkedin_url: linkedinUrl.trim() || undefined,
        twitter_handle: twitterHandle.trim() || undefined,
      };

      const resp = await fetch(`${API_BASE}/api/wargame`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });

      if (!resp.ok) {
        const detail = (await resp.json().catch(() => ({}))) as {
          detail?: string;
        };
        throw new Error(detail.detail || `The API returned HTTP ${resp.status}.`);
      }

      const data = (await resp.json()) as Wargame;
      setWargame(data);
      saveRun(data, judgeName.trim(), pitchText.trim());
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      clearInterval(ticker);
      setRunning(false);
    }
  }

  function loadCachedKarena() {
    setError(null);
    setRunning(false);
    setWargame(null);
    fetch("/karena_cai.json")
      .then((r) => r.json())
      .then((d) => {
        const data = d as Wargame;
        setWargame(data);
        saveRun(
          data,
          data.judge_name,
          data.pitch_summary || "Cached Karena Cai demo",
        );
      })
      .catch((e) => setError(`Could not load the cached demo: ${e.message}`));
  }

  function persistSavedRuns(runs: SavedRun[]) {
    setSavedRuns(runs);
    window.localStorage.setItem(SAVED_RUNS_KEY, JSON.stringify(runs));
  }

  function saveRun(data: Wargame, target: string, pitch: string) {
    const nextRun: SavedRun = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      judgeName: data.judge_name || target,
      pitchText: pitch,
      createdAt: new Date().toISOString(),
      wargame: data,
    };

    const deduped = savedRuns.filter(
      (run) =>
        run.judgeName !== nextRun.judgeName ||
        run.pitchText !== nextRun.pitchText,
    );
    persistSavedRuns([nextRun, ...deduped].slice(0, 8));
  }

  function loadSavedRun(run: SavedRun) {
    setError(null);
    setResolveNote(null);
    setRunning(false);
    setJudgeName(run.judgeName);
    setPitchText(run.pitchText);
    setWargame(run.wargame);
  }

  function clearSavedRuns() {
    persistSavedRuns([]);
  }

  function loadTarget(profile: (typeof TARGET_PROFILES)[number]) {
    setError(null);
    setResolveNote(null);
    setWargame(null);
    setJudgeName(profile.judgeName);
    setLinkedinUrl(profile.linkedinUrl);
    setTwitterHandle(profile.twitterHandle);
  }

  function loadPitch(example: (typeof PITCH_EXAMPLES)[number]) {
    setError(null);
    setResolveNote(null);
    setWargame(null);
    setPitchText(example.pitchText);
  }

  async function resolveHandles() {
    setError(null);
    setResolveNote(null);

    if (!judgeName.trim()) {
      setError("Choose a target profile or type a name before finding handles.");
      return;
    }

    setResolving(true);
    try {
      const resp = await fetch(`${API_BASE}/api/resolve-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ judge_name: judgeName.trim() }),
      });

      if (!resp.ok) {
        const detail = (await resp.json().catch(() => ({}))) as {
          detail?: string;
        };
        throw new Error(detail.detail || `The API returned HTTP ${resp.status}.`);
      }

      const data = (await resp.json()) as {
        linkedin_url?: string | null;
        twitter_handle?: string | null;
      };
      if (data.linkedin_url) setLinkedinUrl(data.linkedin_url);
      if (data.twitter_handle) setTwitterHandle(data.twitter_handle);

      if (data.linkedin_url || data.twitter_handle) {
        setResolveNote(
          `Found ${[
            data.linkedin_url ? "LinkedIn" : null,
            data.twitter_handle ? "X" : null,
          ]
            .filter(Boolean)
            .join(" and ")} for ${judgeName.trim()}.`,
        );
      } else {
        setResolveNote(
          `No obvious LinkedIn or X profile found for ${judgeName.trim()}; you can still run from the name.`,
        );
      }
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setResolving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="relative overflow-hidden border-b border-sky-200">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_16%_18%,rgba(14,165,233,0.20),transparent_33%),radial-gradient(circle_at_84%_12%,rgba(244,63,94,0.14),transparent_30%),linear-gradient(135deg,#f8fbff,#eef7ff_52%,#fff7f8)]" />
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-sky-300 to-transparent" />

        <div className="relative mx-auto grid w-full max-w-7xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[0.85fr_1.15fr] lg:px-8 lg:py-12">
          <header className="flex flex-col justify-between gap-8">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 border border-sky-300 bg-sky-100 px-3 py-1 text-xs font-bold uppercase tracking-[0.22em] text-sky-800">
                Live adversarial briefing
              </div>
              <h1 className="max-w-3xl text-5xl font-black leading-[0.95] tracking-normal text-slate-950 sm:text-6xl lg:text-7xl">
                Pitch Wargames
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-700">
                Pick a target profile and a pitch. The system searches public
                web signals with Apify, then predicts the hardest questions
                before the room asks them.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
              {[
                ["0", "manual profile hunting"],
                ["5", "hard questions"],
                ["1", "room-ready brief"],
              ].map(([value, label]) => (
                <div
                  key={label}
                  className="border border-slate-200 bg-white/75 p-4 shadow-sm"
                >
                  <div className="text-2xl font-black text-sky-700">
                    {value}
                  </div>
                  <div className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-500">
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </header>

          <div className="border border-slate-200 bg-white/90 p-4 shadow-2xl shadow-sky-200/50 backdrop-blur md:p-6">
            <div className="mb-5 flex flex-col gap-2 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-rose-700">
                  Simulation console
                </div>
                <p className="mt-1 text-sm text-slate-600">
                  Click one target and one pitch. LinkedIn and X are hidden
                  because they are optional, not homework.
                </p>
              </div>
              <div className="break-all text-xs text-slate-500">
                API: {API_BASE}
              </div>
            </div>

            <div className="mb-5 grid gap-5 lg:grid-cols-2">
              <PresetGroup title="Ready target profiles">
                {TARGET_PROFILES.map((profile) => (
                  <button
                    key={profile.label}
                    type="button"
                    onClick={() => loadTarget(profile)}
                    disabled={running}
                    className={`border px-3 py-2 text-left transition hover:border-sky-300 hover:bg-sky-50 disabled:cursor-not-allowed disabled:text-slate-400 ${
                      judgeName === profile.judgeName
                        ? "border-sky-400 bg-sky-50"
                        : "border-slate-200 bg-slate-50"
                    }`}
                  >
                    <span className="block text-sm font-bold text-slate-800">
                      {profile.label}
                    </span>
                    <span className="mt-1 block text-xs uppercase tracking-[0.12em] text-slate-500">
                      {profile.role}
                    </span>
                    <span className="mt-2 block text-xs leading-5 text-slate-600">
                      {profile.detail}
                    </span>
                  </button>
                ))}
              </PresetGroup>

              <PresetGroup title="Pitch examples">
                {PITCH_EXAMPLES.map((example) => (
                  <button
                    key={example.label}
                    type="button"
                    onClick={() => loadPitch(example)}
                    disabled={running}
                    className="border border-slate-200 bg-white px-3 py-2 text-left text-sm font-semibold text-slate-700 transition hover:border-sky-300 hover:bg-sky-50 disabled:cursor-not-allowed disabled:text-slate-400"
                  >
                    {example.label}
                  </button>
                ))}
              </PresetGroup>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Target" required>
                  <input
                    type="text"
                    value={judgeName}
                    onChange={(e) => setJudgeName(e.target.value)}
                    placeholder="Choose above or type a name"
                    className="war-input"
                    disabled={running}
                  />
                </Field>
                <div className="grid gap-2 sm:grid-cols-2 md:flex md:items-end">
                  <button
                    type="button"
                    onClick={resolveHandles}
                    disabled={running || resolving}
                    className="min-h-12 w-full border border-sky-300 bg-sky-50 px-4 py-3 text-sm font-bold uppercase tracking-[0.12em] text-sky-800 transition hover:border-sky-500 hover:bg-sky-100 disabled:cursor-not-allowed disabled:text-slate-400"
                  >
                    {resolving ? "Finding" : "Find handles"}
                  </button>
                  <button
                    type="button"
                    onClick={loadCachedKarena}
                    disabled={running || resolving}
                    className="min-h-12 w-full border border-slate-300 bg-white px-5 py-3 text-sm font-bold uppercase tracking-[0.14em] text-slate-700 transition hover:border-rose-300 hover:bg-rose-50 disabled:cursor-not-allowed disabled:text-slate-400"
                  >
                    Load cached demo
                  </button>
                </div>
              </div>

              <Field label="Pitch" required>
                <textarea
                  value={pitchText}
                  onChange={(e) => setPitchText(e.target.value)}
                  placeholder="Choose a pitch above or paste your own..."
                  className="war-input min-h-32 resize-y leading-7"
                  disabled={running}
                />
              </Field>

              <details className="border border-slate-200 bg-slate-50 p-4">
                <summary className="cursor-pointer text-xs font-bold uppercase tracking-[0.16em] text-slate-600">
                  Optional precision handles
                </summary>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Leave these blank during the demo. The pipeline still searches
                  the web from the target name; handles only make the scrape
                  sharper when you already have them.
                </p>
                {resolveNote && (
                  <p className="mt-2 border border-sky-200 bg-white px-3 py-2 text-sm leading-6 text-sky-800">
                    {resolveNote}
                  </p>
                )}
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <Field label="LinkedIn URL">
                    <input
                      type="url"
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                      placeholder="https://linkedin.com/in/their-handle"
                      className="war-input"
                      disabled={running}
                    />
                  </Field>
                  <Field label="X / Twitter handle">
                    <input
                      type="text"
                      value={twitterHandle}
                      onChange={(e) => setTwitterHandle(e.target.value)}
                      placeholder="without the @"
                      className="war-input"
                      disabled={running}
                    />
                  </Field>
                </div>
              </details>

              <button
                type="submit"
                disabled={running}
                className="min-h-12 w-full border border-sky-700 bg-sky-600 px-5 py-3 text-sm font-black uppercase tracking-[0.16em] text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-200 disabled:text-slate-500"
              >
                {running ? "Simulation running" : "Run simulation"}
              </button>
            </form>
          </div>
        </div>
      </section>

      <section className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {running && (
          <div className="mb-6 border border-sky-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-sky-700">
                  Pipeline activity guide
                </div>
                <p className="mt-1 text-sm text-slate-600">
                  The backend returns at completion; this tracker estimates the
                  live actor and model stages while the request runs.
                </p>
              </div>
              <div className="text-sm font-bold text-slate-700">
                Stage {progressStep + 1} / {PROGRESS_STEPS.length}
              </div>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-4">
              {PROGRESS_STEPS.map((step, i) => {
                const isActive = i === progressStep;
                const isDone = i < progressStep;
                return (
                  <div
                    key={step}
                    className={`border p-3 text-sm ${
                      isActive
                        ? "border-sky-300 bg-sky-50 text-sky-950"
                        : isDone
                          ? "border-emerald-300 bg-emerald-50 text-emerald-900"
                          : "border-slate-200 bg-slate-50 text-slate-500"
                    }`}
                  >
                    <div className="mb-2 font-mono text-xs">
                      {isDone ? "DONE" : isActive ? "LIVE" : `0${i + 1}`}
                    </div>
                    <div>{step}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 border border-rose-200 bg-rose-50 p-5">
            <div className="text-sm font-black uppercase tracking-[0.18em] text-rose-800">
              Simulation failed
            </div>
            <p className="mt-2 text-sm leading-6 text-rose-700">{error}</p>
          </div>
        )}

        {savedRuns.length > 0 && (
          <section className="mb-6 border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-xl font-black text-slate-950">
                  Saved Briefings
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Previous runs saved in this browser for instant replay.
                </p>
              </div>
              <button
                type="button"
                onClick={clearSavedRuns}
                className="w-fit border border-slate-300 bg-slate-50 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-600 transition hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
              >
                Clear
              </button>
            </div>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              {savedRuns.map((run) => (
                <button
                  key={run.id}
                  type="button"
                  onClick={() => loadSavedRun(run)}
                  className="border border-slate-200 bg-slate-50 p-3 text-left transition hover:border-sky-300 hover:bg-sky-50"
                >
                  <span className="block text-sm font-black text-slate-900">
                    {run.judgeName}
                  </span>
                  <span className="mt-1 line-clamp-2 block text-xs leading-5 text-slate-600">
                    {run.pitchText}
                  </span>
                  <span className="mt-3 block text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
                    {new Date(run.createdAt).toLocaleString()}
                  </span>
                </button>
              ))}
            </div>
          </section>
        )}

        {wargame ? (
          <WargameResult w={wargame} />
        ) : (
          <div className="grid gap-4 border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm md:grid-cols-3">
            <div>
              <span className="font-bold text-slate-950">Profile signals</span>{" "}
              come from the chosen name, not manual research.
            </div>
            <div>
              <span className="font-bold text-slate-950">
                Adversarial synthesis
              </span>{" "}
              predicts the questions that can derail the pitch.
            </div>
            <div>
              <span className="font-bold text-slate-950">Answer framing</span>{" "}
              turns each risk into a prepared response.
            </div>
          </div>
        )}

        <footer className="mt-10 border-t border-slate-200 pt-5 text-center text-xs text-slate-500">
          Built for the All Things Agent Apify hackathon - May 6, 2026 -{" "}
          <a
            href="https://github.com/SankarSubbayya/pitchwargames"
            className="text-sky-700 hover:text-sky-900"
          >
            github.com/SankarSubbayya/pitchwargames
          </a>
        </footer>
      </section>
    </main>
  );
}

function PresetGroup({
  children,
  title,
}: {
  children: ReactNode;
  title: string;
}) {
  return (
    <div>
      <div className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
        {title}
      </div>
      <div className="grid gap-2 sm:grid-cols-2">{children}</div>
    </div>
  );
}

function Field({
  children,
  label,
  required = false,
}: {
  children: ReactNode;
  label: string;
  required?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-slate-600">
        {label}
        {required && <span className="text-rose-600"> *</span>}
      </span>
      {children}
    </label>
  );
}
