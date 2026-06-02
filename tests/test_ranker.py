"""Tests for BM25 ranking."""
from searchengine.index import InvertedIndex
from searchengine.ranker import bm25_search


def build_index():
    idx = InvertedIndex()
    idx.add_document(1, "the quick brown fox jumps", title="Fox")
    idx.add_document(2, "the lazy brown dog sleeps", title="Dog")
    idx.add_document(3, "quick quick quick rabbit runs fast", title="Rabbit")
    return idx


def test_ranks_more_relevant_document_first():
    idx = build_index()
    results = bm25_search(idx, "quick")
    # doc 3 uses "quick" three times -> should outrank doc 1's single use.
    assert results[0].doc_id == 3
    assert results[1].doc_id == 1


def test_returns_results_sorted_by_score_descending():
    idx = build_index()
    results = bm25_search(idx, "brown quick")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_or_semantics_matches_any_term():
    idx = build_index()
    # "fox" (doc1) and "dog" (doc2) -> both should appear.
    ids = {r.doc_id for r in bm25_search(idx, "fox dog")}
    assert ids == {1, 2}


def test_rare_term_outranks_common_term():
    idx = build_index()
    # "brown" is in 2 of 3 docs (common); "rabbit" is in 1 (rare).
    # A query for both should rank the doc with the rare term on top.
    results = bm25_search(idx, "brown rabbit")
    assert results[0].doc_id == 3


def test_limit_caps_number_of_results():
    idx = build_index()
    assert len(bm25_search(idx, "quick brown rabbit", limit=1)) == 1


def test_empty_query_returns_nothing():
    assert bm25_search(build_index(), "") == []


def test_unknown_term_returns_nothing():
    assert bm25_search(build_index(), "elephant") == []


def test_results_carry_title():
    results = bm25_search(build_index(), "rabbit")
    assert results[0].title == "Rabbit"
