# Contributing

Install the package with `python -m pip install -e '.[dev]'`. Run Ruff, strict
mypy, and pytest before proposing a change. Avoid changing test fixtures to match
a broken detector. Include a minimal, synthetic counterexample for incorrect
findings or missed overlaps.

Good contributions include bounded ingest adapters, explicit normalization
policies, independently labeled detector fixtures, clearer evidence inspection,
and benchmarks with stated ground truth. Semantic detectors need a separate
coverage contract, a pinned model revision, calibrated thresholds, and measured
cost. Do not equate cosine similarity with verified duplicate identity.

Changes to record schemas, hashing, graph construction, or preservation policy
must include compatibility notes. Source fingerprints and reviewed repair plans
are part of the public contract. A change that invalidates old plans should be
explicit, not silently accepted.

Never submit private records, patient data, credentials, or full proprietary
corpora in an issue. Use invented or redacted records. Public issue templates
request a reproduction, exact configuration, and environment versions.
