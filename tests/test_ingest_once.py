"""Uploading the same bytes twice creates one document and no duplicate chunks."""

from app.ingest import ingest_pdf


def _count(conn, table: str) -> int:
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def test_same_bytes_twice_is_one_document(test_db, stub_embedder, sample_pdfs):
    pdf = sample_pdfs[0]
    data = pdf.read_bytes()

    first = ingest_pdf(test_db, stub_embedder, pdf.name, data)
    assert first["status"] == "ready"
    assert first["pages"] > 0
    docs_after_first = _count(test_db, "documents")
    chunks_after_first = _count(test_db, "chunks")
    assert docs_after_first == 1
    assert chunks_after_first > 0

    second = ingest_pdf(test_db, stub_embedder, pdf.name, data)
    assert second["id"] == first["id"]
    assert _count(test_db, "documents") == 1
    assert _count(test_db, "chunks") == chunks_after_first
