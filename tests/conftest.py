"""pytest setup — load .env so integration tests can find APIFY_API_TOKEN
and ANTHROPIC_API_KEY without exporting them in the shell."""

from pathlib import Path

from dotenv import load_dotenv

# .env is at the project root, one level up from tests/
load_dotenv(Path(__file__).parent.parent / ".env")
