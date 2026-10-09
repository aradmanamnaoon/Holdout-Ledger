# Architecture

## Boundaries

| Module | Responsibility |
|---|---|
| models | Strict input and artifact schemas |
| text | Normalization, shingles, canonical hashes |
| graph | Deterministic union-find |
| audit | Witness detection, graph construction, metrics |
| gates | Checksum validation, policies, revision comparison |
| repair | Reviewed plan generation and separate-directory publication |
| io | Bounded JSONL/CSV and explicitly pinned Hub imports |
| store | SQLite snapshots, short-lived connections, retention |
| render | Safe, self-contained HTML embedding |
| api | Local HTTP service, body limits, authentication, audit capacity |
| cli | User-facing workflow and CI exit codes |

The engine imports no web framework and executes no remote model. API and CLI
share the same engine. The frontend uses plain HTML/JavaScript and no external
assets. A report can be opened offline.

## Reproducibility

Input rows are sorted by globally unique ID. Dictionaries use canonical JSON
encoding. Exact/group witnesses, LSH candidates, and component members have
deterministic order. MinHash uses an explicit seed and the datasketch 2.x
`affine32` scheme. Package and Python versions are included in the report hash.

Dataset fingerprints remain stable under record reordering, but change when any
source field changes. Report fingerprints identify the detector configuration
and environment as well. Two audits on different Python patch releases may
have different report hashes even when their findings are equivalent.

## Resource behavior

Exact/group preprocessing is linear in records and text volume. Exhaustive near
matching is quadratic in representative count and bounded by a configurable
limit. LSH indexing is approximate; dense buckets can still create quadratic
candidate growth. Candidate and edge limits fail the audit explicitly.

The engine holds source records and shingle sets in memory. It is designed for
bounded local audits, not distributed corpus deduplication. SQLite persists
completed reports, not an on-disk MinHash index.

The API executes CPU work in a thread pool and gates concurrent audits with a
semaphore. A rejected queue attempt returns 429. Thread execution improves event
loop responsiveness; it is not process isolation and does not eliminate GIL or
memory pressure. Protect shared deployment with token authentication and network
controls. The default CLI host and Compose binding are loopback.

## File safety

Artifact creation uses exclusive file creation. Repair stages a complete result
next to its output directory, reserves a new destination, and publishes the
directory with rename. Original records are never written. Failed staged writes
are cleaned up. A destination populated by another process is not overwritten.
Filesystems must support directory rename within the parent filesystem.
