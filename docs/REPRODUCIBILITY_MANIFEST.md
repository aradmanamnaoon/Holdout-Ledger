# Reproducibility and provenance manifest — verified on 2026-10-16

**This is a documentation manifest of an existing hosted run; GA-03B did not execute new project tests.**

## Identity and execution receipts

| Field | Evidence/setting |
|---|---|
| Repository | `aradmanamnaoon/Holdout-Ledger` |
| Immutable source commit | `cd37cf3505a351fca70843944fd453f7a39e91d7` |
| Package version at commit | `0.1.0` |
| CI run | https://github.com/aradmanamnaoon/Holdout-Ledger/actions/runs/38884482343 |
| CI trigger | Push, at same source commit (run created 2026-10-16T10:01:51Z) |
| CI overall state | Completed / SUCCESS (GitHub Actions API) |
| Test matrix | Ubuntu + Python 3.11, 3.12, 3.13; separate benchmark/evidence/dashboard jobs |
| Resolved Python in benchmark/evidence | CPython 3.12.15 in hosted logs |
| Source package | MIT-licensed `holdout-ledger` from repo; declared constraints in `pyproject.toml` |
| Environment pinning | Workflow uses `pip install -e .` or `-e '.[dev]'`, not a lockfile `pip install -r ...`; resolved dependency receipt uploaded with evidence artifact |
| Benchmark seeds | 42,43,44,45,46 (LSH); 42,43 (exhaustive) |
| Tags / releases | No GitHub releases in inspected API listing. A package version is not evidence of a release. |

## Hosted jobs — 6 / 6 successful

1. `tests (3.11)` — hosted job 116918791536, completed successfully.
2. `tests (3.12)` — hosted job 116918791403, completed successfully; log: **61 passed**, **97.12% statement coverage**, Ruff, format, mypy, source/wheel build and local synthetic demo/repair steps completed.
3. `tests (3.13)` — hosted job 116918791289, completed successfully.
4. `benchmark` — hosted job 116918791199, completed successfully; 5 LSH seeded synthetic fixtures and 2 exhaustive fixtures; artifact `12039395884`.
5. `evidence` — hosted job 116918791204, completed successfully; same-input synthetic baseline comparison and **pinned public OpenNeuro README-only** source probe; artifact `12038617304` includes resolved dependencies.
6. `dashboard` — hosted job 116918790917, completed successfully; tests of jsdom/live local API, not a manual accessibility or real-browser study.

## Test inventory and exact command contracts

Commands below are **already present in the checked-in hosted workflow**. They are recorded to make later replication possible, not a claim of execution in this mission.

```text
ruff check .
ruff format --check .
mypy src
pytest --cov=holdout_ledger --cov-fail-under=90 -q
python -m build
holdout-ledger demo --output-dir /tmp/ledger-demo
holdout-ledger apply /tmp/ledger-demo/records.jsonl --plan /tmp/ledger-demo/plan.json --output-dir /tmp/ledger-fixed
python benchmarks/benchmark.py --size 120 --injected 6 --negatives 20 --seeds 42,43,44,45,46 --mode lsh --check --output benchmark-lsh.json
python benchmarks/benchmark.py --size 80 --injected 4 --negatives 12 --seeds 42,43 --mode exhaustive --check --output benchmark-exhaustive.json
python -m benchmarks.baseline_comparison --size 80 --injected 4 --negatives 12 --seeds 42,43,44,45,46 --check --output baseline-comparison.json
python -m benchmarks.real_readme_probe --output real-readme-probe.json
npm ci
npm run test:ui
```

## Actual illustrative synthetic log excerpt

This table is a direct transcription of the current **hosted log values**, not fabricated sample data. Values are per fixture seed, **not** independently drawn human-subject observations.

| Workflow test | Seeds | TP | FP | FN | TN |
|---|---|---:|---:|---:|---:|
| Constructed LSH lexical/group controls | 42–46 (each) | 18 | 0 | 0 | 20 |
| Constructed exhaustive lexical/group controls | 42–43 (each) | 12 | 0 | 0 | 12 |

**Sample source receipt (LSH seed 42)**, from the hosted benchmark log: `dataset_sha256=e5c67f68a6e4c69f64966ad0f1327662727c7706de5505a5dc28e7e75e35ad66` and `report_sha256=545a86148d3b66b30efd9b91e483ffef0b84987ee9bf3d97facb941a2cdd32ea`. Input/report fingerprints are **not** software package hashes.

The artifact upload receipts include ZIP SHA256 `bfba278d5fa270415ff3b4db3726be7e36c0c4310c635a179188448fa4a2d688` for benchmark artifact `12039395884`, and `b0845dd4725ed6207a1f76024482c7501db7e47184e5c2423cb39e06a1de0c2f` for evidence artifact `12038617304`, as printed by GitHub Actions. These are **hosted uploader-reported digests**, not SHA256 recomputed independently by this mission.

## Not-yet-verified and portability gaps

- This mission did **not** download and independently hash the artifacts, nor rerun benchmarks/tests. GitHub Actions attachments can expire; archival is pending.
- Python environment dependency bounds are not the same as an installed, reproducible lock; `requirements-*.lock` exist but current CI uses declared extras and resolves dependencies dynamically.
- No blinded independent human annotation, source-domain confidence intervals, scientific field replication, or clinical performance exists in this evidence packet.
- Data license is separate from source code license. Public README snippets are not patient-level data.
- Any post-documentation commit changes the SHA, and the verification manifest should be updated with a fresh commit-matched run before release.