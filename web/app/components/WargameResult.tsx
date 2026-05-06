import { Wargame } from "../types";
import { QuestionCard } from "./QuestionCard";

const RELEVANCE_STYLES: Record<string, string> = {
  high: "border-emerald-200 bg-emerald-50 text-emerald-900",
  medium: "border-amber-200 bg-amber-50 text-amber-900",
  low: "border-slate-200 bg-slate-50 text-slate-700",
};

export function WargameResult({ w }: { w: Wargame }) {
  const killerCount = w.predicted_questions.filter(
    (q) => q.likelihood === "killer",
  ).length;
  const highSources = w.sources.filter((source) => source.relevance === "high");

  return (
    <section className="space-y-6">
      <div className="border border-slate-200 bg-white shadow-xl shadow-sky-100/80">
        <div className="grid lg:grid-cols-[1.05fr_0.95fr]">
          <div className="border-b border-slate-200 p-5 md:p-7 lg:border-b-0 lg:border-r">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-rose-700">
              Judge dossier
            </div>
            <h2 className="mt-3 text-4xl font-black leading-tight text-slate-950 md:text-5xl">
              {w.judge_name}
            </h2>
            <p className="mt-4 text-lg leading-8 text-slate-700">
              {w.judge_one_liner}
            </p>
          </div>
          <div className="grid grid-cols-3 divide-x divide-slate-200">
            <Metric value={w.predicted_questions.length} label="questions" />
            <Metric value={killerCount || 1} label="room-killer" />
            <Metric value={highSources.length} label="high sources" />
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700">
            Model readback
          </div>
          <p className="mt-3 leading-7 text-slate-700">{w.pitch_summary}</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <BriefingPanel title="Opening move" body={w.opening_hook} />
          <BriefingPanel title="Closing ask" body={w.closing_ask} />
        </div>
      </div>

      <div className="flex flex-col gap-2 border-b border-slate-200 pb-4 pt-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h3 className="text-3xl font-black tracking-normal text-slate-950">
            Predicted Questions
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            Ordered by likelihood and grounded in scraped target signals.
          </p>
        </div>
        <div className="text-sm font-bold uppercase tracking-[0.16em] text-sky-700">
          answer these before they ask
        </div>
      </div>

      <div className="space-y-4">
        {w.predicted_questions.map((q, i) => (
          <QuestionCard key={i} q={q} index={i + 1} />
        ))}
      </div>

      {highSources.length > 0 && (
        <div className="border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h3 className="text-2xl font-black text-slate-950">Sources Used</h3>
              <p className="mt-1 text-sm text-slate-600">
                High-relevance links used for the target dossier and question triggers.
              </p>
            </div>
            <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
              high confidence only
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {highSources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`block border p-3 transition hover:border-sky-300 hover:bg-sky-50 ${
                  RELEVANCE_STYLES[s.relevance] ?? RELEVANCE_STYLES.medium
                }`}
              >
                <div className="mb-2 font-mono text-xs uppercase">
                  {String(s.relevance).padEnd(6, " ")} source {i + 1}
                </div>
                <div className="line-clamp-2 text-sm font-bold">
                  {s.title || s.url}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      <details className="border border-slate-200 bg-white p-4 shadow-sm">
        <summary className="cursor-pointer text-sm font-bold uppercase tracking-[0.16em] text-slate-600">
          Raw JSON
        </summary>
        <pre className="mt-3 max-h-[32rem] overflow-auto border border-slate-200 bg-slate-950 p-4 text-xs leading-5 text-slate-100">
          {JSON.stringify(w, null, 2)}
        </pre>
      </details>
    </section>
  );
}

function Metric({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex min-h-36 flex-col justify-center p-4 text-center">
      <div className="text-4xl font-black text-sky-700">{value}</div>
      <div className="mt-2 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </div>
    </div>
  );
}

function BriefingPanel({ title, body }: { title: string; body: string }) {
  return (
    <div className="border border-sky-200 bg-sky-50 p-5">
      <div className="text-xs font-bold uppercase tracking-[0.18em] text-sky-700">
        {title}
      </div>
      <p className="mt-3 leading-7 text-slate-800">{body}</p>
    </div>
  );
}
