"""Deterministic citation verification.

Every citation quote must appear as a whitespace-normalized substring of a
retrieved chunk with the same doc and page. Bad citations are dropped, never
shown. If nothing valid remains the answer becomes not_found.
"""

from aiforge_core.vectorstore import Chunk
from pydantic import BaseModel, Field


class Citation(BaseModel):
    doc: str
    page: int
    quote: str


class Answer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    found: bool = False


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def verify_citations(answer: Answer, chunks: list[Chunk]) -> list[Citation]:
    """Return only the citations whose quote really appears in a retrieved
    chunk with the same doc and page."""
    valid: list[Citation] = []
    for cit in answer.citations:
        quote = normalize_ws(cit.quote)
        if not quote:
            continue
        for chunk in chunks:
            if chunk.doc == cit.doc and chunk.page == cit.page and quote in normalize_ws(chunk.text):
                valid.append(cit)
                break
    return valid
