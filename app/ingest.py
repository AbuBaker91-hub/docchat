"""PDF ingest: extract text per page, chunk, embed, upsert.

Wrapped in idempotency.once(key("ingest", file_hash)) so re-uploading the same
bytes returns the original document and creates no new rows or chunks.
"""

import hashlib
from io import BytesIO

import psycopg
from aiforge_core import audit, vectorstore
from aiforge_core.idempotency import key, once
from pypdf import PdfReader

from .chunk import chunk_page


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_pdf(conn: psycopg.Connection, embedder, filename: str, data: bytes) -> dict:
    """Ingest one PDF. Returns {"id", "status", "pages"}. Idempotent on bytes."""
    fhash = file_hash(data)

    def do() -> dict:
        try:
            reader = PdfReader(BytesIO(data))
            all_chunks: list[dict] = []
            for page_no, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                all_chunks.extend(chunk_page(filename, page_no, text))
            pages = len(reader.pages)
            inserted = vectorstore.upsert(conn, all_chunks, embedder)
            status = "ready"
        except Exception as e:  # noqa: BLE001 - a broken PDF must not 500 the API
            row = conn.execute(
                "INSERT INTO documents (filename, pages, status) VALUES (%s, 0, 'failed') RETURNING id",
                (filename,),
            ).fetchone()
            audit.record(
                conn, "ingest", ref=str(row[0]), input_hash=fhash[:16], ok=False, detail=str(e)[:500]
            )
            return {"id": row[0], "status": "failed", "pages": 0}
        row = conn.execute(
            "INSERT INTO documents (filename, pages, status) VALUES (%s, %s, 'ready') RETURNING id",
            (filename, pages),
        ).fetchone()
        audit.record(
            conn,
            "ingest",
            ref=str(row[0]),
            input_hash=fhash[:16],
            detail=f"{pages} pages, {len(all_chunks)} chunks, {inserted} new",
        )
        return {"id": row[0], "status": status, "pages": pages}

    result, _ran = once(conn, key("ingest", fhash), do)
    return result
