# Methodology and interpretation

The question is narrow: do the available text records or declared entity groups
connect records assigned to different evaluation splits?

## What a finding means

An exact witness connects normalized-identical text. A near witness connects
text with verified token-shingle Jaccard similarity at or above the configured
threshold. A group witness connects records with the same non-null group ID.

Connected components combine these relations transitively. If A matches B and
B matches C, all three belong to one component even if A does not match C.
This is useful for conservative split-boundary repair. It is not a claim that
every component member is an interchangeable duplicate.

Witness counts are not the total number of duplicate pairs. Stars represent
exact and group equivalence classes with linear edges. One representative per
exact-text group participates in near-match search; the graph propagates the
relationship to its exact duplicates.

## Metrics

| Field | Definition |
|---|---|
| cross_split_records | Every record in a component containing multiple splits |
| exposed_holdout_ids | Validation/test members connected to a lower-priority split |
| exposed_holdout_fraction | Exposed IDs divided by all validation and test records; zero when no holdouts exist |
| label_conflicts | Normalized-exact text groups with more than one non-null label |
| candidates_verified | Near-search candidate pairs subjected to exact Jaccard verification |

Validation connected to test alone is not counted as exposed validation, but
test is exposed by that validation overlap. The component still contributes all
its members to `cross_split_records`. Threshold policies can be calibrated to
this conservative definition.

## Candidate recall and normalization

Exhaustive mode provides full pair coverage only for lexical Jaccard among the
available representative records. It does not cover hidden data or semantic
duplicates below the lexical threshold. LSH adds possible candidate-retrieval
false negatives. Every emitted near edge has an exact score, but that does not
make every overlap discoverable.

NFKC and casefold change compatibility and case distinctions. Persian mode also
folds Arabic variants and zero-width non-joiners. Review these choices for code,
identifiers, and domain-specific language. Punctuation is retained for exact
matching but tokenization treats punctuation as delimiters for near matching.
Blank records are flagged. Punctuation-only records do not create empty sketches.

Short texts use a complete short token sequence rather than an empty n-gram set.
This reduces accidental short-text collisions but does not provide robust
semantic similarity. Boilerplate can still produce lexical false positives.

## Repair is a change to the training population

A repair protects all records in each component's highest-priority split. Every
test record is retained. Validation members are retained unless their component
also contains test. Training members connected to a protected split are removed.

The input fingerprint covers IDs, original text, splits, labels, groups, and
metadata. Repair recomputes the audit and plan, checking the recorded environment
and report fingerprint. The output is a separate directory with a manifest.
Within-split duplication and label conflicts remain visible.

This is an explicit curation policy, not a universally optimal data selection
rule. It can remove useful training records or reduce subgroup coverage. Inspect
the plan, measure changed class/group distributions, retrain, and evaluate on a
predeclared holdout. Never select the similarity threshold by maximizing the
final test score. Do not report model-quality improvement from an audit alone.

## Benchmark scope

The included benchmark injects exact copies and one-token suffix mutations into
a seeded synthetic corpus. Report recall, false positives, and false negatives
for these known injections. Do not extrapolate the result to real corpora,
paraphrases, or a million-record workload. Tracemalloc reports Python allocations,
not full process RSS or peak native NumPy memory. Wall time is machine-specific
and includes tracing overhead.

To assess a real deployment, manually label a held-out sample of candidate and
non-candidate pairs, report candidate recall separately from verification quality,
and repeat with the exact versions and configuration intended for production.

## Labeled synthetic regression benchmark (v2)

The original single-seed positive-only benchmark had no clean test
records and could not estimate a false-positive rate. Its preserved
historical JSON is NOT evidence of specificity.

The new seeded fixture supplies three positive classes: normalized-exact
copies, high-Jaccard one-token near copies, and shared declared-group
records with otherwise unrelated text. It also supplies true negatives:
unrelated controls and deliberately below-threshold hard lexical
near-controls. Labels describe this **specific lexical and declared-group
contract**, not semantic ground truth in the real world.

Per-seed confusion counts are TP, FP, FN and TN over **only** the
explicitly labeled test set. Precision and recall use their ordinary
definitions; FPR is FP/(FP+TN) only if any negative examples exist.
Undefined denominators are represented as null, never coerced to 0.
Descriptive seed min/mean/max is not a confidence interval or an
empirical sampling distribution of actual users.

The `--check` option rejects missing planted positives and improperly
flagged planted negatives. The independent controls in
`tests/test_benchmark.py` ensure that an all-positive detector fails on
negative records and an all-negative detector fails on positives.
The exhaustive fixture on small inputs is a lexical oracle for the
declared threshold, **not** a semantic paraphrase oracle. LSH may still
miss candidates on other data or thresholds. No new results should
be presented without their hosted job logs and source SHA.

## Extension: baselines, error bars, and original-source probe

The [same-input baseline evaluation](../benchmarks/baseline_comparison.py)
uses identical predeclared fixture records across normalized-exact,
declared group-only, union, exhaustive lexical/group and MinHash LSH/group
detectors. The exhaustive lexical result is an *algorithmic reference*
and not independent reviewer ground truth.

The report captures five seed-specific confusion matrices, min/mean/max
per-seed recall and FPR, and 95% illustrative Wilson binomial intervals.
The independence assumptions behind a population confidence interval
do not hold when samples are repeatedly generated by one narrow recipe.
There are no licensed claims of real-world sensitivity, specificity or
independent sample uncertainty.

The [README-only real-source probe](../benchmarks/real_readme_probe.py)
uses CC0-labeled public neuroscience dataset *documentation* at immutable
source commits. It records aggregate overlap counts without external labels
or participant-level research data. Independent human labels, ethics/rights
clearance and real participant evaluation are **not supplied**. See
[the rights ledger](evaluation_rights_and_limits.md) and
[independent research protocol](independent_evaluation_protocol.md).
