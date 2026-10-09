# Verification record

Local verification used Python 3.12.14. The 45 Python tests passed with 97.12%
statement coverage. Ruff lint and formatting and strict mypy checks passed.
The audit engine had 100% statement coverage; coverage does not establish
detector accuracy on unseen data.

The optional Node 24/jsdom integration check passed against the live local API.
It loaded the synthetic records, submitted an audit, persisted a snapshot,
rendered result statistics, inspected four cross-split components, constructed
an SVG witness graph, and displayed member records without JavaScript errors.
It does not test browser layout, keyboard accessibility, or screenshots. A
Chromium download failed in this environment, so those checks remain unverified.

The seeded benchmark audited 3,200 records in approximately 6.90 seconds, with
47.3 MiB peak traced Python allocations. Native allocations and total RSS are
not included. All 200 deliberately injected exact/one-token overlaps were found
and no other holdout IDs were exposed. This limited synthetic experiment does
not establish real-world recall or semantic contamination coverage.

Wheel and source distributions are built locally; wheel smoke verification
checks packaged static assets, typed-package metadata, and the CLI demo.
GitHub CI is configured for Python 3.11–3.13 and the dashboard workflow. It has
not run until the new repository is published. Docker execution and live Hub
dataset downloads have not been verified here. The HF adapter uses controlled
stream contract tests.
