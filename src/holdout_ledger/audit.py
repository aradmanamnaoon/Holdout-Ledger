"""Exact, near-text, entity-group, and label-consistency audit engine."""

import platform
from collections import Counter, defaultdict
from collections.abc import Iterable
from importlib.metadata import version
from itertools import combinations
from typing import Literal

from datasketch import MinHash, MinHashLSH

from .graph import Components
from .models import AuditConfig, AuditReport, Cluster, Conflict, Edge, Member, Record, Summary
from .text import dataset_digest, digest, jaccard, normalize, shingles, tokens


class AuditLimitError(ValueError):
    """A resource limit aborts the whole audit; no truncated report is returned."""


def audit(records: Iterable[Record], config: AuditConfig | None = None) -> AuditReport:
    """Build a witness graph and report; ingestion streams but the index is in memory."""
    config = config or AuditConfig()
    rows: list[Record] = []
    seen: set[str] = set()
    for candidate in records:
        row = Record.model_validate_json(candidate.model_dump_json())
        if row.id in seen:
            raise ValueError(f"duplicate record ID: {row.id}")
        if len(rows) >= config.max_records:
            raise AuditLimitError("max_records exceeded")
        seen.add(row.id)
        rows.append(row)
    if not rows:
        raise ValueError("dataset must contain at least one record")
    rows.sort(key=lambda r: r.id)
    by_id = {row.id: row for row in rows}
    normalized = {row.id: normalize(row.text, config.normalization) for row in rows}
    exact: dict[str, list[str]] = defaultdict(list)
    entities: dict[str, list[str]] = defaultdict(list)
    blank: list[str] = []
    short: list[str] = []
    for row in rows:
        if not normalized[row.id]:
            blank.append(row.id)
        else:
            exact[normalized[row.id]].append(row.id)
            if len(tokens(normalized[row.id])) < config.word_ngram:
                short.append(row.id)
        if row.group_id is not None:
            entities[row.group_id].append(row.id)
    graph = Components(by_id)
    edges: list[Edge] = []
    conflicts: list[Conflict] = []

    def connect(
        left: str, right: str, kind: Literal["exact", "near", "group"], score: float | None
    ) -> None:
        if len(edges) >= config.max_edges:
            raise AuditLimitError("max_edges exceeded")
        left, right = sorted((left, right))
        edges.append(
            Edge(
                left=left,
                right=right,
                kind=kind,
                score=score,
                cross_split=by_id[left].split != by_id[right].split,
            )
        )
        graph.union(left, right)

    for group in exact.values():
        for member in group[1:]:
            connect(group[0], member, "exact", 1.0)
        labels = sorted({label for key in group if (label := by_id[key].label) is not None})
        if len(labels) > 1:
            conflicts.append(Conflict(record_ids=group, labels=labels))
    for group in entities.values():
        for member in group[1:]:
            connect(group[0], member, "group", None)
    # One representative per exact-text group prevents quadratic duplicate cliques.
    representatives = sorted(group[0] for group in exact.values())
    sets = {key: shingles(normalized[key], config.word_ngram) for key in representatives}
    method: Literal["exhaustive", "lsh"] = "exhaustive"
    if config.mode == "lsh" or (
        config.mode == "auto" and len(representatives) > config.exhaustive_limit
    ):
        method = "lsh"
    if method == "exhaustive" and len(representatives) > config.exhaustive_limit:
        raise AuditLimitError("exhaustive_limit exceeded; select lsh or increase the limit")
    candidates = 0

    def verify(left: str, right: str) -> None:
        nonlocal candidates
        candidates += 1
        if candidates > config.max_candidates:
            raise AuditLimitError("max_candidates exceeded")
        score = jaccard(sets[left], sets[right])
        if score >= config.threshold:
            connect(left, right, "near", score)

    if method == "exhaustive":
        for left, right in combinations(representatives, 2):
            verify(left, right)
    else:
        index = MinHashLSH(threshold=config.candidate_threshold, num_perm=config.num_perm)
        for key in representatives:
            if not sets[key]:
                continue
            sketch = MinHash(num_perm=config.num_perm, seed=config.seed, scheme="affine32")
            sketch.update_batch([item.encode() for item in sorted(sets[key])])
            for other in sorted(index.query(sketch)):
                verify(other, key)
            index.insert(key, sketch)
    reasons: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        reasons[graph.find(edge.left)].add(edge.kind)
    clusters: list[Cluster] = []
    exposed: list[str] = []
    for group in graph.groups():
        if len(group) < 2:
            continue
        splits = {by_id[key].split for key in group}
        cross = len(splits) > 1
        clusters.append(
            Cluster(
                id=digest(group)[:16],
                members=[
                    Member(
                        id=key,
                        split=by_id[key].split,
                        label=by_id[key].label,
                        text_preview=by_id[key].text[:500] if config.include_text else None,
                    )
                    for key in group
                ],
                cross_split=cross,
                reasons=sorted(reasons[graph.find(group[0])]),
            )
        )
        # Train->validation/test and validation->test overlap both compromise holdouts.
        priority = {"train": 0, "validation": 1, "test": 2}
        lowest = min(priority[split] for split in splits)
        exposed.extend(key for key in group if priority[by_id[key].split] > lowest)
    split_counts: dict[str, int] = dict(sorted(Counter(row.split for row in rows).items()))
    holdouts = split_counts.get("validation", 0) + split_counts.get("test", 0)
    summary = Summary(
        records=len(rows),
        split_counts=split_counts,
        clusters=len(clusters),
        cross_split_clusters=sum(c.cross_split for c in clusters),
        cross_split_records=sum(len(c.members) for c in clusters if c.cross_split),
        exposed_holdout_ids=sorted(exposed),
        exposed_holdout_fraction=len(exposed) / holdouts if holdouts else 0.0,
        exact_edges=sum(e.kind == "exact" for e in edges),
        near_edges=sum(e.kind == "near" for e in edges),
        group_edges=sum(e.kind == "group" for e in edges),
        label_conflicts=len(conflicts),
        blank_record_ids=blank,
        short_record_ids=short,
        candidates_verified=candidates,
    )
    warnings = [
        "Lexical overlap and declared groups only; semantic, temporal, "
        "and feature leakage are not covered.",
        "Clusters include transitive matches; not every member pair "
        "has the reported near-match similarity.",
        "Entity groups must be meaningful evaluation units; a source website is often too broad.",
    ]
    if method == "lsh":
        warnings.append("LSH candidate retrieval is approximate and can miss near matches.")
    if blank:
        warnings.append("Blank texts are flagged, not treated as content duplicates.")
    payload = dict(
        schema_version=1,
        dataset_sha256=dataset_digest(rows),
        config=config.model_dump(),
        method=method,
        environment={
            "python": platform.python_version(),
            "datasketch": version("datasketch"),
            "holdout_ledger": "0.1.0",
        },
        summary=summary.model_dump(),
        edges=[e.model_dump() for e in edges],
        clusters=[c.model_dump() for c in clusters],
        label_conflicts=[c.model_dump() for c in conflicts],
        warnings=warnings,
    )
    return AuditReport.model_validate({**payload, "report_sha256": digest(payload)})
