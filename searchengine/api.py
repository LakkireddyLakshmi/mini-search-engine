"""
HTTP API + web UI for the search engine.

A small FastAPI app that loads the corpus once at startup and exposes:

    GET /api/search?q=...&limit=...   -> ranked results as JSON
    GET /api/autocomplete?q=...       -> query suggestions as JSON
    GET /api/topics?limit=...         -> a sample of document titles
    GET /api/document?title=...       -> full text of one document
    GET /api/stats                    -> index headline numbers
    GET /                             -> a single-page search UI

Run it with:  uvicorn searchengine.api:app --reload

Set CORPUS_PATH to point at a different corpus (the deployed app uses the
8k-article Wikipedia corpus; tests fall back to the small bundled sample).
"""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from searchengine.engine import DEFAULT_CORPUS, SearchEngine

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
CORPUS_PATH = os.getenv("CORPUS_PATH", str(DEFAULT_CORPUS))

app = FastAPI(title="Mini Search Engine", version="1.0")

# Build the index once when the server starts, then reuse it for every request.
engine = SearchEngine.from_corpus(CORPUS_PATH)


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
def topics(limit: int = 50):
    """A sample of document titles — used to show what's searchable."""
    titles = [doc.title for doc in engine.index.documents.values()]
    return {"topics": titles[:limit]}


@app.get("/api/stats")
def stats():
    """Headline numbers about the index, shown in the UI."""
    return engine.stats()


@app.get("/api/document")
def document(title: str = Query(..., description="exact document title")):
    """Return the full text of a document so the UI can open it for reading."""
    for doc in engine.index.documents.values():
        if doc.title == title:
            return {"title": doc.title, "text": doc.text}
    raise HTTPException(status_code=404, detail="document not found")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")
