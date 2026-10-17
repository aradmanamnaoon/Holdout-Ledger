# Data and model statement (research software; no model release)

## Artifact classification

This project distributes **software and reproducible synthetic/example workflows**, not a trained ML model or a curated human neuroscience dataset. This is a scope statement, not a claim of compliance with every dataset-card or model-card standard.

## Synthetic fixtures — dataset-card-style description

- **Intended use:** unit tests and bounded regression checks for the implemented split-overlap rules.
- **Source:** seeded, deliberately generated text records in `benchmarks/benchmark.py`, plus invented examples under `examples/`.
- **Content:** normalized-exact copies, high-Jaccard one-token variations, declared shared-group positives, disjoint negative controls, and below-threshold hard lexical negatives.
- **Labels:** constructed by generator with known membership; *not* independent annotator labels or meaningful psychology/neuroscience outcomes.
- **Evaluation:** five LSH seeds and two exhaustive seeds in current CI. Do not interpret as statistical power, confidence intervals, or estimates of real error prevalence.
- **Rights:** generator and example code fall under repository's stated MIT software license where owned by the repository owner; separately verify any incorporated third-party content or imported dataset licenses. No general redistribution permission follows from MIT source code alone.
- **Bias/limitations:** vocabulary, pattern choice, thresholds and group structure encode the algorithm's design assumptions. Excellent fixture results do not predict performance on unseen languages, datasets, subjects, clinical material or semantic paraphrases.
- **Privacy:** avoid real participant identifiers, patient files, and unpublished protected text in GitHub issues/artifacts.

## Observational public-document probe

`benchmarks/real_readme_probe.py` probes pinned public OpenNeuro README text (not participant files); it is a descriptive code-path check. Even when the source repository labels specific README files CC0, inspect source revision/license provenance before any redistribution or archiving of text. It does not establish a real research dataset's split leakage, human adjudication or diagnostic validity.

## Model card status

**No model weights, training procedure, model card, predictive outputs, model performance or clinical deployment are released.** A standard trained-model card is **not applicable**. If the software later integrates a learned semantic detector, require a separate model card with training-data rights, model revision, empirical calibration/thresholds, slice errors, privacy/security risks, maintenance ownership and externally reproducible evaluation.

## Existing canonical documentation — do not duplicate

- [`docs/methodology.md`](https://github.com/aradmanamnaoon/Holdout-Ledger/blob/cd37cf3505a351fca70843944fd453f7a39e91d7/docs/methodology.md)
- [`docs/evaluation_rights_and_limits.md`](https://github.com/aradmanamnaoon/Holdout-Ledger/blob/cd37cf3505a351fca70843944fd453f7a39e91d7/docs/evaluation_rights_and_limits.md)
- [`docs/independent_evaluation_protocol.md`](https://github.com/aradmanamnaoon/Holdout-Ledger/blob/cd37cf3505a351fca70843944fd453f7a39e91d7/docs/independent_evaluation_protocol.md)