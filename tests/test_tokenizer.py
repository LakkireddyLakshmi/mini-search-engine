"""Tests for the tokenizer."""
from searchengine.tokenizer import tokenize


def test_lowercases_and_splits():
    assert tokenize("Quick Brown Fox") == ["quick", "brown", "fox"]


def test_removes_stopwords():
    assert tokenize("the cat and the dog") == ["cat", "dog"]


def test_keeps_stopwords_when_asked():
    assert tokenize("the cat", remove_stopwords=False) == ["the", "cat"]


def test_handles_punctuation_and_numbers():
    assert tokenize("Hello, world! 2024") == ["hello", "world", "2024"]


def test_empty_text():
    assert tokenize("") == []
