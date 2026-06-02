"""
The inverted index — the core data structure of any search engine.

A normal list would force us to scan every document for every query (slow).
An *inverted index* flips that around: for each word, it stores the list of
documents that contain it (and how many times). So a search becomes an instant
dictionary lookup instead of a full scan — the same idea behind Google.

Example, after indexing:
    doc 1: "the quick brown fox"
    doc 2: "the lazy brown dog"
the index for "brown" -> {1: 1, 2: 1}, for "fox" -> {1: 1}.
"""
from collections import defaultdict
from dataclasses import dataclass, field

from searchengine.tokenizer import tokenize


@dataclass
class Document:
    """A stored document and its metadata."""

    doc_id: int
    title: str
    text: str
    length: int  # number of tokens — used later for ranking


class InvertedIndex:
    """Maps each word to the documents (and counts) where it appears."""

    def __init__(self) -> None:
        # term -> {doc_id: term_frequency}
        self.postings: dict[str, dict[int, int]] = defaultdict(dict)
        # doc_id -> Document
        self.documents: dict[int, Document] = {}

    def add_document(self, doc_id: int, text: str, title: str = "") -> None:
        """Tokenize a document and record where each word appears."""
        tokens = tokenize(text)
        counts: dict[str, int] = defaultdict(int)
        for token in tokens:
            counts[token] += 1
        for term, freq in counts.items():
            self.postings[term][doc_id] = freq
        self.documents[doc_id] = Document(
            doc_id=doc_id, title=title, text=text, length=len(tokens)
        )

    def documents_containing(self, term: str) -> dict[int, int]:
        """Return {doc_id: term_frequency} for a single term."""
        return self.postings.get(term, {})

    def search_all(self, query: str) -> set[int]:
        """Return doc ids that contain ALL the query words (AND search)."""
        terms = tokenize(query)
        if not terms:
            return set()
        result: set[int] | None = None
        for term in terms:
            ids = set(self.documents_containing(term).keys())
            result = ids if result is None else (result & ids)
            if not result:
                break
        return result or set()

    @property
    def num_documents(self) -> int:
        return len(self.documents)
