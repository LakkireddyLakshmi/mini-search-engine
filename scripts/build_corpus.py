"""
Build a real search corpus from Simple English Wikipedia.

Downloads one parquet shard of `wikimedia/wikipedia` (the 20231101.simple
config) from the Hugging Face Hub and streams it row-batch by row-batch — so
it never loads the whole file into memory — keeping the first N substantial
articles. The result is written as gzipped JSONL of {"title", "text"} records,
the same format the engine already loads.

    python scripts/build_corpus.py            # default: 8000 articles
    python scripts/build_corpus.py 20000      # more articles

Re-run this to regenerate data/wiki.jsonl.gz; it is what the deployed app serves.
"""
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

# Plain JSONL (not gzipped): Hugging Face Spaces reject binary files outside
# LFS, and a text file under ~10 MB pushes cleanly.
OUT = Path(__file__).resolve().parent.parent / "data" / "wiki.jsonl"
MIN_CHARS = 400      # skip stubs / disambiguation pages
MAX_CHARS = 1500     # cap very long articles to keep the corpus under 10 MB
DEFAULT_N = 5000


def main(n: int = DEFAULT_N) -> None:
    print(f"Downloading Simple English Wikipedia parquet (one shard)…")
    path = hf_hub_download(
        repo_id="wikimedia/wikipedia",
        filename="20231101.simple/train-00000-of-00001.parquet",
        repo_type="dataset",
    )

    pf = pq.ParquetFile(path)
    kept = 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as out:
        # Stream in batches instead of reading the whole file at once.
        for batch in pf.iter_batches(batch_size=1000, columns=["title", "text"]):
            titles = batch.column("title").to_pylist()
            texts = batch.column("text").to_pylist()
            for title, text in zip(titles, texts):
                if not text or len(text) < MIN_CHARS:
                    continue
                clean = " ".join(text.split())[:MAX_CHARS]
                out.write(json.dumps({"title": title, "text": clean}) + "\n")
                kept += 1
                if kept >= n:
                    break
            if kept >= n:
                break

    size_mb = OUT.stat().st_size / 1e6
    print(f"Wrote {kept} articles to {OUT}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    main(count)
