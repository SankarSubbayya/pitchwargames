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
            placeholder=(
                "We're building Pitch Wargames — an adversarial pitch coach that "
                "predicts the 5 hardest questions a specific judge will ask, using "
                "Apify-scraped social data and Claude. Founders walk in knowing the "
                "questions before they're asked."
            ),
            height=160,
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


# --- result rendering ---
def render_wargame(w: Wargame) -> None:
    st.divider()
    st.markdown(f"## ⚔️ Wargame: pitching **{w.pitch_summary[:80]}…** to **{w.judge_name}**")
    st.markdown(f"_{w.judge_one_liner}_")

    st.markdown("### 🎤 Open with this:")
    st.success(w.opening_hook)

    st.markdown("### 🔥 Predicted questions")
    st.caption("Click each card to reveal the answer that lands and the trap to avoid.")

    badge_color = {"killer": "🔴", "very_likely": "🟠", "likely": "🟡"}

    for i, q in enumerate(w.predicted_questions, 1):
        badge = badge_color.get(q.likelihood, "⚪")
        with st.expander(
            f"{badge}  **Q{i}** — {q.text}  _({q.likelihood.replace('_', ' ')})_",
            expanded=(q.likelihood == "killer"),
        ):
            st.markdown("**Why they'll ask:**")
            st.write(q.why_they_ask)
            st.markdown("**The answer that lands:**")
            st.info(q.suggested_answer)
            st.markdown("**Trap to avoid:**")
            st.warning(q.trap_to_avoid)

    st.markdown("### 💰 Close with this ask:")
    st.success(w.closing_ask)

    if w.sources:
        with st.expander(f"📚 Sources ({len(w.sources)})"):
            for s in w.sources:
                st.markdown(f"- [{s.title or s.url}]({s.url}) _({s.relevance})_")

    with st.expander("📋 Raw JSON (for debugging / submission)"):
        st.code(w.model_dump_json(indent=2), language="json")


if st.session_state.wargame:
    render_wargame(st.session_state.wargame)


# --- footer ---
st.divider()
st.caption(
    "Built for the *All Things Agent* Apify hackathon · May 6, 2026 · "
    "Set `MOCK_APIFY=1` in `.env` to demo without burning credits."
)
