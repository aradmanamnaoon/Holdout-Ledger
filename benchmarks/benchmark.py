"""Seeded lexical/group leakage smoke benchmark; not a real-world accuracy estimate.

All test records have preassigned truth, including disjoint and below-threshold
negative cases. Metrics apply only to these constructed synthetic examples.
"""

import argparse
import json
import platform
import random
import statistics
import time
import tracemalloc
from pathlib import Path

from holdout_ledger import AuditConfig, Record, audit
from holdout_ledger.text import jaccard, shingles


def corpus(
    size: int, injected: int, negatives: int = 100, seed: int = 42
) -> tuple[list[Record], set[str], set[str]]:
    """Generate exact, lexical-near, and declared-group positives plus true negatives.

    'injected' is the count PER positive class. A hard negative changes the last
    eight of 32 words; its lexical shingle overlap is below the default 0.8
    threshold. Group positives have dissimilar text and an explicit shared ID.
    """
    hard_count = negatives // 2
    if injected < 1 or negatives < 2 or size < 3 * injected + hard_count:
        raise ValueError("require injected>=1, negatives>=2, size>=3*injected+negatives//2")
    rng = random.Random(seed)
    vocabulary = [f"term{i}" for i in range(20_000)]
    rows = [
        Record(id=f"train-{i:06d}", text=" ".join(rng.sample(vocabulary, 32)), split="train")
        for i in range(size)
    ]
    positives: set[str] = set()
    negative_ids: set[str] = set()
    for i in range(injected):
        exact_id = f"test-exact-{i:06d}"
        rows.append(Record(id=exact_id, text=rows[i].text, split="test"))
        positives.add(exact_id)

        near_id = f"test-near-{i:06d}"
        near_words = rows[injected + i].text.split()
        near_words[-1] = f"replacement{seed}_{i}"
        rows.append(Record(id=near_id, text=" ".join(near_words), split="test"))
        positives.add(near_id)

        group_id = f"subject-{seed}-{i}"
        group_index = 2 * injected + i
        rows[group_index] = rows[group_index].model_copy(update={"group_id": group_id})
        group_test_id = f"test-group-{i:06d}"
        rows.append(
            Record(
                id=group_test_id,
                text=" ".join(f"independentgroup{seed}_{i}_{j}" for j in range(32)),
                split="test",
                group_id=group_id,
            )
        )
        positives.add(group_test_id)

    for i in range(negatives):
        key = f"test-negative-{i:06d}"
        if i < hard_count:
            source = rows[3 * injected + i]
            words = source.text.split()
            words[-8:] = [f"independenthard{seed}_{i}_{j}" for j in range(8)]
            text = " ".join(words)
            if jaccard(shingles(source.text, 3), shingles(text, 3)) >= 0.8:
                raise AssertionError("constructed hard negative exceeds lexical oracle")
        else:
            text = " ".join(f"independentclean{seed}_{i}_{j}" for j in range(32))
        rows.append(Record(id=key, text=text, split="test"))
        negative_ids.add(key)
    return rows, positives, negative_ids


def confusion(
    found: set[str], positives: set[str], negatives: set[str]
) -> dict[str, int | float | None]:
    """Evaluate a complete labeled holdout; never invent undefined denominators."""
    if positives & negatives or found - (positives | negatives):
        raise ValueError("ground truth must partition all flagged holdout IDs")
    tp = len(found & positives)
    fp = len(found & negatives)
    fn = len(positives - found)
    tn = len(negatives - found)
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
    }


def run_once(size: int, injected: int, negatives: int, seed: int, mode: str) -> dict:
    """One fully labeled synthetic experiment, with reproducible input/report hashes."""
    rows, positives, negative_ids = corpus(size, injected, negatives, seed)
    config = AuditConfig(mode=mode)
    tracemalloc.start()
    started = time.perf_counter()
    try:
        report = audit(rows, config)
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    found = set(report.summary.exposed_holdout_ids)
    return {
        "seed": seed,
        "training_records": size,
        "test_positives": len(positives),
        "test_negatives": len(negative_ids),
        "records": len(rows),
        "counts_and_metrics": confusion(found, positives, negative_ids),
        "wall_seconds": elapsed,
        "peak_python_allocation_bytes": peak,
        "candidate_pairs": report.summary.candidates_verified,
        "dataset_sha256": report.dataset_sha256,
        "report_sha256": report.report_sha256,
        "method": report.method,
        "environment": report.environment,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=3000)
    parser.add_argument("--injected", type=int, default=100, help="positives per class")
    parser.add_argument("--negatives", type=int, default=100)
    parser.add_argument("--seeds", default="42,43,44,45,46")
    parser.add_argument("--mode", choices=["lsh", "exhaustive"], default="lsh")
    parser.add_argument("--check", action="store_true", help="gate planted positives and negatives")
    parser.add_argument("--output", type=Path, default=Path("benchmark-result.json"))
    args = parser.parse_args()
    try:
        seeds = [int(value.strip()) for value in args.seeds.split(",")]
        if not seeds or len(set(seeds)) != len(seeds) or any(seed < 0 for seed in seeds):
            raise ValueError("seeds must be unique nonnegative integers")
    except ValueError as exc:
        parser.error(str(exc))
    runs = [run_once(args.size, args.injected, args.negatives, seed, args.mode) for seed in seeds]
    metric_names = ("precision", "recall", "false_positive_rate")
    summary = {}
    for name in metric_names:
        values = [run["counts_and_metrics"][name] for run in runs]
        observed = [value for value in values if value is not None]
        summary[name] = (
            {"mean": statistics.mean(observed), "min": min(observed), "max": max(observed)}
            if observed
            else None
        )
    result = {
        "schema_version": 2,
        "python": platform.python_version(),
        "method": args.mode,
        "seeds": seeds,
        "config": AuditConfig(mode=args.mode).model_dump(),
        "results": runs,
        "descriptive_seed_range": summary,
        "scope": (
            "Only seeded constructed exact, lexical-near, declared-group, and clean/hard "
            "negative records. No claim of real-world sensitivity, specificity, "
            "semantic leakage coverage, clinical use or downstream model improvement."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if args.check and any(
        run["counts_and_metrics"]["false_negatives"] or run["counts_and_metrics"]["false_positives"]
        for run in runs
    ):
        raise SystemExit("synthetic labeled benchmark gate failed")


if __name__ == "__main__":
    main()
