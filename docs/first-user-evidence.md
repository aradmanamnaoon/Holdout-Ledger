# First-user feedback and evidence standard

This repository does **not** include usage telemetry. The project maintainer may track GitHub traffic, stars, forks, issues, and voluntary reports separately. Those are **different** measures and must not be added together as if they were users.

## A useful first run

1. A volunteer independently installs the local package and opens the synthetic HTML report or runs the synthetic dashboard audit.
2. They may optionally submit the [first-run feedback form](https://github.com/aradmanamnaoon/Holdout-Ledger/issues/new?template=first-run-feedback.yml).
3. Report the stage **as stated**; an installation failure is a prospect/attempt, not a completed demo.
4. Deduplicate self-reports by author and time window where possible. One issue from one account is at most one self-reported tester, not a verified unique installation. No silent collection or cross-platform identity matching.
5. Do not solicit testimonials from someone who has not tried the project or rewards for stars. A LinkedIn recommendation is a personal professional endorsement, not a substitute for user adoption.

## What can be counted

| Indicator | Evidence | Interpretation |
|---|---|---|
| Completed synthetic first run | Explicit voluntary report that the HTML report or dashboard audit was opened and evaluated | Self-reported engagement; count with caveat |
| Installation failure | Voluntary report of attempted installation | Onboarding friction, not an active user |
| GitHub stars | GitHub repository API snapshot and baseline | Interest, **not** users |
| GitHub visitors / clones | Authorized Insights traffic, dated unique counts if accessible | Traffic proxy, **not** independently verified users |
| Community replies | Source thread and timestamp | Engagement, **not** automatically adoption |
| LinkedIn recommendations | Author-visible native LinkedIn recommendation | A genuine recommendation only when actually received |

## Privacy boundary

Never ask people to upload real health records, unpublished data, copyrighted datasets, identifying group IDs, private environment paths, credentials, or confidential business files to an issue. Prefer fabricated minimal JSONL examples. Do not require email addresses or tracking pixels. Contributors can remain anonymous where the platform permits.

## Review cadence

Record the baseline before outreach, and each later observation with retrieval timestamp, source URL, metric definition, and limitations. Label missing analytics **unavailable**, not zero. In launch content, do not cite synthetic-control outcomes as general population sensitivity/specificity, or imply that an audit proves a model is clinically reliable.
