"""Reproducible synthetic detector benchmark; not a production reliability claim."""

import argparse
import json
import platform
import random
import time
import tracemalloc
from pathlib import Path

from holdout_ledger import AuditConfig, Record, audit


def corpus(size: int, injected: int, seed: int = 42) -> tuple[list[Record], set[str]]:
    if injected < 1 or injected > size // 2:
        raise ValueError("injected must be between 1 and half the corpus size")
    rng = random.Random(seed)
    vocabulary = [f"term{i}" for i in range(20_000)]
    rows = [
        Record(id=f"train-{i:06d}", text=" ".join(rng.sample(vocabulary, 32)), split="train")
        for i in range(size)
    ]
    truth: set[str] = set()
    for i in range(injected):
        key = f"test-exact-{i:06d}"
        truth.add(key)
        rows.append(Record(id=key, text=rows[i].text, split="test"))
        key = f"test-near-{i:06d}"
        truth.add(key)
        words = rows[i + injected].text.split()
        words[-1] = f"replacement{i}"
        rows.append(Record(id=key, text=" ".join(words), split="test"))
    return rows, truth


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=3000)
    parser.add_argument("--injected", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("benchmark-result.json"))
    args = parser.parse_args()
    rows, truth = corpus(args.size, args.injected)
    tracemalloc.start()
    started = time.perf_counter()
    report = audit(rows, AuditConfig(mode="lsh"))
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    found = set(report.summary.exposed_holdout_ids)
    result = {
        "schema_version": 1,
        "python": platform.python_version(),
        "records": len(rows),
        "known_injected_holdouts": len(truth),
        "true_positives": len(found & truth),
        "false_positives": len(found - truth),
        "false_negatives": len(truth - found),
        "recall": len(found & truth) / len(truth),
        "wall_seconds": elapsed,
        "peak_python_allocation_bytes": peak,
        "candidate_pairs": report.summary.candidates_verified,
        "dataset_sha256": report.dataset_sha256,
        "report_sha256": report.report_sha256,
        "config": report.config.model_dump(),
        "environment": report.environment,
        "scope": "Synthetic exact copies and one-token suffix mutations; not real-world recall.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
