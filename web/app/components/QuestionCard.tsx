import { Question } from "../types";

const LIKELIHOOD_STYLES: Record<
  Question["likelihood"],
  { container: string; badge: string; label: string; rank: string }
> = {
  killer: {
    container:
      "border-rose-200 bg-rose-50 shadow-lg shadow-rose-100/80",
    badge: "border-rose-200 bg-rose-600 text-white",
    label: "Killer question",
    rank: "text-rose-700",
  },
  very_likely: {
    container: "border-amber-200 bg-amber-50",
    badge: "border-amber-200 bg-amber-500 text-white",
    label: "Very likely",
    rank: "text-amber-700",
  },
  likely: {
    container: "border-sky-200 bg-sky-50",
    badge: "border-sky-200 bg-sky-600 text-white",
    label: "Likely",
    rank: "text-sky-700",
  },
};

export function QuestionCard({ q, index }: { q: Question; index: number }) {
  const styles = LIKELIHOOD_STYLES[q.likelihood];

  return (
    <article className={`${styles.container} border p-4 md:p-6`}>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className={`font-mono text-sm font-black ${styles.rank}`}>
          Q{String(index).padStart(2, "0")}
        </div>
        <span
          className={`${styles.badge} inline-flex w-fit border px-3 py-1 text-xs font-black uppercase tracking-[0.14em]`}
        >
          {styles.label}
        </span>
      </div>

      <p className="mb-5 text-xl font-black leading-snug text-slate-950 md:text-2xl">
        &quot;{q.text}&quot;
      </p>

      <div className="mb-5 border-l-2 border-slate-300 pl-4">
        <div className="mb-1 text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
          Why they will ask
        </div>
        <p className="leading-7 text-slate-700">{q.why_they_ask}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="border border-emerald-200 bg-white p-4">
          <div className="mb-2 text-xs font-black uppercase tracking-[0.16em] text-emerald-700">
            Answer that lands
          </div>
          <p className="leading-7 text-slate-800">{q.suggested_answer}</p>
        </div>
        <div className="border border-rose-200 bg-white p-4">
          <div className="mb-2 text-xs font-black uppercase tracking-[0.16em] text-rose-700">
            Trap to avoid
          </div>
          <p className="leading-7 text-slate-800">{q.trap_to_avoid}</p>
        </div>
      </div>
    </article>
  );
}
