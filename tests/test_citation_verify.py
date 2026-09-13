"""A citation quote not present in the retrieved text is dropped; when all
citations are dropped the result is not_found."""

from aiforge_core import vectorstore
from aiforge_core.vectorstore import Chunk

from app.answer import ask
from app.verify import Answer, Citation, verify_citations

CHUNKS = [
    Chunk(1, "policy.pdf", 1, "Returns", "The standard return window is 30 days from delivery.", 1.0),
    Chunk(2, "policy.pdf", 2, "Shipping", "Standard shipping takes 5 to 7 business days.", 0.9),
]


def test_bad_quote_dropped_good_quote_kept():
    answer = Answer(
        answer="30 days.",
        citations=[
            Citation(doc="policy.pdf", page=1, quote="return\n   window is    30 days"),
            Citation(doc="policy.pdf", page=1, quote="this quote was never in any document"),
        ],
        confidence=0.9,
        found=True,
    )
    valid = verify_citations(answer, CHUNKS)
    assert [c.quote for c in valid] == ["return\n   window is    30 days"]


def test_right_quote_wrong_page_dropped():
    answer = Answer(
        answer="30 days.",
        citations=[Citation(doc="policy.pdf", page=2, quote="return window is 30 days")],
        confidence=0.9,
        found=True,
    )
    assert verify_citations(answer, CHUNKS) == []


def test_all_citations_dropped_becomes_not_found(test_db, mock_provider, mock_router, stub_embedder):
    vectorstore.upsert(
        test_db,
        [
            {"doc": "policy.pdf", "page": 1, "section": "Returns", "text": "The return window is 30 days."},
            {"doc": "policy.pdf", "page": 2, "section": "Shipping", "text": "Shipping takes 5 business days."},
            {"doc": "policy.pdf", "page": 3, "section": "Gifts", "text": "Gift cards never expire at all."},
        ],
        stub_embedder,
    )
    mock_provider.set(
        "answer",
        {
            "answer": "The return window is 30 days.",
            "citations": [{"doc": "policy.pdf", "page": 1, "quote": "an invented quote"}],
            "confidence": 0.9,
            "found": True,
        },
    )
    result = ask(test_db, mock_router, stub_embedder, "What is the return window?")
    assert result["status"] == "not_found"
    assert result["citations"] == []
    assert len(result["closest_passages"]) == 3
