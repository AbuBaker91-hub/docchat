"""Prepare a demo database end to end: run migrations, then ingest the three
sample PDFs. Idempotent - re-running is a fast no-op (migrations are tracked,
ingest is keyed on the file hash).

Run against a remote (e.g. Neon) database for the serverless demo. When
EMBEDDER is unset it defaults to the stub embedder here, matching the keyless
demo configuration so /ask works immediately:

    set DATABASE_URL=postgresql://<user>:<pass>@<host>/<db>
    .venv\\Scripts\\python.exe -m scripts.seed_remote
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def seed() -> None:
    from aiforge_core.db import connect, run_migrations

    from app.ingest import ingest_pdf
    from app.main import build_embedder

    conn = connect()
    applied = run_migrations(conn, ROOT / "migrations")
    print(f"migrations applied: {applied or 'none (up to date)'}")
    embedder = build_embedder()
    for pdf in sorted((ROOT / "samples" / "docs").glob("*.pdf")):
        result = ingest_pdf(conn, embedder, pdf.name, pdf.read_bytes())
        print(f"seed {pdf.name}: id={result['id']} status={result['status']}")
    conn.close()


if __name__ == "__main__":
    os.environ.setdefault("EMBEDDER", "stub")  # match the keyless demo deployment
    seed()
