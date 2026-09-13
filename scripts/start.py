"""Container / demo entrypoint: run migrations, seed the sample PDFs
idempotently (ingest is wrapped in once()), then start uvicorn."""

import os
import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def seed() -> None:
    from aiforge_core.db import connect, run_migrations

    from app.ingest import ingest_pdf
    from app.main import build_embedder

    conn = connect()
    run_migrations(conn, ROOT / "migrations")
    embedder = build_embedder()
    for pdf in sorted((ROOT / "samples" / "docs").glob("*.pdf")):
        result = ingest_pdf(conn, embedder, pdf.name, pdf.read_bytes())
        print(f"seed {pdf.name}: id={result['id']} status={result['status']}")
    conn.close()


if __name__ == "__main__":
    seed()
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
