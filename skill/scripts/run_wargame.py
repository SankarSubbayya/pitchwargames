#!/usr/bin/env python3
"""OpenClaw skill entrypoint — runs the full Pitch Wargames pipeline and prints
the resulting Wargame as JSON to stdout."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make the parent package importable when this script is invoked from the skill dir.
_HERE = Path(__file__).resolve()
_PROJECT = _HERE.parent.parent.parent
sys.path.insert(0, str(_PROJECT))

from dotenv import load_dotenv  # noqa: E402

from pitch_lens.pipeline import WargameInput, run_full  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Pitch Wargames simulation.")
    parser.add_argument("--name", required=True, help="Full name of the person being pitched")
    parser.add_argument("--pitch", required=True, help="The founder's pitch in 2-3 sentences")
    parser.add_argument("--linkedin", default="", help="LinkedIn profile URL (optional)")
    parser.add_argument("--twitter", default="", help="X / Twitter handle without @ (optional)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    load_dotenv(_PROJECT / ".env")

    result = run_full(
        WargameInput(
            judge_name=args.name,
            pitch_text=args.pitch,
            linkedin_url=args.linkedin or None,
            twitter_handle=args.twitter or None,
        )
    )

    print(json.dumps(result.model_dump(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
