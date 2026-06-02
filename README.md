# Mini Search Engine

A small but real search engine built from scratch — the kind of data-structures
and algorithms work behind tools like Google, implemented and tested step by step.

No black-box search library: the inverted index, ranking, and autocomplete are
all hand-written to demonstrate core CS fundamentals.

## How search works here

```
  documents ──► tokenizer ──► inverted index ──► BM25 ranking ──► results
                                    ▲                                 │
                              autocomplete (trie) ◄──── query ────────┘
```

- **Tokenizer** — turns text into clean, lowercased words and drops filler words.
- **Inverted index** — for every word, stores which documents contain it (and how
  often), so a search is an instant lookup instead of scanning everything.
- **Ranking (BM25)** — orders matches so the most relevant document comes first.
- **Autocomplete (trie)** — suggests completions as you type.

## Run the tests

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt
pytest -v
```

## Project status

- [x] **Step 1 — Index core:** tokenizer + inverted index + AND search (tested, CI)
- [ ] **Step 2 — Ranking:** BM25 relevance scoring (best result first)
- [ ] **Step 3 — Autocomplete:** trie-based query suggestions
- [ ] **Step 4 — Data:** load a real document set (e.g. Wikipedia samples)
- [ ] **Step 5 — API + UI:** search endpoint and a web page
- [ ] **Step 6 — Deploy:** put it live
