# Mini Search Engine

A small but real search engine built from scratch — the kind of data-structures
and algorithms work behind tools like Google, implemented and tested step by step.

No black-box search library: the inverted index, BM25 ranking, and trie
autocomplete are all hand-written to demonstrate core CS fundamentals.

It indexes **5,000 real Wikipedia articles** and answers queries in **single-digit
milliseconds**.

**🔎 Live demo:** https://huggingface.co/spaces/sweety783/mini-search-engine

## Numbers

| Metric | Value |
| --- | --- |
| Documents indexed | 5,000 (Simple English Wikipedia) |
| Unique terms | ~50,000 |
| Index build time | ~2 s (one-time, at startup) |
| Query latency | ~0.3–2 ms |

Measured locally on the bundled corpus; reproduce with `scripts/build_corpus.py`.

## How search works here

```
  documents ──► tokenizer ──► inverted index ──► BM25 ranking ──► results
                                    ▲                                 │
                              autocomplete (trie) ◄──── query ────────┘
```

- **Tokenizer** — turns text into clean, lowercased words and drops filler words.
- **Inverted index** — for every word, stores which documents contain it (and how
  often), so a search is an instant lookup instead of scanning everything. Title
  words are weighted up (simple BM25F-style field boosting).
- **Ranking (BM25)** — scores each match by term frequency (with saturation),
  term rarity (IDF), and document length, so the most relevant document comes first.
- **Autocomplete (trie)** — a prefix tree that suggests completions as you type,
  ordered by how common each word is in the corpus.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements-dev.txt
```

**Search from the terminal:**

```bash
python -m searchengine.cli "inverted index"
```

**Run the web app** (search box with live autocomplete):

```bash
uvicorn searchengine.api:app --reload
# open http://127.0.0.1:8000
```

**HTTP API:**

```
GET /api/search?q=black+hole&limit=10   -> ranked results as JSON
GET /api/autocomplete?q=comp             -> query suggestions as JSON
GET /api/document?title=Black+hole       -> full article text
GET /api/stats                           -> index size + term count
```

## The corpus

The app ships with two corpora:

- `data/corpus.jsonl` — 25 hand-written CS/science articles (used by the tests, so
  they stay fast and deterministic).
- `data/wiki.jsonl` — 5,000 Simple English Wikipedia articles (what the deployed
  app serves). Regenerate it with:

  ```bash
  pip install huggingface_hub pyarrow
  python scripts/build_corpus.py 5000     # streams one Wikipedia parquet shard
  ```

The engine picks the corpus from the `CORPUS_PATH` env var (the Docker image sets
it to the Wikipedia corpus); without it, the small sample is used.

## Run the tests

```bash
pytest -v
```

45 tests cover the tokenizer, inverted index, BM25 ranking, trie autocomplete,
the end-to-end engine (plain + gzipped corpora), and the HTTP API.

## Project layout

```
searchengine/
  tokenizer.py      text -> clean tokens
  index.py          inverted index (with title boosting)
  ranker.py         BM25 relevance scoring
  autocomplete.py   trie / prefix tree
  engine.py         ties index + ranking + autocomplete together
  api.py            FastAPI endpoints + web UI
  cli.py            terminal search
scripts/build_corpus.py   build the Wikipedia corpus from the HF Hub
data/corpus.jsonl   bundled sample documents (25 CS/science articles, for tests)
data/wiki.jsonl     5,000 Simple English Wikipedia articles (served in prod)
static/index.html   single-page search UI
tests/              one test module per component
```

## Project status — complete

- [x] **Step 1 — Index core:** tokenizer + inverted index + AND search
- [x] **Step 2 — Ranking:** BM25 relevance scoring (best result first)
- [x] **Step 3 — Autocomplete:** trie-based query suggestions
- [x] **Step 4 — Data:** 5,000-article Wikipedia corpus + loader + build script
- [x] **Step 5 — API + UI:** search/autocomplete endpoints and a web page
- [ ] **Step 6 — Scale (next):** shard the index across processes/nodes with a
      gRPC query service and load-test it — turning this into a *distributed*
      search engine.
