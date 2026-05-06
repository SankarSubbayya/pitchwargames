"""FastAPI wrapper around the Pitch Wargames engine — used by the Next.js frontend."""

from __future__ import annotations

import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pitch_lens.briefing import Wargame
from pitch_lens.pipeline import WargameInput, run_full

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


app = FastAPI(
    title="Pitch Wargames API",
    description="Wraps the pitch_lens engine for the Next.js frontend.",
    version="0.1.0",
)

# Allow the Next.js dev server to call us locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WargameRequest(BaseModel):
    judge_name: str = Field(min_length=1)
    pitch_text: str = Field(min_length=1)
    linkedin_url: str | None = None
    twitter_handle: str | None = None


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "pitch-wargames-api"}


@app.post("/api/wargame", response_model=Wargame)
def wargame(req: WargameRequest) -> Wargame:
    log.info("wargame request: judge=%s, pitch_chars=%d", req.judge_name, len(req.pitch_text))
    try:
        return run_full(
            WargameInput(
                judge_name=req.judge_name.strip(),
                pitch_text=req.pitch_text.strip(),
                linkedin_url=(req.linkedin_url or "").strip() or None,
                twitter_handle=(req.twitter_handle or "").strip() or None,
            )
        )
    except Exception as e:
        log.exception("wargame failed")
        raise HTTPException(status_code=500, detail=str(e))
