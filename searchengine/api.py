"""
HTTP API + web UI for the search engine.

A small FastAPI app that loads the corpus once at startup and exposes:

    GET /api/search?q=...&limit=...   -> ranked results as JSON
    GET /api/autocomplete?q=...       -> query suggestions as JSON
    GET /api/topics                   -> all document titles (for the UI)
    GET /                             -> a single-page search UI

Run it with:  uvicorn searchengine.api:app --reload
"""
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from searchengine.engine import SearchEngine

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Mini Search Engine", version="1.0")

# Build the index once when the server starts, then reuse it for every request.
engine = SearchEngine.from_corpus()


@app.get("/api/search")
def search(q: str = Query("", description="search query"), limit: int = 10):
    hits = engine.search(q, limit=limit)
    return {
        "query": q,
        "count": len(hits),
        "results": [
            {"title": h.title, "score": h.score, "snippet": h.snippet} for h in hits
        ],
    }


@app.get("/api/autocomplete")
def autocomplete(q: str = Query("", description="prefix to complete"), limit: int = 5):
    return {"query": q, "suggestions": engine.autocomplete(q, limit=limit)}


@app.get("/api/topics")
def topics():
    """The titles of every indexed document — used to show what's searchable."""
    return {"topics": [doc.title for doc in engine.index.documents.values()]}


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")
