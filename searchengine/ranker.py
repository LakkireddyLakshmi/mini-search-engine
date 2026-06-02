"""
Ranking — deciding which matching document comes *first*.

AND-search tells us *which* documents match, but not which is most relevant.
BM25 is the ranking function used by real search engines (Elasticsearch,
Lucene). For each query word it rewards two things and penalises one:

  * term frequency  — a doc that uses the word more is more relevant,
                      but with diminishing returns (saturates, via k1).
  * rarity (IDF)    — a rare word ("photosynthesis") is a stronger signal
                      than a common one ("data").
  * length (b)      — long documents naturally contain more words, so we
                      normalise by length to stop them dominating.

The score of a document is the sum of these per-word scores.
"""
import math
from dataclasses import dataclass

from searchengine.index import InvertedIndex
from searchengine.tokenizer import tokenize

# Standard BM25 tuning constants (the values Lucene ships with).
K1 = 1.5  # term-frequency saturation point
B = 0.75  # how strongly to penalise long documents


@dataclass
class SearchResult:
    """One ranked hit: which document, how relevant, and its title."""

    doc_id: int
    score: float
    title: str


def _idf(index: InvertedIndex, term: str) -> float:
    """Inverse document frequency — how rare (and therefore informative) a term is."""
    n_docs_with_term = len(index.documents_containing(term))
    if n_docs_with_term == 0:
        return 0.0
    n = index.num_documents
    # +0.5 smoothing keeps the value finite and non-negative.
    return math.log(1 + (n - n_docs_with_term + 0.5) / (n_docs_with_term + 0.5))


def _avg_doc_length(index: InvertedIndex) -> float:
    if index.num_documents == 0:
        return 0.0
    total = sum(doc.length for doc in index.documents.values())
    return total / index.num_documents


def bm25_search(index: InvertedIndex, query: str, limit: int = 10) -> list[SearchResult]:
    """Return the best-matching documents for a query, most relevant first.

    Unlike AND-search this is OR-style: a document matching *any* query term
    is a candidate, and BM25 sorts the candidates by relevance.
    """
    terms = tokenize(query)
    if not terms:
        return []

    avgdl = _avg_doc_length(index)
    scores: dict[int, float] = {}

    for term in terms:
        idf = _idf(index, term)
        if idf == 0.0:
            continue
        for doc_id, freq in index.documents_containing(term).items():
            doc_len = index.documents[doc_id].length
            # BM25 term contribution: saturating TF, length-normalised.
            denom = freq + K1 * (1 - B + B * doc_len / avgdl) if avgdl else freq + K1
            scores[doc_id] = scores.get(doc_id, 0.0) + idf * (freq * (K1 + 1)) / denom

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [
        SearchResult(doc_id=doc_id, score=score, title=index.documents[doc_id].title)
        for doc_id, score in ranked[:limit]
    ]
