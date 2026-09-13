"""Eval harness: retrieval recall@8 and citation accuracy over samples/gold.jsonl.

recall@8          was a chunk from the expected doc + page among the 8 retrieved
citation_accuracy share of gold questions whose final VERIFIED citations point
                  at the expected doc + page

Runs offline with StubEmbedder + MockProvider (EMBEDDER=stub,
LLM_PROVIDER_ORDER=mock) so the harness itself is testable, and with the real
embedder/providers in production.
"""

import json
from pathlib import Path

import psycopg
from aiforge_core import vectorstore
from aiforge_core.llm import Router

from .verify import Answer, verify_citations

ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = ROOT / "samples" / "gold.jsonl"
K = 8


def load_gold(path: str | Path = GOLD_PATH) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def run_eval(
    conn: psycopg.Connection, router: Router, embedder, gold_path: str | Path = GOLD_PATH
) -> dict:
    gold = load_gold(gold_path)
    recall_hits = 0
    citation_hits = 0
    for item in gold:
        question = item["question"]
        expected = (item["expected_doc"], item["expected_page"])
        chunks = vectorstore.hybrid(conn, question, K, embedder)
        if any((c.doc, c.page) == expected for c in chunks):
            recall_hits += 1
        chunk_payload = [
            {"doc": c.doc, "page": c.page, "section": c.section or "", "text": c.text}
            for c in chunks
        ]
        try:
            result = router.generate_json(
                "answer", {"question": question, "chunks": chunk_payload}, schema=Answer
            )
            valid = verify_citations(result.data, chunks)
        except Exception:  # noqa: BLE001 - one bad generation must not stop the eval
            valid = []
        if any((c.doc, c.page) == expected for c in valid):
            citation_hits += 1
    n = len(gold)
    return {
        "recall_at_8": round(recall_hits / n, 3),
        "citation_accuracy": round(citation_hits / n, 3),
        "questions": n,
    }


def print_metrics(metrics: dict) -> None:
    print(f"recall@8           {metrics['recall_at_8']}")
    print(f"citation_accuracy  {metrics['citation_accuracy']}")
    print(f"questions          {metrics['questions']}")


def main() -> None:
    from aiforge_core.db import connect, run_migrations

    from .main import build_embedder, build_router

    conn = connect()
    run_migrations(conn, ROOT / "migrations")
    metrics = run_eval(conn, build_router(for_eval=True), build_embedder())
    print_metrics(metrics)
    conn.close()


if __name__ == "__main__":
    main()
