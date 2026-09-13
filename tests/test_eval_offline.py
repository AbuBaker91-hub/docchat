"""The eval harness runs fully offline (StubEmbedder + canned MockProvider)
and prints two metrics between 0 and 1."""

from app.canned import eval_responses
from app.eval import print_metrics, run_eval
from app.ingest import ingest_pdf


def test_eval_runs_offline(test_db, mock_provider, mock_router, stub_embedder, sample_pdfs, capsys):
    assert len(sample_pdfs) == 3
    for pdf in sample_pdfs:
        result = ingest_pdf(test_db, stub_embedder, pdf.name, pdf.read_bytes())
        assert result["status"] == "ready"

    mock_provider.set("answer", eval_responses())
    metrics = run_eval(test_db, mock_router, stub_embedder)

    assert metrics["questions"] == 20
    assert 0.0 <= metrics["recall_at_8"] <= 1.0
    assert 0.0 <= metrics["citation_accuracy"] <= 1.0
    # the committed gold set must actually work with the stub embedder
    assert metrics["recall_at_8"] >= 0.6

    print_metrics(metrics)
    out = capsys.readouterr().out
    assert "recall@8" in out
    assert "citation_accuracy" in out
