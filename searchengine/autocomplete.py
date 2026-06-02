"""
Autocomplete — suggesting query completions as the user types.

The data structure for this is a *trie* (prefix tree). Every node is one
character; a path from the root spells out a prefix, and words branch off
shared prefixes. So "cat", "car" and "card" share the "ca" path:

        c - a - t*
                 \\- r* - d*     (* marks the end of a real word)

Finding every word that starts with "ca" is then just: walk to the "ca"
node, then collect everything below it — no scanning the whole vocabulary.
Each word also stores a weight (how often it appears) so the most common
completions are suggested first.
"""
from dataclasses import dataclass, field


@dataclass
class _Node:
    children: dict[str, "_Node"] = field(default_factory=dict)
    is_word: bool = False
    weight: int = 0  # popularity of the word ending here


class Trie:
    """A prefix tree for fast 'words starting with...' lookups."""

    def __init__(self) -> None:
        self.root = _Node()

    def insert(self, word: str, weight: int = 1) -> None:
        """Add a word (or bump its weight if already present)."""
        word = word.lower()
        if not word:
            return
        node = self.root
        for char in word:
            node = node.children.setdefault(char, _Node())
        node.is_word = True
        node.weight += weight

    def _find_node(self, prefix: str) -> "_Node | None":
        node = self.root
        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def _collect(self, node: "_Node", prefix: str) -> list[tuple[str, int]]:
        """Depth-first walk gathering every (word, weight) below a node."""
        found: list[tuple[str, int]] = []
        if node.is_word:
            found.append((prefix, node.weight))
        for char, child in node.children.items():
            found.extend(self._collect(child, prefix + char))
        return found

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """Return up to `limit` completions of `prefix`, most popular first."""
        prefix = prefix.lower()
        node = self._find_node(prefix)
        if node is None:
            return []
        words = self._collect(node, prefix)
        # Sort by weight (desc), then alphabetically for stable ties.
        words.sort(key=lambda wc: (-wc[1], wc[0]))
        return [word for word, _ in words[:limit]]
