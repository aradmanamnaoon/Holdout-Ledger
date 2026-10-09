# Launch drafts

Publish only after the public repository and its CI are verified. Replace the
URL with the actual published location. No posts have been sent.

## LinkedIn

A model's score can look solid while train and test share the same records or entity.

Finding overlap is only half the work. I also want evidence I can inspect, a repair I can review, and a test split that stays intact.

I built Holdout Ledger for that workflow.

It audits exact text, lexical near matches, and declared entity groups. A local dashboard shows the matching records. Each repair plan is bound to the source dataset, keeps every test record, and writes a separate output with provenance.

It also has offline reports, SQLite snapshots, and CI checks for new overlap.

The demo needs no API key or GPU. The Python suite has 45 passing tests. A seeded lexical benchmark found all 200 injected overlaps in 3,200 records; that does not establish recall on real data.

Repo: https://github.com/aradmanamnaoon/holdout-ledger

How do you check that your evaluation split is independent before trusting a score?

## X thread

1. A strong evaluation score is hard to trust when train and test share content or entities. I built Holdout Ledger to inspect those boundaries and review repairs while keeping the test split intact.

2. A duplicate count gives me little context. I need record IDs, split membership, match evidence, and a clear rule for what can change before retraining.

3. Holdout Ledger combines exact text, verified lexical near matches, and declared entity groups. It has a local evidence dashboard, offline HTML reports, and SQLite snapshots.

4. The demo uses 14 invented records. Load it, inspect a component, review the removal plan, and export separate split files. All test records stay. No model API or GPU is needed.

5. The useful lesson: clusters are transitive, and lexical matching misses semantic overlap. I report the detector's limits alongside evidence. The 200/200 synthetic result is a narrow benchmark, not a universal recall claim.

6. Try the demo and bring a small redacted case that the detector misses. Source and tests: https://github.com/aradmanamnaoon/holdout-ledger. What split-boundary check should every training pipeline include?

## 60-second video outline

- 0–10s: “Before I trust an evaluation score, I want to know whether train and test share records or the same entity.” Show two matching rows in different splits.
- 10–20s: “I built Holdout Ledger to inspect that evidence locally.” Load the 14-row synthetic demo and run the audit.
- 20–35s: Select a component. “These lines show the match witnesses. A cluster can connect through several records; it does not mean every pair is a match.” Show IDs and split labels.
- 35–48s: Open the repair plan. “The plan removes lower-priority split members, keeps every test record, and rejects a changed source dataset.” Show separate output and manifest.
- 48–55s: “It also has saved snapshots and CI checks. Lexical checks still miss semantic overlap.” Show the coverage note.
- 55–60s: “The demo needs no API key. Try it and tell me which split-boundary case I should test next.” Show the public repository URL after publication.
