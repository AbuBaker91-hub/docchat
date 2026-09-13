"""Vercel serverless entrypoint: exposes the FastAPI ASGI app as `app`.

The demo deployment runs keyless: LLM_PROVIDER_ORDER=mock (canned answers
matched to the question) and EMBEDDER=stub (no model downloads). Cold start
runs the idempotent migrations; it never ingests sample PDFs - the remote
demo DB is seeded once with `python -m scripts.seed_remote`.
"""

import sys
from pathlib import Path

# make the repo root importable inside the serverless bundle
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402,F401
