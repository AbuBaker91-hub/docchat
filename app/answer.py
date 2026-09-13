"""Answer pipeline: retrieve -> generate -> verify -> store.

Every stage writes one audit row with ref = sha-hash of the question text.
The model never gets the last word: citations are checked against the source
text before the user sees them, and an unverifiable answer becomes not_found.
"""

import json

import psycopg
from aiforge_core import audit, vectorstore
from aiforge_core.llm import AllProvidersFailed, Router, ValidationFailed

from .verify import Answer, verify_citations

RETRIEVE_K = 8
CLOSEST_N = 3


def _passages(chunks: list, n: int) -> list[dict]:
    return [
        {"doc": c.doc, "page": c.page, "section": c.section or "", "text": c.text}
        for c in chunks[:n]
    ]


def ask(conn: psycopg.Connection, router: Router, embedder, question: str) -> dict:
    """Run the full pipeline for one question and persist the result."""
    ref = audit.input_hash(question)

    chunks = vectorstore.hybrid(conn, question, RETRIEVE_K, embedder)
    audit.record(conn, "retrieve", ref=ref, input_hash=ref, detail=f"{len(chunks)} chunks")

    chunk_payload = [
        {"doc": c.doc, "page": c.page, "section": c.section or "", "text": c.text} for c in chunks
    ]
    prompt_version = ""
    try:
        result = router.generate_json(
            "answer", {"question": question, "chunks": chunk_payload}, schema=Answer
        )
        prompt_version = result.prompt_version
    except (ValidationFailed, AllProvidersFailed) as e:
        audit.record(conn, "generate", ref=ref, ok=False, detail=f"{type(e).__name__}: {e}"[:500])
        payload = {"status": "failed", "detail": "The model could not produce a valid answer."}
        _store(conn, question, payload, "failed", prompt_version)
        return payload

    ans: Answer = result.data
    audit.record(
        conn,
        "generate",
        ref=ref,
        prompt_version=result.prompt_version,
        detail=f"provider={result.provider} found={ans.found} citations={len(ans.citations)}",
    )

    valid = verify_citations(ans, chunks)
    dropped = len(ans.citations) - len(valid)

    if ans.found and valid:
        payload = {
            "status": "answered",
            "answer": ans.answer,
            "citations": [c.model_dump() for c in valid],
            "confidence": ans.confidence,
        }
        status = "answered"
    else:
        payload = {
            "status": "not_found",
            "answer": "",
            "citations": [],
            "confidence": ans.confidence,
            "closest_passages": _passages(chunks, CLOSEST_N),
        }
        status = "not_found"
    audit.record(
        conn,
        "verify",
        ref=ref,
        prompt_version=result.prompt_version,
        detail=f"{len(valid)} valid, {dropped} dropped -> {status}",
    )

    qid = _store(conn, question, payload, status, prompt_version)
    payload["id"] = qid
    payload["question"] = question
    return payload


def _store(
    conn: psycopg.Connection, question: str, payload: dict, status: str, prompt_version: str
) -> int:
    row = conn.execute(
        """INSERT INTO questions (text, answer_json, status, prompt_version)
           VALUES (%s, %s, %s, %s) RETURNING id""",
        (question, json.dumps(payload), status, prompt_version),
    ).fetchone()
    return row[0]
