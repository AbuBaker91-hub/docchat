"""Chunk boundaries: heading stays with its paragraph, overlap exists,
no empty chunks. No LLM, no DB."""

from app.chunk import MAX_WORDS, OVERLAP_WORDS, chunk_page, is_heading

PARAGRAPH = (
    "The standard return window is 30 days from the date of delivery. "
    "Items must be unused and in their original packaging."
)


def test_heading_stays_with_first_paragraph():
    text = "Intro line about nothing in particular.\n\nReturns and Refunds\n" + PARAGRAPH
    chunks = chunk_page("doc.pdf", 1, text)
    with_heading = [c for c in chunks if "Returns and Refunds" in c["text"]]
    assert len(with_heading) == 1
    assert "The standard return window is 30 days" in with_heading[0]["text"]
    assert with_heading[0]["section"] == "Returns and Refunds"


def test_all_caps_heading_detected():
    assert is_heading("IMPORTANT SAFETY INSTRUCTIONS")
    assert is_heading("Returns and Refunds")
    assert not is_heading("This is a normal sentence that ends with a period.")
    assert not is_heading("x" * 90)


def test_overlap_present():
    words = [f"word{i}" for i in range(MAX_WORDS * 2)]
    chunks = chunk_page("doc.pdf", 1, " ".join(words))
    assert len(chunks) >= 2
    first, second = chunks[0]["text"].split(), chunks[1]["text"].split()
    assert first[-OVERLAP_WORDS:] == second[:OVERLAP_WORDS]


def test_no_empty_chunks():
    for text in ["", "   \n\n  ", "Heading Only", PARAGRAPH, "A Title\n\n" + PARAGRAPH]:
        for c in chunk_page("doc.pdf", 1, text):
            assert c["text"].strip()
