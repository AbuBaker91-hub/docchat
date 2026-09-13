# Same four commands in every aiforge project (+ eval here).
# Windows without make: run the commands inside each target directly,
# swapping .venv/bin/ for .venv\Scripts\.

PY := .venv/bin/python

.PHONY: setup test demo lint eval

setup:
	uv venv -p 3.12 .venv
	uv pip install -p .venv -e ".[dev]"
	docker compose up -d db
	$(PY) -c "from aiforge_core.db import connect, run_migrations; c = connect(); run_migrations(c, 'migrations'); c.close()"

test:
	$(PY) -m pytest -q

# Needs either the real embedder (uv pip install -p .venv -e ".[demo]") or
# EMBEDDER=stub for a zero-download offline demo. LLM_PROVIDER_ORDER=mock
# runs keyless with canned answers.
demo:
	docker compose up -d db
	$(PY) scripts/start.py

lint:
	$(PY) -m ruff check .

eval:
	$(PY) -m app.eval
