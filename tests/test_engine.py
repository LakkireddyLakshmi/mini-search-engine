"""End-to-end tests for the full engine built from the bundled corpus."""
import gzip
import json

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


def test_loads_gzipped_corpus(tmp_path):
    path = tmp_path / "mini.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"title": "Cats", "text": "cats are small felines"}) + "\n")
        fh.write(json.dumps({"title": "Dogs", "text": "dogs are loyal animals"}) + "\n")
    engine = SearchEngine.from_corpus(path)
    assert engine.index.num_documents == 2
    assert engine.search("felines")[0].title == "Cats"


def test_stats_reports_index_size():
    stats = SearchEngine.from_corpus().stats()
    assert stats["documents"] == 25
    assert stats["terms"] > 0
