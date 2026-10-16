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
JSON artifact upload. **New-job verified:** [GitHub Actions run 38864517618](https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/38864517618)
completed successfully on 2026-10-16 at source commit
`6b070153b92adef68874319ca22c14d0820d9a71`.
Its Python 3.11–3.13 and dashboard jobs passed; the 3.12 log reports
**55 passing tests and 97.12% statement coverage**. The separate
benchmark job passed five labeled LSH seed fixtures (18 TP, 20 TN,
0 FP, 0 FN per seed) and two small exhaustive fixtures (12 TP, 12 TN,
0 FP, 0 FN per seed). The [JSON benchmark artifact](https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/38864517618/artifacts/12029619273)
was uploaded successfully. These results establish only the deliberately
constructed fixture contract, not real-corpus detector accuracy.
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

## GA-02B baseline and real-source evidence (2026-10-16)

An expanded [hosted push workflow run 38866047011](https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/38866047011)
finished successfully on a code commit
`f2a2f4aedf9fb8cc257edbc957e6153f27206a73`.
All six jobs passed (Python 3.11, 3.12, 3.13, controlled benchmarks,
OpenNeuro evidence and dashboard). The Python 3.12 job log reports **61 passed**
and **97.12% statement coverage**. Later documentation-only additions and
an environment-receipt artifact change require their own current-head run.

The [captured baseline/README evidence artifact](https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/38865933203/artifacts/12031605486)
demonstrates five matched synthetic seeds: exact-only baseline 20 TP,
40 FN and 60 TN pooled, compared with the full lexical-plus-group detector
60 TP, 0 FN, 60 TN. This **does not** establish natural-dataset superiority
because the generator explicitly constructs exactly the failure types
the enhanced detector was built to catch. The exhaustive lexical oracle and
LSH detector agreed on the synthetic fixtures; no general LSH recall is proven.

The separate OpenNeuro README probe fetched two revision-pinned, public
CC0-labeled README files and audited 24 eligible paragraphs. It reported
one cross-source exact overlap cluster affecting two paragraphs, with no
cross-source lexical near edge. The source documents refer to related NIMH
resources; the split by source README is artificial, the pair is not a
clinically meaningful leakage adjudication, and real-world precision/recall
are **UNKNOWN**. No participant-level files were requested or uploaded.

[Rights and data/model audit](evaluation_rights_and_limits.md) and
[independent blind annotation protocol](independent_evaluation_protocol.md)
distinguish verified software tests, partially source-audited document text,
and still-unavailable human review.
