"""
Command-line search — query the engine straight from the terminal.

    python -m searchengine.cli "inverted index"
    python -m searchengine.cli            # interactive mode
"""
import sys

from searchengine.engine import SearchEngine


def _show(engine: SearchEngine, query: str) -> None:
    hits = engine.search(query)
    if not hits:
        print("  no results")
        return
    for rank, hit in enumerate(hits, start=1):
        print(f"  {rank}. {hit.title}  ({hit.score:.2f})")
        print(f"     {hit.snippet}")


def main() -> None:
    engine = SearchEngine.from_corpus()
    print(f"Loaded {engine.index.num_documents} documents.\n")

    if len(sys.argv) > 1:  # one-shot query from the command line
        _show(engine, " ".join(sys.argv[1:]))
        return

    print("Type a query (blank line to quit).")
    while True:
        try:
            query = input("\nsearch> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            break
        _show(engine, query)


if __name__ == "__main__":
    main()
