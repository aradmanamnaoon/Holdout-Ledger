# Launch kit — reviewed claims and drafts

**Status (2026-10-16): DRAFT ONLY — no outreach or submissions are evidenced here.**
Do not represent any draft as already published. Do not imply third-party
validation, real-user counts, increased model accuracy, medical deployment, or
independent adoption.

Project: https://github.com/aradmanamnaoon/Holdout-Ledger

## Who should try it

Engineers auditing text classification or NLP training/evaluation splits,
maintainers of evaluation datasets with declared subjects/sessions/doc families,
and reproducibility reviewers who need record-level explanations before changing
a split.

Core job: inspect available train/validation/test records for **normalized
exact text, lexical near-copy, and declared entity-group overlap**, obtain
witness-level evidence, and apply an explicitly reviewed repair while
retaining test members. This is not image-similarity detection, a semantic
paraphrase detector, or a substitute for subject-level study design.

Distinctive feature versus large-scale deduplication pipelines: a bounded,
local, auditable split-review workflow with transitive component inspection,
source-fingerprint-bound plans, and separate repaired output. Compare with
[DataTrove](https://github.com/huggingface/datatrove) and
[Data-Juicer](https://github.com/datajuicer/data-juicer) on actual use cases,
not generalized superiority claims.

## First-time-user call to action

Copyable tutorial: [first run](first-run.md)

```bash
git clone https://github.com/aradmanamnaoon/Holdout-Ledger.git
cd Holdout-Ledger
python -m pip install -e '.[dev]'
holdout-ledger demo --output-dir demo-output
```

Open `demo-output/audit.html` locally. No GPU or API key is needed for the
included synthetic example. Read [methodological limitations](methodology.md)
before interpreting a real audit.

## LinkedIn draft (requires author approval before publishing)

**Headline:** Can you explain why two records ended up on opposite sides of your test boundary?

High evaluation metrics do not mean much until we verify how data was split.

Holdout Ledger is an open-source, local Python workbench that makes three kinds
of overlap inspectable: normalized-exact text, verified lexical near matches,
and declared entity groups.

Rather than just returning a duplicate count, it shows match witnesses and
connected components. The workflow produces a reviewable, source-bound repair
plan and writes a separate dataset without modifying the original or deleting
test records.

There's a reproducible synthetic demo, an HTML evidence explorer, CLI tools,
and CI checks. No GPU or external model API is required for the demo.

Important limitation: this is a bounded text/group audit, **not** proof that
a real dataset is leakage-free; semantic paraphrases and hidden group
relationships can go undetected.

If you work with ML evaluation splits, I'd value a report on where the
installation steps are confusing or a *synthetic* counterexample the detector
misses.

Repo: https://github.com/aradmanamnaoon/Holdout-Ledger

## X thread draft (requires Postory item-specific approval)

1. Train/test overlap can distort ML evaluation. Holdout Ledger is a local,
   open-source workbench for text and declared-group split audits, with
   explainable witnesses and human-reviewable repair plans. No GPU or model
   API for the invented-data demo.

2. It checks normalized-exact text, verified lexical near matches, and
   declared groups. Transitive clusters need care: not every pair in a
   cluster must be a direct near-duplicate match.

3. It keeps test records when applying an explicitly reviewed repair, writes
   a separate dataset, and records provenance. A split audit is not a model
   re-evaluation, and cannot verify hidden or semantic overlap.

4. The first-run tutorial includes the synthetic dataset, local HTML report,
   CI checks, and a privacy-safe feedback path:
   https://github.com/aradmanamnaoon/Holdout-Ledger

## Dev.to technical article outline (draft; no API publishing established)

Title: **How a train/test split can leak even when record IDs are unique**

- Introduce normalized exact overlap, lexical near-copy and subject-group
  leakage with a two- to four-record invented example.
- Explain why duplicate counts differ from connected-component witnesses.
- Demonstrate `holdout-ledger demo --output-dir demo-output` and inspecting
  `audit.html`.
- Show how fingerprint-bound repair plans prevent applying stale reviews.
- Explain limitations and when to choose broader deduplication pipelines.
- Ask for independently reproducible synthetic counterexamples, not stars.

## Show HN candidate (human-submitted, only when ready)

Title: **Show HN: Holdout Ledger – a local workbench to inspect split leakage**

```
A small, local Python workbench for checking whether text or declared groups
cross train/validation/test splits. It produces witness-level evidence, a
human-reviewable repair plan, and a separate repaired output.

Try the synthetic example without an API key:
git clone https://github.com/aradmanamnaoon/Holdout-Ledger.git
cd Holdout-Ledger
python -m pip install -e '.[dev]'
holdout-ledger demo --output-dir demo-output

Then open demo-output/audit.html.

It detects lexical and declared-group overlap, not all possible leakage.
Feedback on missed synthetic cases, confusing witnesses, and first-run
friction would be particularly helpful.
```

Read [Show HN guidelines](https://news.ycombinator.com/showhn.html).
The human account holder should be genuinely familiar with the project and
available to answer technical questions; do not automate submissions or
solicit votes.

## Reddit candidate: share only in a moderator-approved venue

**Educational angle:** A reproducible three-part explanation of when
train/test duplicates are not simple exact matches, illustrated with
*invented* JSONL records and a screenshot of the local evidence explorer.

Post only where rules permit self-promotion, clearly disclose the project's
relationship to the author, and avoid linking or repeating the same text
across multiple communities.

## 60-second demonstration shot list

| Seconds | On-screen action | Spoken point |
|---|---|---|
| 0–10 | Two invented records assigned to train/test | A test score depends on an independent split |
| 10–20 | Launch demo and open report | Inspect a local synthetic audit without a model |
| 20–35 | Select a connected component and witness | Show which exact, near, or group evidence connects records |
| 35–48 | Open plan and show removal IDs | Human reviews changes; original input remains untouched |
| 48–55 | Show manifest and re-audit | Separate output documents what changed |
| 55–60 | Show GitHub repository | Try the example and share a synthetic missed case |

No recorded video, real dataset analysis, or reported user outcome is implied
by this script.

## Publication and evidence rules

- Confirm the target branch's current CI and actual first-run behavior.
- Obtain specific approval to post or send as the author from each account.
- Do not contact strangers in bulk; never offer incentives for stars.
- Record the precise URL, posting date, authentic replies, reproducible
  feedback and any independently evidenced usage.
- GitHub traffic or post views are **interest** metrics, not unique real users.
- LinkedIn recommendations should be requested from genuine past collaborators
  or clients only. Use LinkedIn's native recommendation request interface.
