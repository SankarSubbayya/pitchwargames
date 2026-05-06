"""Pitch Wargames — Streamlit demo.

Adversarial pitch coach. Given a judge's name and your pitch, predicts the 5
hardest questions they will ask you and arms you with the answer that lands.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from pitch_lens.briefing import Wargame
from pitch_lens.pipeline import WargameInput, run_full

CACHE_DIR = Path(__file__).parent / "cache"

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

st.set_page_config(page_title="Pitch Wargames", page_icon="🎯", layout="wide")

# --- session state ---
if "wargame" not in st.session_state:
    st.session_state.wargame = None
if "running" not in st.session_state:
    st.session_state.running = False

# --- header ---
st.title("🎯 Pitch Wargames")
st.markdown(
    "**Adversarial pitch coach for founders, sales reps, and anyone walking into a high-stakes pitch.** "
    "Name the investor, judge, or buyer you're meeting — we predict the 5 hardest questions they'll ask, "
    "tied to *their* portfolio and *their* recent posts, and arm you with the answer that lands."
)
st.caption(
    "Powered by 4 composed Apify Actors (LinkedIn · X · Google Search · Web Crawler) "
    "+ Claude Sonnet 4.6. Demo target today: hackathon judges. Real market: investor pitches, sales calls, interviews."
)

# --- input form ---
with st.form("wargame_form", clear_on_submit=False):
    col1, col2 = st.columns([1, 1])
    with col1:
        judge_name = st.text_input(
            "Person you're pitching to *",
            placeholder="e.g. Petros Hong (judge), Marc Andreessen (VC), Jane Smith (CTO)",
            help="Investor, hackathon judge, sales prospect, interviewer — anyone you're about to pitch",
        )
        linkedin_url = st.text_input(
            "LinkedIn URL (optional but strongly recommended)",
            placeholder="https://linkedin.com/in/petroshong",
        )
        twitter_handle = st.text_input(
            "X / Twitter handle (optional)",
            placeholder="petroshong",
            help="Without the @",
        )
    with col2:
        pitch_text = st.text_area(
            "Your pitch in 2-3 sentences *",
            placeholder="(Paste your pitch here. Example: 'We help X solve Y by doing Z.')",
            height=160,
            help=(
                "The model conditions every predicted question on YOUR pitch. "
                "Generic pitches → generic questions. Specific pitches → specific questions."
            ),
        )

    submitted = st.form_submit_button(
        "🎯 Run the simulation",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.running,
    )

# --- Cached demo fallback (for wifi outages / Apify rate-limits during the demo) ---
cached = sorted(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else []
if cached:
    with st.expander("📦 Or load a cached demo (no API spend, instant)", expanded=False):
        for cf in cached:
            label = cf.stem.replace("_", " ").title()
            if st.button(f"Load: {label}", key=f"cache_{cf.stem}"):
                st.session_state.wargame = Wargame.model_validate_json(cf.read_text())
                st.session_state.running = False
                st.rerun()

if submitted:
    if not judge_name.strip() or not pitch_text.strip():
        st.error("Judge name and pitch text are both required.")
        st.stop()

    st.session_state.running = True
    st.session_state.wargame = None

    progress = st.progress(0, text="Starting…")

    def _on_progress(label: str, step: int, total: int) -> None:
        progress.progress(step / total, text=f"[{step}/{total}] {label}")

    try:
        result = run_full(
            WargameInput(
                judge_name=judge_name.strip(),
                pitch_text=pitch_text.strip(),
                linkedin_url=linkedin_url.strip() or None,
                twitter_handle=twitter_handle.strip() or None,
            ),
            on_progress=_on_progress,
        )
        st.session_state.wargame = result
        progress.progress(1.0, text="Done.")
    except Exception as e:
        st.error(f"Simulation failed: {e}")
        st.exception(e)
    finally:
        st.session_state.running = False


# --- styling: color-coded likelihood + card polish ---
_CARD_CSS = """
<style>
.killer-card {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    border: 2px solid #d32f2f;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 12px rgba(211, 47, 47, 0.15);
}
.very-likely-card {
    background: #fff8f0;
    border-left: 6px solid #f57c00;
    border-radius: 8px;
    padding: 1.25rem;
    margin: 0.75rem 0;
}
.likely-card {
    background: #fffef5;
    border-left: 6px solid #fbc02d;
    border-radius: 8px;
    padding: 1.25rem;
    margin: 0.75rem 0;
}
.q-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.q-badge.killer { background: #d32f2f; color: white; }
.q-badge.very_likely { background: #f57c00; color: white; }
.q-badge.likely { background: #fbc02d; color: #333; }
.q-text {
    font-size: 1.15rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0.75rem 0 1rem 0;
    line-height: 1.4;
}
.q-meta-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.25rem;
}
.q-why { color: #333; font-style: italic; margin-bottom: 1rem; line-height: 1.5; }
.answer-box {
    background: #e8f5e9;
    border-left: 4px solid #2e7d32;
    padding: 0.85rem 1rem;
    border-radius: 6px;
    margin: 0.5rem 0;
    line-height: 1.5;
}
.trap-box {
    background: #fff3e0;
    border-left: 4px solid #e65100;
    padding: 0.85rem 1rem;
    border-radius: 6px;
    margin: 0.5rem 0;
    line-height: 1.5;
}
.judge-hero {
    background: linear-gradient(135deg, #1a237e 0%, #311b92 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin: 1rem 0;
}
.judge-hero h2 { color: white !important; margin: 0 0 0.5rem 0; }
.judge-hero .one-liner { font-size: 1.05rem; line-height: 1.5; opacity: 0.95; }
.callout-hook {
    background: #e3f2fd;
    border: 2px solid #1976d2;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    line-height: 1.5;
}
.callout-ask {
    background: #f3e5f5;
    border: 2px solid #7b1fa2;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    line-height: 1.5;
}
.callout-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    opacity: 0.7;
}
</style>
"""


# --- result rendering ---
def render_wargame(w: Wargame) -> None:
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    st.divider()

    # Judge hero
    st.markdown(
        f"""<div class="judge-hero">
        <h2>⚔️ Pitching to: {w.judge_name}</h2>
        <div class="one-liner">{w.judge_one_liner}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Pitch echo (so user sees the model understood)
    with st.container(border=True):
        st.markdown("**📝 Your pitch (as the model understood it):**")
        st.caption(w.pitch_summary)

    # Hook + Ask side by side
    col_hook, col_ask = st.columns(2)
    with col_hook:
        st.markdown(
            f"""<div class="callout-hook">
            <div class="callout-label">🎤 Open with this</div>
            <div>{w.opening_hook}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_ask:
        st.markdown(
            f"""<div class="callout-ask">
            <div class="callout-label">💰 Close with this ask</div>
            <div>{w.closing_ask}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.markdown("## 🔥 Predicted questions")
    st.caption(
        f"{len(w.predicted_questions)} questions, ordered by likelihood. "
        "Every prediction is grounded in a specific trigger from the scraped data."
    )

    label_map = {"killer": "KILLER QUESTION", "very_likely": "VERY LIKELY", "likely": "LIKELY"}
    card_class_map = {"killer": "killer-card", "very_likely": "very-likely-card", "likely": "likely-card"}

    for i, q in enumerate(w.predicted_questions, 1):
        badge_label = label_map.get(q.likelihood, q.likelihood.upper())
        card_class = card_class_map.get(q.likelihood, "likely-card")

        st.markdown(
            f"""<div class="{card_class}">
            <span class="q-badge {q.likelihood}">Q{i} · {badge_label}</span>
            <div class="q-text">"{q.text}"</div>
            <div class="q-meta-label">Why they'll ask</div>
            <div class="q-why">{q.why_they_ask}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        ans, trap = st.columns(2)
        with ans:
            st.markdown(
                f"""<div class="answer-box">
                <div class="q-meta-label">✅ The answer that lands</div>
                <div>{q.suggested_answer}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with trap:
            st.markdown(
                f"""<div class="trap-box">
                <div class="q-meta-label">⚠️ Trap to avoid</div>
                <div>{q.trap_to_avoid}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("")  # spacing

    # Sources — inline, no click
    if w.sources:
        st.markdown("## 📚 Sources used")
        st.caption("Every claim above is grounded in one of these.")
        cols = st.columns(min(len(w.sources), 4))
        for i, s in enumerate(w.sources):
            with cols[i % len(cols)]:
                rel_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(s.relevance, "⚪")
                st.markdown(
                    f"{rel_emoji} **[{s.title or s.url[:40]}]({s.url})**  \n"
                    f"<small>{s.relevance} relevance</small>",
                    unsafe_allow_html=True,
                )

    # Raw JSON tucked at the very bottom for engineers
    with st.expander("🔧 Raw JSON (developers only)"):
        st.code(w.model_dump_json(indent=2), language="json")


if st.session_state.wargame:
    render_wargame(st.session_state.wargame)


# --- footer ---
st.divider()
st.caption(
    "Built for the *All Things Agent* Apify hackathon · May 6, 2026 · "
    "Set `MOCK_APIFY=1` in `.env` to demo without burning credits."
)
