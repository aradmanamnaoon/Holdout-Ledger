# Verification record

## Independently inspectable hosted software checks

[GitHub Actions run 37960837739](https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/37960837739)
succeeded on October 9, 2026 at source commit
`6a432f805b913d393a1eb367ba7bb6a1bee090a5`.
Python 3.11, 3.12 and 3.13 jobs passed, and the Python 3.12 job log
states **45 passed in 2.82s** and **97.12% statement coverage**. Lint,
format, mypy, build, synthetic demo/repair, and jsdom/API dashboard
integration checks completed. Source coverage and controlled fixtures do
not establish detector accuracy on unseen datasets.

The jsdom test is not a full browser screenshot/layout, keyboard
accessibility, or manual UX audit. Docker execution, live Hugging Face
imports, and real participant datasets remain unverified. Hub imports
have mock-stream contract tests only.

## Benchmark evidence distinction

[Historical result-local.json](../benchmarks/result-local.json) reports
a single author-executed Python 3.12.14 benchmark (3,200 records,
200/200 **planted positives**, 6.90s wall-clock, and 47.3 MiB peak traced
Python allocations). **It had no clean negative test records.**
Consequently its zero false-positive count does not measure specificity;
its traced Python allocation is not full process RSS.

The revised [benchmark source](../benchmarks/benchmark.py) adds
prelabeled exact/near/group positives, disjoint and hard lexical negatives,
multiple seeds, TP/FP/FN/TN, denominator-checked metrics, and a
`--check` exit-code gate. The [GitHub workflow](../.github/workflows/ci.yml)
now contains separate LSH and exhaustive *synthetic* benchmark jobs and
JSON artifact upload. **New-job status: NOT VERIFIED in this document
until a current-branch hosted run has completed successfully.**
Do not reuse the October 9 run as if it had executed the new benchmark.

False-positive rate is reported only with an actual negative class.
The seeded runs do not sample real-world contamination distributions
or test semantic similarity, feature leakage, participant privacy,
downstream model performance, or clinical value.

## Reproducibility conditions

Pin the source SHA, runtime/version information, seed list, selected
`AuditConfig`, generated input hash and audit report hash. Compare
the same configuration on compatible environments; wall time and
Python allocation are workload- and machine-dependent. CI installs
the declared package extras, but it does not directly install the
checked-in `requirements-*.lock` files. A fully locked end-to-end
environment and independent scientific replication remain separate
future verification goals.
