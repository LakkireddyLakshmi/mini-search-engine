"""Tests for the HTTP API."""
from fastapi.testclient import TestClient

from searchengine.api import app

client = TestClient(app)


def test_search_endpoint_returns_results():
    res = client.get("/api/search", params={"q": "inverted index"})
    assert res.status_code == 200
    body = res.json()
    assert body["count"] > 0
    assert body["results"][0]["title"] == "Inverted Index"
    assert "snippet" in body["results"][0]


def test_search_respects_limit():
    res = client.get("/api/search", params={"q": "search index data", "limit": 2})
    assert len(res.json()["results"]) == 2


def test_search_empty_query():
    res = client.get("/api/search", params={"q": ""})
    assert res.json()["count"] == 0


def test_autocomplete_endpoint():
    res = client.get("/api/autocomplete", params={"q": "sea"})
    assert res.status_code == 200
    assert "search" in res.json()["suggestions"]


def test_topics_endpoint_lists_titles():
    res = client.get("/api/topics")
    assert res.status_code == 200
    topics = res.json()["topics"]
    assert len(topics) == 25
    assert "Inverted Index" in topics


def test_document_endpoint_returns_full_text():
    res = client.get("/api/document", params={"title": "Trie"})
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Trie"
    assert "prefix tree" in body["text"]


def test_document_endpoint_404_for_unknown_title():
    res = client.get("/api/document", params={"title": "Nope"})
    assert res.status_code == 404


def test_home_serves_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
