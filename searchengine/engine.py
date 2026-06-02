"""
The search engine — ties every piece together into one object.

This is the layer the API and CLI talk to. It loads a corpus of documents,
builds the inverted index (for matching) and a trie (for autocomplete), and
exposes two operations:

    search(query)        -> ranked list of relevant documents (BM25)
    autocomplete(prefix) -> popular query completions (trie)

The trie is seeded from the indexed vocabulary, weighting each word by how
often it appears across the whole corpus, so common terms surface first.
"""
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from searchengine.autocomplete import Trie
from searchengine.index import InvertedIndex
from searchengine.ranker import SearchResult, bm25_search

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus.jsonl"


@dataclass
class Hit:
    """A search result enriched with a snippet of the document text."""

    doc_id: int
    title: str
    score: float
    snippet: str


class SearchEngine:
    """A complete in-memory search engine: index + ranking + autocomplete."""

    def __init__(self) -> None:
        self.index = InvertedIndex()
        self.trie = Trie()

    def add_document(self, doc_id: int, text: str, title: str = "") -> None:
        self.index.add_document(doc_id, text, title=title)

    def build_autocomplete(self) -> None:
        """Seed the trie from the index, weighting words by total frequency."""
        totals: dict[str, int] = defaultdict(int)
        for term, postings in self.index.postings.items():
            totals[term] += sum(postings.values())
        for term, weight in totals.items():
            self.trie.insert(term, weight=weight)

    @classmethod
    def from_corpus(cls, path: Path | str = DEFAULT_CORPUS) -> "SearchEngine":
        """Build an engine from a JSONL file of {"title", "text"} records."""
        engine = cls()
        with open(path, encoding="utf-8") as fh:
            for doc_id, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                engine.add_document(
                    doc_id, record["text"], title=record.get("title", "")
                )
        engine.build_autocomplete()
        return engine

    def _snippet(self, doc_id: int, length: int = 160) -> str:
        text = self.index.documents[doc_id].text
        return text if len(text) <= length else text[:length].rsplit(" ", 1)[0] + "…"

    def search(self, query: str, limit: int = 10) -> list[Hit]:
        results: list[SearchResult] = bm25_search(self.index, query, limit=limit)
        return [
            Hit(
                doc_id=r.doc_id,
                title=r.title,
                score=round(r.score, 4),
                snippet=self._snippet(r.doc_id),
            )
            for r in results
        ]

    def autocomplete(self, prefix: str, limit: int = 5) -> list[str]:
        return self.trie.suggest(prefix, limit=limit)
