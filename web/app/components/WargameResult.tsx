import { Wargame } from "../types";
import { QuestionCard } from "./QuestionCard";

const RELEVANCE_DOT: Record<string, string> = {
  high: "🟢",
  medium: "🟡",
  low: "🔴",
};

export function WargameResult({ w }: { w: Wargame }) {
  return (
    <section className="space-y-6">
      {/* Judge hero */}
      <div className="bg-gradient-to-br from-indigo-900 to-purple-900 text-white rounded-xl p-6 md:p-8 shadow-xl">
        <div className="text-xs font-bold tracking-widest uppercase opacity-70 mb-2">
          ⚔️ Pitching to
        </div>
        <h2 className="text-3xl md:text-4xl font-bold mb-3">{w.judge_name}</h2>
        <p className="text-lg leading-relaxed opacity-95">{w.judge_one_liner}</p>
      </div>

      {/* Pitch echo */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="text-[0.7rem] font-bold tracking-widest uppercase text-slate-500 mb-2">
          📝 Your pitch (as the model understood it)
        </div>
        <p className="text-slate-700 leading-relaxed">{w.pitch_summary}</p>
      </div>

      {/* Hook + Ask side-by-side */}
      <div className="grid md:grid-cols-2 gap-5">
        <div className="bg-blue-50 border-2 border-blue-500 rounded-xl p-5">
          <div className="text-[0.7rem] font-bold tracking-widest uppercase text-blue-700 mb-2">
            🎤 Open with this
          </div>
          <p className="text-slate-800 leading-relaxed">{w.opening_hook}</p>
        </div>
        <div className="bg-purple-50 border-2 border-purple-500 rounded-xl p-5">
          <div className="text-[0.7rem] font-bold tracking-widest uppercase text-purple-700 mb-2">
            💰 Close with this ask
          </div>
          <p className="text-slate-800 leading-relaxed">{w.closing_ask}</p>
        </div>
      </div>

      {/* Predicted questions */}
      <div>
        <h3 className="text-2xl font-bold text-slate-900 mt-8 mb-1">🔥 Predicted questions</h3>
        <p className="text-sm text-slate-600 mb-4">
          {w.predicted_questions.length} questions, ordered by likelihood. Every prediction is
          grounded in a specific trigger from the scraped data.
        </p>
        {w.predicted_questions.map((q, i) => (
          <QuestionCard key={i} q={q} index={i + 1} />
        ))}
      </div>

      {/* Sources */}
      {w.sources.length > 0 && (
        <div>
          <h3 className="text-2xl font-bold text-slate-900 mt-8 mb-1">📚 Sources used</h3>
          <p className="text-sm text-slate-600 mb-4">Every claim above is grounded in one of these.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {w.sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-white border border-slate-200 rounded-lg p-3 hover:border-indigo-400 hover:shadow-md transition"
              >
                <div className="text-2xl">{RELEVANCE_DOT[s.relevance] ?? "⚪"}</div>
                <div className="font-semibold text-sm text-slate-900 mt-2 line-clamp-2">
                  {s.title || s.url}
                </div>
                <div className="text-xs text-slate-500 mt-1">{s.relevance} relevance</div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Raw JSON */}
      <details className="bg-slate-100 rounded-lg p-4 mt-8">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">
          🔧 Raw JSON (developers only)
        </summary>
        <pre className="mt-3 text-xs overflow-x-auto bg-slate-900 text-slate-100 p-4 rounded">
          {JSON.stringify(w, null, 2)}
        </pre>
      </details>
    </section>
  );
}
