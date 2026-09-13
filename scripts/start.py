"""Container / demo entrypoint: run migrations, seed the sample PDFs
idempotently (ingest is wrapped in once()), then start uvicorn."""

import os
import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from scripts.seed_remote import seed

    seed()
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
