# Independent leakage-evaluation protocol — READY FOR HUMAN ETHICS/RIGHTS REVIEW

Status: **research plan only**. No recruitment, human annotation, dataset transfer, IRB review, independent validation, or publication has occurred.

## Research question and estimands

How accurately does a declared lexical-and-group split auditor find **cross-split leakage candidates** in one independently sourced and lawfully reusable text dataset, compared with exact-only and group-only baselines? The primary unit is a *held-out record*; secondary unit is a *witness pair*. These units are correlated by source, subject and component. Report them separately.

The algorithm cannot detect all semantic, temporal, feature or preprocessing leakage. Do not label them as negatives in a semantic-leakage study merely because the model has no feature for them.

## Preconditions (must be checked before obtaining any records)

1. Select an appropriate public or specifically authorized nonclinical corpus with a clear license permitting evaluation, documentation and storage; verify revision, provenance, consent and permitted processing in a source-rights register. **No dataset selected or ingested at this stage**.
2. Exclude clinical/private patient data, identifiers, participant-level measurements and protected psychology responses unless a competent investigator has secured approval. A CC0 label alone does not establish de-identification or participant consent.
3. Have an external qualified domain reviewer and a second independent annotator accept a pre-registered protocol; record conflicts of interest and whether AI assisted the annotation preparation.
4. Freeze source revision/hash, sample sizes, audit configuration, detector version, primary estimand and exclusion rules before viewing held-out results. Never tune the decision threshold against the final evaluation set.

## Source and splits

Use the original publisher's train/test/subject/session split if available and predeclared. Derive group IDs from source-documented subject/session identifiers and report that mapping and its limitations. Do not expose raw group identifiers publicly; replace them with study-local pseudonyms if permissioned. Do not allow repeated subject sessions to cross evaluation boundaries for a subject-wise generalization task.

## Blind annotation

Make a stratified sample of detector-positive exact/near/group witness pairs **and** detector-negative candidate/record controls sampled independently of model outputs. Two independent human annotators label *evidence of source overlap* with categories: normalized-exact, lexical near, same declared participant/session, semantically similar but not lexically near, independent/non-overlapping, or uncertain. Separate objective matching from judgments about whether a given overlap invalidates the intended scientific estimand.

Provide a short rubric with counterexamples and an adjudication log. Both annotators should be blind to model flags and scores during first-pass labeling. Record raw annotations, abstentions and adjudicated labels; do not silently discard disagreement. Report inter-annotator agreement before adjudication; a Cohen kappa or Krippendorff alpha only where suitable for the label coding and sampling design.

## Analysis

- Predeclare primary **record-level** precision, recall, false-positive rate, confusion matrix and abstention policy; include true negatives from independently evaluated negative cases.
- Compare the same evaluated records with normalized-exact-only, group-only, union and Holdout Ledger (the exhaustive detector is an *algorithmic lexical comparator*, not a substitute for human ground truth).
- Report component-level errors separately from witness-pair errors, especially transitive false exposure and larger connected components.
- Quantify uncertainty with subject/source-cluster bootstrap or a predeclared cluster-robust method; do **not** treat repeated trials from a participant or multiple seeds of one synthetic generator as independent field observations.
- Report hard false-negative cases (paraphrases, script/Unicode variation, temporal/feature leakage), source distribution, group size, pre/post repair record counts, retained test records, and any subgroup-level attrition.
- Publish code, rights manifest, de-identified aggregate metrics and reviewer signoff if permitted; do not publish raw private participant records.

## Acceptance gates for a defensible claim

A manuscript or research-performance statement requires: independent annotator agreement; source and license proof; adequate hard-negative controls; suitable sample selection for the estimand; frozen split, seed and configuration; hosted reproducible logs; disclosed uncertainty; documented failures and comparison baselines. A 100% score on generated planted fixtures does not substitute for any of these.

Current status:
- Synthetic regression and same-input baseline checks: implemented and hosted in GitHub CI.
- Public, non-participant README descriptive probe: implemented and hosted.
- Human-annotated independent accuracy evaluation: **BLOCKED on lawful data selection, review and annotators**.
- Clinical participant research: **NOT AUTHORIZED / NOT PERFORMED**.
