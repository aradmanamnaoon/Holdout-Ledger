"""Same-input baselines and uncertainty for constructed synthetic leakage fixtures.

Use only seeded ground truth from benchmark.corpus. Wilson intervals describe
these created fixtures, NOT external/general-population performance.
"""

import argparse
import json
import math
import statistics
from pathlib import Path

from benchmarks.benchmark import confusion, corpus
from holdout_ledger import AuditConfig, Record, audit
from holdout_ledger.text import normalize


def baseline_ids(rows: list[Record]) -> dict[str, set[str]]:
    train_texts: set[str] = set()
    train_groups: set[str] = set()
    for row in rows:
        if row.split == "train":
            text = normalize(row.text)
            if text:
                train_texts.add(text)
            if row.group_id is not None:
                train_groups.add(row.group_id)
    exact = {
        row.id
        for row in rows
        if row.split == "test" and normalize(row.text) in train_texts
    }
    group = {
        row.id
        for row in rows
        if row.split == "test"
        and row.group_id is not None
        and row.group_id in train_groups
    }
    return {"normalized_exact": exact, "declared_group": group, "exact_or_group": exact | group}


def wilson_interval(successes: int, total: int) -> list[float] | None:
    """95% Wilson binomial interval; sampling assumptions do not hold across seeds."""
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total**2)) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def compare_seed(size: int, injected: int, negatives: int, seed: int) -> dict:
    rows, positives, negative_ids = corpus(size, injected, negatives, seed)
    baselines = baseline_ids(rows)
    reference = audit(rows, AuditConfig(mode="exhaustive", exhaustive_limit=3000))
    approximate = audit(rows, AuditConfig(mode="lsh"))
    results = {
        name: confusion(found, positives, negative_ids) for name, found in baselines.items()
    }
    results["exhaustive_lexical_group"] = confusion(
        set(reference.summary.exposed_holdout_ids), positives, negative_ids
    )
    results["lsh_lexical_group"] = confusion(
        set(approximate.summary.exposed_holdout_ids), positives, negative_ids
    )
    oracle_near = {
        (edge.left, edge.right)
        for edge in reference.edges
        if edge.kind == "near"
    }
    candidate_near = {
        (edge.left, edge.right)
        for edge in approximate.edges
        if edge.kind == "near"
    }
    return {
        "seed": seed,
        "records": len(rows),
        "positives": len(positives),
        "negatives": len(negative_ids),
        "metrics": results,
        "lexical_near_pairs_found_by_exhaustive": len(oracle_near),
        "lexical_near_pairs_found_by_lsh": len(candidate_near),
        "lsh_near_edge_recall_vs_exhaustive": (
            len(oracle_near & candidate_near) / len(oracle_near) if oracle_near else None
        ),
        "dataset_sha256": reference.dataset_sha256,
        "exhaustive_report_sha256": reference.report_sha256,
        "lsh_report_sha256": approximate.report_sha256,
    }


def summarize(runs: list[dict]) -> dict:
    metric_fields = ("true_positives", "false_positives", "false_negatives", "true_negatives")
    out: dict = {}
    for method in runs[0]["metrics"]:
        totals = {
            key: sum(run["metrics"][method][key] for run in runs) for key in metric_fields
        }
        recall_range = [run["metrics"][method]["recall"] for run in runs]
        fpr_range = [run["metrics"][method]["false_positive_rate"] for run in runs]
        recall_values = [v for v in recall_range if v is not None]
        fpr_values = [v for v in fpr_range if v is not None]
        out[method] = {
            "pooled_counts": totals,
            "seed_recall_min_mean_max": (
                [min(recall_values), statistics.mean(recall_values), max(recall_values)]
                if recall_values else None
            ),
            "seed_fpr_min_mean_max": (
                [min(fpr_values), statistics.mean(fpr_values), max(fpr_values)]
                if fpr_values else None
            ),
            "illustrative_wilson_95_recall": wilson_interval(
                totals["true_positives"], totals["true_positives"] + totals["false_negatives"]
            ),
            "illustrative_wilson_95_specificity": wilson_interval(
                totals["true_negatives"], totals["true_negatives"] + totals["false_positives"]
            ),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=80)
    parser.add_argument("--injected", type=int, default=4)
    parser.add_argument("--negatives", type=int, default=12)
    parser.add_argument("--seeds", default="42,43,44,45,46")
    parser.add_argument("--output", type=Path, default=Path("baseline-comparison.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.size <= 200:
        parser.error("exhaustive reference is bounded to training size 1..200")
    try:
        seeds = [int(value) for value in args.seeds.split(",")]
        if not seeds or len(set(seeds)) != len(seeds) or any(s < 0 for s in seeds):
            raise ValueError("seeds must be distinct nonnegative integers")
    except ValueError as exc:
        parser.error(str(exc))
    runs = [compare_seed(args.size, args.injected, args.negatives, seed) for seed in seeds]
    output = {
        "schema_version": 1,
        "experiment_type": "synthetic same-input baseline comparison",
        "seed_list": seeds,
        "runs": runs,
        "method_summary": summarize(runs),
        "disclosure": (
            "Synthetic planted labels and repeated fixtures are not independent "
            "real-world samples. Wilson bounds are illustrative under a binomial "
            "assumption that does not hold for generalization; they are not "
            "empirical real-world confidence intervals. Exhaustive is a lexical "
            "reference implementation, not independent human ground truth."
        ),
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if args.check:
        assert all(
            run["metrics"]["lsh_lexical_group"] == run["metrics"]["exhaustive_lexical_group"]
            and run["metrics"]["lsh_lexical_group"]["false_negatives"] == 0
            and run["metrics"]["lsh_lexical_group"]["false_positives"] == 0
            and run["lsh_near_edge_recall_vs_exhaustive"] == 1.0
            for run in runs
        ), "same-input LSH vs exhaustive synthetic contract failed"


if __name__ == "__main__":
    main()
