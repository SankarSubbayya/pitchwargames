"use client";

import { FormEvent, useState } from "react";
import { Wargame, WargameRequest } from "./types";
import { WargameResult } from "./components/WargameResult";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const PROGRESS_STEPS = [
  "Looking up the judge's LinkedIn…",
  "Reading recent X posts…",
  "Searching the web for articles & mentions…",
  "Running the adversarial simulation…",
];

export default function Home() {
  const [judgeName, setJudgeName] = useState("");
  const [pitchText, setPitchText] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [twitterHandle, setTwitterHandle] = useState("");

  const [running, setRunning] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [wargame, setWargame] = useState<Wargame | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setWargame(null);

    if (!judgeName.trim() || !pitchText.trim()) {
      setError("Judge name and pitch text are both required.");
      return;
    }

    setRunning(true);
    setProgressStep(0);

    // Optimistic progress ticker — the backend doesn't stream, so we tick through
    // the steps on a timer. Tuned to match the typical 60-90s pipeline runtime.
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
        const detail = await resp.json().catch(() => ({}));
        throw new Error(detail.detail || `API returned ${resp.status}`);
      }
      const data = (await resp.json()) as Wargame;
      setWargame(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      clearInterval(ticker);
      setRunning(false);
    }
  }

  function loadCachedKarena() {
    setError(null);
    setRunning(false);
    fetch("/karena_cai.json")
      .then((r) => r.json())
      .then((d) => setWargame(d as Wargame))
      .catch((e) => setError(`Couldn't load cache: ${e.message}`));
  }

  return (
    <main className="flex-1 max-w-5xl mx-auto w-full px-4 md:px-6 py-8 md:py-12">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          🎯 Pitch <span className="text-indigo-600">Wargames</span>
        </h1>
        <p className="mt-3 text-lg text-slate-700 max-w-3xl leading-relaxed">
          <strong>Adversarial pitch coach.</strong> Name the investor, judge, or buyer
          you're meeting — we predict the 5 hardest questions they'll ask, tied to{" "}
          <em>their</em> portfolio and <em>their</em> recent posts, and arm you with
          the answer that lands.
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Powered by 4 composed Apify Actors (LinkedIn · X · Google Search · Web Crawler) + Claude
          Sonnet 4.6. Built for the All Things Agent Apify hackathon.
        </p>
      </header>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8 mb-6"
      >
        <div className="grid md:grid-cols-2 gap-5">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1">
                Person you're pitching to <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={judgeName}
                onChange={(e) => setJudgeName(e.target.value)}
                placeholder="e.g. Karena Cai (judge), Marc Andreessen (VC)"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={running}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1">
                LinkedIn URL <span className="text-slate-400 text-xs">(optional but recommended)</span>
              </label>
              <input
                type="url"
                value={linkedinUrl}
                onChange={(e) => setLinkedinUrl(e.target.value)}
                placeholder="https://linkedin.com/in/their-handle"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={running}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-800 mb-1">
                X / Twitter handle <span className="text-slate-400 text-xs">(optional)</span>
              </label>
              <input
                type="text"
                value={twitterHandle}
                onChange={(e) => setTwitterHandle(e.target.value)}
                placeholder="without the @"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={running}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-800 mb-1">
              Your pitch in 2-3 sentences <span className="text-red-500">*</span>
            </label>
            <textarea
              value={pitchText}
              onChange={(e) => setPitchText(e.target.value)}
              placeholder="(Paste your pitch here. Example: 'We help X solve Y by doing Z.')"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 h-44 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              disabled={running}
            />
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              The model conditions every predicted question on YOUR pitch. Specific pitches → specific questions.
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-col md:flex-row gap-3">
          <button
            type="submit"
            disabled={running}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg shadow transition"
          >
            {running ? "🎯 Running the simulation…" : "🎯 Run the simulation"}
          </button>
          <button
            type="button"
            onClick={loadCachedKarena}
            disabled={running}
            className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-3 px-6 rounded-lg border border-slate-300 transition"
          >
            📦 Load cached: Karena Cai
          </button>
        </div>
      </form>

      {/* Progress */}
      {running && (
        <div className="bg-white rounded-xl border border-indigo-200 p-5 mb-6 shadow-sm">
          <div className="text-sm font-semibold text-slate-800 mb-3">
            Step {progressStep + 1} of {PROGRESS_STEPS.length}
          </div>
          <div className="space-y-2">
            {PROGRESS_STEPS.map((step, i) => {
              const isActive = i === progressStep;
              const isDone = i < progressStep;
              return (
                <div key={i} className="flex items-center gap-3">
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                      isDone
                        ? "bg-emerald-500 text-white"
                        : isActive
                          ? "bg-indigo-600 text-white animate-pulse"
                          : "bg-slate-200 text-slate-400"
                    }`}
                  >
                    {isDone ? "✓" : i + 1}
                  </div>
                  <span
                    className={`text-sm ${
                      isActive
                        ? "text-indigo-700 font-semibold"
                        : isDone
                          ? "text-slate-500 line-through"
                          : "text-slate-400"
                    }`}
                  >
                    {step}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-300 rounded-xl p-4 mb-6">
          <div className="font-semibold text-red-800">Simulation failed</div>
          <div className="text-sm text-red-700 mt-1">{error}</div>
          <div className="text-xs text-red-600 mt-2">
            Make sure the FastAPI backend is running at <code>{API_BASE}</code> (see README).
          </div>
        </div>
      )}

      {/* Result */}
      {wargame && <WargameResult w={wargame} />}

      {/* Footer */}
      <footer className="mt-16 pt-6 border-t border-slate-200 text-xs text-slate-500 text-center">
        Built for the <strong>All Things Agent</strong> Apify hackathon · May 6, 2026 ·{" "}
        <a
          href="https://github.com/SankarSubbayya/pitchwargames"
          className="text-indigo-600 hover:underline"
        >
          github.com/SankarSubbayya/pitchwargames
        </a>
      </footer>
    </main>
  );
}
