"""
Turn raw text into a clean list of search words ("tokens").

Searching works on words, not raw strings — so before we index or search any
text we: lowercase it (so "Apple" matches "apple"), split it into words, and
drop tiny filler words ("the", "a", "is") that add noise but no meaning.
"""
import re

# Common filler words that carry little search meaning.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was",
    "were", "will", "with", "this", "or", "but", "not", "they", "you",
}

_WORD_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Lowercase the text, extract word tokens, and drop stopwords."""
    tokens = _WORD_RE.findall(text.lower())
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens
