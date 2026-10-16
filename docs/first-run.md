# First run: inspect a split leak without your own data

**Audience:** ML engineers, NLP practitioners, and data stewards who need to
check whether accessible text examples or declared entity groups cross
train/validation/test boundaries.

This exercise uses **invented records only**. No GPU, account, model API,
patient data, or external dataset is necessary.

## 1. Clone and install

The package supports Python 3.11–3.13. Use an isolated environment:

```bash
git clone https://github.com/aradmanamnaoon/Holdout-Ledger.git
cd Holdout-Ledger
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
```

Editable installation is from this **repository**, not from PyPI.
If a dependency cannot be resolved, report your Python version and exact
error, without pasting sensitive environment variables.

## 2. Produce a fully local synthetic audit

```bash
holdout-ledger demo --output-dir demo-output
```

The output directory contains synthetic records, an audit and a proposed
repair plan. The offline HTML report is
`demo-output/audit.html` (open it in your browser). This command does not
prove any real dataset is contaminated.

Alternatively, run the dashboard:

```bash
holdout-ledger serve
```

Open `http://127.0.0.1:8000`; select **Load synthetic demo** and
**Run audit**. Do not expose the development server to untrusted networks.

## 3. Look for one explainable witness

In the report/explorer, inspect the split memberships of one connected
component and the individual witness relations. Check whether a link is
normalized-exact text, lexical near match, or a declared `group_id`.

A connected component is **transitive**: not every pair of records in
the component is necessarily a direct near match. A warning is evidence
to review, not proof of training leakage in an unseen model.

## 4. Review a proposed repair before applying it

```bash
holdout-ledger audit examples/records.jsonl \
  --config examples/audit_config.json --output audit.json --html audit.html
holdout-ledger plan audit.json --output review-plan.json
```

Inspect `review-plan.json` before proceeding:

```bash
holdout-ledger apply examples/records.jsonl \
  --plan review-plan.json --output-dir repaired-output
```

The original input is not overwritten. Existing output directories
cause a deliberate failure. The repair preserves test records, but
removal of training examples can change representativeness and class
balance. Re-audit repaired data and re-train/re-evaluate a model before
reporting an effect on model performance.

## 5. Run the project checks

```bash
ruff check .
ruff format --check .
mypy src
pytest --cov=holdout_ledger --cov-fail-under=90 -q
```

Passing a seeded synthetic test or benchmark does **not** establish
accuracy on a naturally occurring corpus. The detailed limitations are in
[methodology](methodology.md) and [verification](verification.md).

## 6. Evaluate the tool before using real data

- Are your `group_id` units subjects/sessions/document families rather
  than arbitrary broad collections?
- Are exact-text normalization and Jaccard shingling appropriate?
- Have you checked permissions, copyright, privacy and export boundaries?
- Would text previews or persistent reports expose confidential information?
- Have you kept test splits untouched and inspected any removed records?
- Will the detector miss semantic paraphrases or hidden overlap not in the data?

For restricted or medical content, start with a privacy-reviewed local setup
and avoid submitting patient or proprietary records to public issues.

## 7. Report a useful first-user experience

If you try this, please open a [GitHub issue](https://github.com/aradmanamnaoon/Holdout-Ledger/issues/new)
with your OS, Python version, synthetic steps to reproduce, expected versus
observed behavior, and whether the CLI/dashboard worked. **Do not upload
restricted data.** A reproducible counterexample is more helpful than an
unsupported accuracy claim.

See the [API guide](api.md) and [contributing guide](../CONTRIBUTING.md).
