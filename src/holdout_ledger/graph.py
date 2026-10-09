"""Deterministic union-find for witness graphs."""

from collections import defaultdict
from collections.abc import Iterable


class Components:
    def __init__(self, ids: Iterable[str]) -> None:
        self.parent = {key: key for key in ids}

    def find(self, key: str) -> str:
        root = key
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[key] != key:
            previous = self.parent[key]
            self.parent[key] = root
            key = previous
        return root

    def union(self, left: str, right: str) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            # A canonical minimum ID prevents input order from changing the roots.
            self.parent[max(a, b)] = min(a, b)

    def groups(self) -> list[list[str]]:
        result: dict[str, list[str]] = defaultdict(list)
        for key in sorted(self.parent):
            result[self.find(key)].append(key)
        return sorted(result.values(), key=lambda group: group[0])
