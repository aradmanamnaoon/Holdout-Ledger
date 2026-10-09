# Holdout Ledger specification

## Problem and user

Text duplicates, near-identical templates, and repeated entities across train,
validation, and test can make evaluation scores misleading. An overlap count
does not explain which records are connected or how to change training data
without changing the holdout. This project serves ML engineers and technical
founders who can inspect their own text dataset and declared entity identifiers.

## Core features

1. Audit normalized-exact text, lexical near matches, declared group overlap,
   and exact-text conflicting labels with explicit resource limits.
2. Inspect record IDs, splits, witnesses, and transitive components in a local
   dashboard or a self-contained offline HTML report.
3. Save immutable audit snapshots in SQLite and compare compatible revisions
   for newly exposed holdout IDs and label-conflict changes.
4. Generate a reviewed removal plan bound to source fields and configuration;
   preserve every test record and publish separate outputs with provenance.
5. Run CI policy gates and import an explicit bounded sample from a pinned
   Hugging Face dataset commit.

## Architecture and files

Pydantic contracts define records, reports, plans, and policies. The pure audit
engine normalizes and fingerprints records, creates exact/group witnesses,
retrieves exhaustive or MinHash LSH candidates, verifies lexical Jaccard scores,
and builds union-find components. CLI and FastAPI adapters reuse the same engine.
The API keeps snapshots in SQLite; the browser uses embedded HTML/CSS/JavaScript
without external assets. Repair is a local file operation, outside the API.

`src/holdout_ledger/` contains contracts, text utilities, graph/audit logic,
gates, repair, I/O, store, renderer, CLI, API, and static pages. `tests/` covers
core and adapter behavior. `examples/` supplies canonical records and policies.
`benchmarks/` records a seeded experiment. `docs/` explains methodology,
architecture, API, verification, research, and adoption. CI, packaging, Docker,
contribution templates, and MIT licensing complete the repository.

## Test strategy and success criteria

Use synthetic records with known overlaps and negative controls. Verify
determinism, normalization, label/group distinctions, transitive components,
exact verification of LSH matches, resource-limit aborts, stale/edited plan
rejection, holdout preservation, no-overwrite behavior, checksums, API body and
concurrency limits, and script-safe report embedding. Contract-test Hub imports
with controlled streams. Exercise the dashboard DOM against the live local API.

Success requires a no-key demo, a clean lint/type/test run with at least 90%
statement coverage, packaged static assets, repair outputs that retain all test
records, and measurable controlled benchmark results with stated limitations.
Twenty organic stars is an adoption target after publication; it is not a
correctness criterion or guaranteed outcome. Semantic, temporal, image, and
feature leakage detection are outside this version's scope.
