"""Vector and keyword results sharing a chunk id fuse into one entry."""

from aiforge_core.vectorstore import Chunk, merge_results


def _chunk(cid: int, score: float) -> Chunk:
    return Chunk(cid, "doc.pdf", 1, "S", f"text {cid}", score)


def test_shared_chunk_id_deduped():
    vector = [_chunk(1, 0.9), _chunk(2, 0.8)]
    keyword = [_chunk(1, 0.7), _chunk(3, 0.6)]
    merged = merge_results(vector, keyword, k=10)
    ids = [c.id for c in merged]
    assert sorted(ids) == [1, 2, 3]
    assert len(ids) == len(set(ids))


def test_shared_chunk_ranks_first():
    # chunk 1 appears in both lists, so reciprocal-rank fusion must rank it top
    vector = [_chunk(2, 0.99), _chunk(1, 0.5)]
    keyword = [_chunk(1, 0.9), _chunk(3, 0.1)]
    merged = merge_results(vector, keyword, k=2)
    assert merged[0].id == 1
    assert len(merged) == 2
