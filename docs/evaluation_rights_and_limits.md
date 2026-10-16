# GA-02B — Data rights, independent-data boundary and evaluation integrity

Audit date: 2026-10-16. This file is an evidence ledger, not proof that the software is scientifically validated.

## Scope and claims

Holdout Ledger audits **lexical text overlap and caller-supplied groups**; it does not diagnose, model participants, identify subjects from text, detect semantic paraphrases, or train a predictive model. Source code is [MIT licensed](../LICENSE). No trained model or model weights are shipped, and there is no model-training dataset to license for the code's own operation. Imported user text retains its own license, consent, and privacy obligations.

### Data/source audit

| Source | Content accessed by the hosted experiment | Rights evidence | Permitted evaluation claim | What remains unverified |
|---|---|---|---|---|
| [Synthetic fixture](../benchmarks/benchmark.py) | Generated tokens and invented subject-like identifiers | Generated in repository; no external personal data | TP/FP/FN/TN for the predeclared generated detector contract | Population accuracy, domain adaptation, independent truth |
| [OpenNeuro ds004131 README](https://github.com/OpenNeuroDatasets/ds004131/blob/693ce9a1caf909c19ddf1d497e3bce805e78db60/README) | README markdown paragraphs only, pinned commit `693ce9a1caf909c19ddf1d497e3bce805e78db60` | README expressly says CC0 1.0; upstream `LICENSE` is a Git-annex link, and GitHub's license classifier reads NOASSERTION. Avoid redistributing text without resolving that ambiguity. | Descriptive lexical overlaps between public README excerpts | Legal review of downstream datasets; real participant rights |
| [OpenNeuro ds005752 README](https://github.com/OpenNeuroDatasets/ds005752/blob/f6c800b5f9fb5990683c86d278cb3e944c93f8b0/README) | README markdown paragraphs only, pinned commit `f6c800b5f9fb5990683c86d278cb3e944c93f8b0` | README states CC0 1.0; repository's actual LICENSE text is CC0 1.0 | Descriptive lexical overlaps, not validation against human annotations | Participant data not accessed; independent evaluation labels absent |

### Privacy and dataset discipline

1. No `participants.tsv`, `phenotype/*.tsv`, imaging files, assessments, genomic records, or participant-level records are read. A README may **describe** health research without itself containing research participant rows.
2. The hosted [real-README probe](../benchmarks/real_readme_probe.py) only requests the pinned public `README` path of the two repositories, checks the CC0 statement, and produces aggregate counts, SHA-256 input receipts, configuration and report fingerprints. It **does not commit or upload** the source paragraphs.
3. The probe's artificial split is **one source repository per split**. The two sources concern related NIMH resources, so they are neither independent real-world contamination cases nor independent proof of accuracy.
4. Full real participant datasets could require participant consent, permitted purpose, domain review, group identifiers, site/date splits, de-identification review, governance and license checks. This exercise deliberately does not import them.
5. A dataset labeled CC0 is not by itself a privacy or ethical authorization, and an unkeyed SHA-256 is not a digital signature or confidentiality protection.

## Comparison protocol

Run [baseline_comparison.py](../benchmarks/baseline_comparison.py) on **identical seeded inputs** for:
- Normalized-exact text match baseline: match train and test after the same declared normalization.
- Declared-group baseline: match exact non-null group ID across train and test.
- The union of those two baselines.
- Exhaustive lexical-and-group detector: a within-scope pairwise reference, **not an independent external annotation**.
- Approximate LSH-and-group detector: report overlap quality relative to the exhaustive lexical witness graph, including near-edge candidate recall.

The planted synthetic fixture has three equal positive classes and explicit negative cases. Report per-run confusion counts, seed-wise min/mean/max and illustrative Wilson binomial bounds. Because multiple seeds reuse the same generator/controlled distribution, observations are not independent population samples. **Wilson intervals are descriptive for these fixtures; they are NOT valid real-world uncertainty estimates.**

Fail closed on detector regressions, misclassified planted hard negatives, or missing expected lexical near edges. All baseline summaries are source-bound to a seed, dataset SHA, report SHA and exact configuration.

## What still requires humans or external parties

- **Independent human-annotated corpus:** permitted research dataset under reviewed rights, with ambiguous and near-duplicate/nonmatch pairs labeled by qualified evaluators blind to the model's outputs; an adjudication protocol and inter-rater agreement. **NOT OBTAINED**.
- **Participant-level validation:** an actual ethically authorized neuroscience/psychology dataset, documented participants/sessions/trials, subject-wise splits and privacy/legal review. **NOT PERFORMED**.
- **External replication and user adoption:** reproducible runs by a different lab/developer, usability feedback from real users, independent citations. **NOT CLAIMED**.
- **Predictive performance:** if later tested, predefined downstream ML tasks/splits, no threshold tuning on the final test set, baselines and uncertainty at subject level. **NOT RUN**.
- **Security:** SHA checksums detect edits but do not establish authorship or protect private participant inputs. **No public-data certification inferred**.

## Evidence interpretation

A fully green hosted CI run is strong evidence of **software test reproducibility**, not human-labeled real-world accuracy, publication, independent adoption or clinical use. The parent GA-02B audit and GA-01B flagship assessment should remain honest about these gaps.

Relevant methodological background: [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [datasketch LSH](https://ekzhu.com/datasketch/lsh.html), and [BIDS](https://bids.neuroimaging.io/) for future convention checks (no BIDS compliance claimed).
