"""Bounded canonical JSONL/CSV ingestion and explicit Hugging Face imports."""

import csv
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

from .models import Record, Split

MAX_LINE = 1_048_576


def read_records(path: Path) -> Iterator[Record]:
    """Stream canonical records; report malformed input with source line context."""
    if path.suffix.lower() == ".csv":
        csv.field_size_limit(MAX_LINE)
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            allowed = set(Record.model_fields)
            if not reader.fieldnames or not {"id", "text", "split"} <= set(reader.fieldnames):
                raise ValueError(f"{path}: CSV requires id,text,split columns")
            if not set(reader.fieldnames) <= allowed:
                raise ValueError(f"{path}: unexpected CSV columns")
            for line, raw in enumerate(reader, 2):
                if None in raw or any(value is None for value in raw.values()):
                    raise ValueError(f"{path}:{line}: mismatched CSV fields")
                payload: dict[str, Any] = dict(raw)
                for key in ("label", "group_id"):
                    if payload.get(key) == "":
                        payload[key] = None
                if "metadata" in payload:
                    payload["metadata"] = json.loads(payload["metadata"] or "{}")
                try:
                    yield Record.model_validate(payload)
                except ValueError as exc:
                    raise ValueError(f"{path}:{line}: invalid record") from exc
        return
    if path.suffix.lower() not in {".jsonl", ".ndjson"}:
        raise ValueError("input must be .jsonl, .ndjson, or .csv")
    with path.open(encoding="utf-8") as handle:
        line = 0
        while True:
            raw_line = handle.readline(MAX_LINE + 1)
            if not raw_line:
                break
            line += 1
            if len(raw_line.encode("utf-8")) > MAX_LINE:
                raise ValueError(f"{path}:{line}: record exceeds 1 MiB")
            if not raw_line.strip():
                continue
            try:
                yield Record.model_validate_json(raw_line)
            except ValueError as exc:
                raise ValueError(f"{path}:{line}: invalid record") from exc


def write_records(path: Path, records: Iterator[Record] | list[Record]) -> None:
    """Create a new file; remove an incomplete import if its stream fails."""
    handle = path.open("x", encoding="utf-8")
    try:
        with handle:
            for record in records:
                handle.write(record.model_dump_json() + "\n")
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def stream_hf(
    dataset: str,
    revision: str,
    source_split: str,
    target_split: Split,
    text_column: str,
    limit: int,
    subset: str | None = None,
    group_column: str | None = None,
    label_column: str | None = None,
) -> Iterator[Record]:
    """Import an explicitly bounded sample from an immutable dataset revision."""
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("revision must be the dataset repository's 40-character commit SHA")
    if limit < 1:
        raise ValueError("limit must be positive")
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ValueError("install holdout-ledger[hf] to import Hugging Face datasets") from exc
    stream = load_dataset(
        dataset, name=subset, split=source_split, revision=revision, streaming=True
    )
    iterator = iter(stream)
    for index in range(limit):
        try:
            row = next(iterator)
        except StopIteration:
            return
        text = row.get(text_column)
        if not isinstance(text, str):
            raise ValueError(f"row {index}: {text_column} must be text")
        group = row.get(group_column) if group_column else None
        label = row.get(label_column) if label_column else None
        yield Record(
            id=f"{dataset}:{source_split}:{index}",
            text=text,
            split=target_split,
            label=str(label) if label is not None else None,
            group_id=str(group) if group is not None else None,
            metadata={
                "dataset": dataset,
                "revision": revision.lower(),
                "source_split": source_split,
                "row_index": index,
                "sample_limit": limit,
                "subset": subset,
            },
        )


def load_json(path: Path) -> Any:
    if path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("JSON artifact exceeds 50 MiB")
    return cast(Any, json.loads(path.read_text(encoding="utf-8")))
