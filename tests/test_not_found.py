"""MockProvider answers found=false -> status not_found with the 3 closest
passages, a stored question row and audit rows for every stage."""

from aiforge_core import audit, vectorstore

from app.answer import ask


def test_not_found_returns_three_closest_passages(test_db, mock_provider, mock_router, stub_embedder):
    vectorstore.upsert(
        test_db,
        [
            {"doc": "a.pdf", "page": 1, "section": "One", "text": "Alpha paragraph about kettles."},
            {"doc": "a.pdf", "page": 2, "section": "Two", "text": "Beta paragraph about shipping."},
            {"doc": "b.pdf", "page": 1, "section": "Three", "text": "Gamma paragraph about contracts."},
            {"doc": "b.pdf", "page": 2, "section": "Four", "text": "Delta paragraph about warranties."},
        ],
        stub_embedder,
    )
    mock_provider.set(
        "answer", {"answer": "", "citations": [], "confidence": 0.1, "found": False}
    )
    question = "Who won the 1998 world cup?"
    result = ask(test_db, mock_router, stub_embedder, question)

    assert result["status"] == "not_found"
    assert result["answer"] == ""
    assert len(result["closest_passages"]) == 3
    for passage in result["closest_passages"]:
        assert passage["doc"] and passage["text"]

    row = test_db.execute("SELECT status FROM questions WHERE text = %s", (question,)).fetchone()
    assert row[0] == "not_found"

    stages = [r["stage"] for r in audit.rows_for(test_db, audit.input_hash(question))]
    assert stages == ["retrieve", "generate", "verify"]
