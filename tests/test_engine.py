"""End-to-end tests for the full engine built from the bundled corpus."""
from searchengine.engine import SearchEngine


def test_loads_corpus():
    engine = SearchEngine.from_corpus()
    # The bundled corpus has 25 documents.
    assert engine.index.num_documents == 25


def test_search_returns_relevant_hit_first():
    engine = SearchEngine.from_corpus()
    hits = engine.search("inverted index")
    assert hits, "expected at least one hit"
    # The dedicated "Inverted Index" article should rank among the top results.
    assert "Inverted Index" in {h.title for h in hits[:3]}


def test_search_hits_carry_snippet_and_score():
    engine = SearchEngine.from_corpus()
    hit = engine.search("ranking")[0]
    assert hit.snippet
    assert hit.score > 0


def test_autocomplete_from_corpus_vocabulary():
    engine = SearchEngine.from_corpus()
    suggestions = engine.autocomplete("sear")
    assert "search" in suggestions


def test_autocomplete_ranks_common_words_first():
    engine = SearchEngine.from_corpus()
    # "search" appears very frequently across the corpus, so for prefix "se"
    # it should be among the top suggestions.
    assert "search" in engine.autocomplete("se", limit=5)


def test_search_no_match_returns_empty():
    engine = SearchEngine.from_corpus()
    assert engine.search("zzzznonexistent") == []
