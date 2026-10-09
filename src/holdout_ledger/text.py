"""Explicit normalization and lexical similarity; no semantic model is implied."""

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable

from .models import Record


def canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    )


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def normalize(text: str, mode: str = "unicode") -> str:
    """NFKC + casefold + whitespace; Persian mode additionally folds Arabic ی/ک."""
    value = unicodedata.normalize("NFKC", text).casefold()
    if mode == "persian":
        for original, replacement in [("ي", "ی"), ("ى", "ی"), ("ك", "ک"), ("\u200c", " ")]:
            value = value.replace(original, replacement)
    return " ".join(value.split())


def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text, flags=re.UNICODE)


def shingles(text: str, width: int) -> set[str]:
    """Short texts use their complete token sequence, avoiding empty sketches."""
    words = tokens(text)
    if not words:
        return set()
    size = min(width, len(words))
    return {"\x1f".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def dataset_digest(records: Iterable[Record]) -> str:
    """Order-independent fingerprint binds all source fields, not only text."""
    return digest([r.model_dump() for r in sorted(records, key=lambda r: r.id)])
