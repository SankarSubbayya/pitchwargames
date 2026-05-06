import { Question } from "../types";

const LIKELIHOOD_STYLES: Record<
  Question["likelihood"],
  { container: string; badge: string; badgeText: string; label: string }
> = {
  killer: {
    container:
      "bg-gradient-to-br from-red-50 to-rose-100 border-2 border-red-500 shadow-lg shadow-red-100",
    badge: "bg-red-600",
    badgeText: "text-white",
    label: "🔴 KILLER QUESTION",
  },
  very_likely: {
    container: "bg-orange-50 border-l-[6px] border-orange-500",
    badge: "bg-orange-500",
    badgeText: "text-white",
    label: "🟠 VERY LIKELY",
  },
  likely: {
    container: "bg-yellow-50 border-l-[6px] border-yellow-500",
    badge: "bg-yellow-400",
    badgeText: "text-yellow-900",
    label: "🟡 LIKELY",
  },
};

export function QuestionCard({ q, index }: { q: Question; index: number }) {
  const styles = LIKELIHOOD_STYLES[q.likelihood];

  return (
    <article className={`${styles.container} rounded-xl p-6 my-4`}>
      <div className="flex items-baseline gap-3 mb-3">
        <span
          className={`${styles.badge} ${styles.badgeText} text-xs font-bold tracking-wider uppercase px-3 py-1 rounded-full`}
        >
          Q{index} · {styles.label}
        </span>
      </div>

      <p className="text-xl font-semibold text-slate-900 leading-snug mb-4">
        “{q.text}”
      </p>

      <div className="mb-5">
        <div className="text-[0.7rem] font-bold tracking-wider uppercase text-slate-500 mb-1">
          Why they'll ask
        </div>
        <p className="italic text-slate-700 leading-relaxed">{q.why_they_ask}</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-emerald-50 border-l-4 border-emerald-700 rounded-md p-4">
          <div className="text-[0.7rem] font-bold tracking-wider uppercase text-emerald-800 mb-2">
            ✅ The answer that lands
          </div>
          <p className="text-slate-800 leading-relaxed">{q.suggested_answer}</p>
        </div>
        <div className="bg-orange-50 border-l-4 border-orange-700 rounded-md p-4">
          <div className="text-[0.7rem] font-bold tracking-wider uppercase text-orange-800 mb-2">
            ⚠️ Trap to avoid
          </div>
          <p className="text-slate-800 leading-relaxed">{q.trap_to_avoid}</p>
        </div>
      </div>
    </article>
  );
}
