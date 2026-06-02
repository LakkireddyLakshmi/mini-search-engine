"""Tests for trie-based autocomplete."""
from searchengine.autocomplete import Trie


def build_trie():
    t = Trie()
    for word in ["cat", "car", "card", "care", "dog"]:
        t.insert(word)
    return t


def test_suggests_words_with_prefix():
    assert set(build_trie().suggest("ca")) == {"cat", "car", "card", "care"}


def test_prefix_with_single_match():
    assert build_trie().suggest("do") == ["dog"]


def test_unknown_prefix_returns_empty():
    assert build_trie().suggest("xyz") == []


def test_more_popular_word_suggested_first():
    t = Trie()
    t.insert("car", weight=1)
    t.insert("card", weight=10)
    assert t.suggest("car")[0] == "card"


def test_ties_break_alphabetically():
    t = Trie()
    t.insert("care")
    t.insert("card")
    # equal weight -> alphabetical order
    assert t.suggest("car") == ["card", "care"]


def test_limit_caps_suggestions():
    assert len(build_trie().suggest("ca", limit=2)) == 2


def test_insert_is_case_insensitive():
    t = Trie()
    t.insert("Cat")
    assert t.suggest("ca") == ["cat"]


def test_repeated_insert_increases_weight():
    t = Trie()
    t.insert("car")
    t.insert("card")
    t.insert("card")  # card now weight 2
    assert t.suggest("car")[0] == "card"


def test_empty_prefix_returns_all_words():
    assert set(build_trie().suggest("", limit=10)) == {
        "cat", "car", "card", "care", "dog"
    }
