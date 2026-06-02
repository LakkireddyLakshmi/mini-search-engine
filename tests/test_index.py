"""Tests for the inverted index."""
from searchengine.index import InvertedIndex


def build_index():
    idx = InvertedIndex()
    idx.add_document(1, "the quick brown fox", title="Fox")
    idx.add_document(2, "the lazy brown dog", title="Dog")
    idx.add_document(3, "quick quick rabbit", title="Rabbit")
    return idx


def test_counts_documents():
    assert build_index().num_documents == 3


def test_postings_record_term_frequency():
    idx = build_index()
    # "quick" appears once in doc 1 and twice in doc 3
    assert idx.documents_containing("quick") == {1: 1, 3: 2}


def test_stopwords_are_not_indexed():
    idx = build_index()
    assert idx.documents_containing("the") == {}


def test_and_search_requires_all_terms():
    idx = build_index()
    # only doc 1 has both "quick" and "brown"
    assert idx.search_all("quick brown") == {1}


def test_search_single_term():
    idx = build_index()
    assert idx.search_all("brown") == {1, 2}


def test_search_no_match():
    idx = build_index()
    assert idx.search_all("elephant") == set()
