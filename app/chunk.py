"""Heading-aware chunking.

A page is split into sections at heading lines (Title Case or ALL CAPS lines
shorter than 80 characters), then each section is cut into ~500-token chunks
with an 80-token overlap. A heading always stays with its first paragraph
because it is prepended to the section body before cutting.

Token counts are approximated as words * 1.3 (a simple heuristic for English
prose with subword tokenizers); we never call a real tokenizer.
"""

TOKENS_PER_WORD = 1.3
CHUNK_TOKENS = 500
OVERLAP_TOKENS = 80

MAX_WORDS = int(CHUNK_TOKENS / TOKENS_PER_WORD)  # ~384 words per chunk
OVERLAP_WORDS = int(OVERLAP_TOKENS / TOKENS_PER_WORD)  # ~61 words of overlap

_SMALL_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "in",
    "of", "on", "or", "the", "to", "with",
}


def approx_tokens(text: str) -> int:
    return int(len(text.split()) * TOKENS_PER_WORD)


def _first_alpha(word: str) -> str:
    for ch in word:
        if ch.isalpha():
            return ch
    return ""


def is_heading(line: str) -> bool:
    """A heading is a short line (< 80 chars) in Title Case or ALL CAPS."""
    s = line.strip()
    if not s or len(s) >= 80:
        return False
    if s.endswith((".", ",", ";", ":")):
        return False
    words = [w for w in s.split() if _first_alpha(w)]
    if not words or len(words) > 10:
        return False
    if s == s.upper():
        return True  # ALL CAPS
    for i, w in enumerate(words):
        if i > 0 and w.lower() in _SMALL_WORDS:
            continue  # "Terms of Service" is still Title Case
        if not _first_alpha(w).isupper():
            return False
    return True


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split page text into (heading, body) pairs. Text before the first
    heading gets an empty heading."""
    sections: list[tuple[str, list[str]]] = []
    current_heading = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if is_heading(line):
            if current_lines or current_heading:
                sections.append((current_heading, current_lines))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_heading, current_lines))
    out = []
    for heading, lines in sections:
        body = "\n".join(lines).strip()
        if heading or body:
            out.append((heading, body))
    return out


def chunk_page(doc: str, page: int, text: str) -> list[dict]:
    """Chunk one page of extracted text into vectorstore-ready dicts."""
    chunks: list[dict] = []
    for heading, body in split_sections(text):
        full = f"{heading}\n{body}".strip()
        words = full.split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(len(words), start + MAX_WORDS)
            piece = " ".join(words[start:end])
            chunks.append({"doc": doc, "page": page, "section": heading, "text": piece})
            if end == len(words):
                break
            start = end - OVERLAP_WORDS
    return chunks
