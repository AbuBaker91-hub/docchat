"""FastAPI app: routes from the docchat spec on top of aiforge_core.create_app.

Embedder choice   EMBEDDER=stub -> StubEmbedder (offline, no downloads),
                  anything else -> real MiniLM (needs the [embeddings] extra).
Provider choice   LLM_PROVIDER_ORDER=mock -> MockProvider with canned answers
                  (keyless demo), otherwise the gemini -> groq chain from env.
"""

import os
from pathlib import Path

from aiforge_core.app import create_app
from aiforge_core.db import connect, run_migrations
from aiforge_core.llm import Router, router_from_env
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .answer import ask
from .eval import run_eval
from .ingest import ingest_pdf

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"


def build_embedder():
    if os.getenv("EMBEDDER", "").strip().lower() == "stub":
        from aiforge_core.embed import StubEmbedder

        return StubEmbedder()
    from aiforge_core.embed import Embedder

    return Embedder()


def _mock_router(responses: list) -> Router:
    from aiforge_core.llm.providers import MockProvider

    return Router([MockProvider({"answer": responses})], prompts_dir=PROMPTS_DIR)


def build_router(for_eval: bool = False) -> Router:
    if os.getenv("LLM_PROVIDER_ORDER", "gemini,groq").strip().lower() == "mock":
        from .canned import ask_responses, eval_responses

        return _mock_router(eval_responses() if for_eval else ask_responses())
    return router_from_env(PROMPTS_DIR)


app = create_app("docchat", static_dir=ROOT / "static")


@app.on_event("startup")
def startup() -> None:
    app.state.conn = connect()
    run_migrations(app.state.conn, ROOT / "migrations")
    app.state.embedder = build_embedder()
    app.state.router = build_router()


@app.on_event("shutdown")
def shutdown() -> None:
    app.state.conn.close()


class AskIn(BaseModel):
    question: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.post("/documents")
async def upload_document(request: Request, file: UploadFile) -> dict:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")
    state = request.app.state
    return ingest_pdf(state.conn, state.embedder, file.filename, data)


@app.get("/documents")
def list_documents(request: Request) -> list[dict]:
    rows = request.app.state.conn.execute(
        "SELECT id, filename, pages, status, uploaded_at FROM documents ORDER BY id"
    ).fetchall()
    return [
        {
            "id": r[0],
            "filename": r[1],
            "pages": r[2],
            "status": r[3],
            "uploaded_at": r[4].isoformat(),
        }
        for r in rows
    ]


@app.post("/ask")
def ask_route(request: Request, body: AskIn) -> dict:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    state = request.app.state
    return ask(state.conn, state.router, state.embedder, question)


@app.get("/questions")
def list_questions(request: Request) -> list[dict]:
    rows = request.app.state.conn.execute(
        """SELECT id, text, answer_json, status, prompt_version, created_at
           FROM questions ORDER BY id"""
    ).fetchall()
    return [
        {
            "id": r[0],
            "question": r[1],
            "result": r[2],
            "status": r[3],
            "prompt_version": r[4],
            "created_at": r[5].isoformat(),
        }
        for r in rows
    ]


@app.get("/eval")
def eval_route(request: Request) -> dict:
    state = request.app.state
    return run_eval(state.conn, build_router(for_eval=True), state.embedder)
