"""Detector contracts, deterministic witnesses, and declared coverage limits."""

import random

import pytest
from pydantic import ValidationError

from holdout_ledger.audit import AuditLimitError, audit
from holdout_ledger.demo import demo_records
from holdout_ledger.gates import gate, verify_report
from holdout_ledger.models import AuditConfig, GatePolicy, Record
from holdout_ledger.text import dataset_digest, jaccard, normalize, shingles


def row(key: str, text: str, split: str = "train", **extra: object) -> Record:
    return Record.model_validate(dict(id=key, text=text, split=split, **extra))


def test_demo_has_independent_failure_classes() -> None:
    report = audit(demo_records())
    assert report.summary.records == 14
    assert report.summary.cross_split_clusters == 4
    assert report.summary.cross_split_records == 8
    assert report.summary.exposed_holdout_ids == [
        "test-exact",
        "test-fa",
        "test-group",
        "validation-near",
    ]
    assert report.summary.label_conflicts == 1
    assert report.summary.blank_record_ids == ["train-blank"]
    assert not gate(report).passed
    verify_report(report)


def test_record_order_does_not_change_report() -> None:
    records = demo_records()
    baseline = audit(records)
    random.Random(27).shuffle(records)
    assert audit(records) == baseline
    assert all(member.text_preview is None for c in baseline.clusters for member in c.members)


def test_exact_edges_are_linear_not_duplicate_cliques() -> None:
    records = [
        row(str(i), "same normalized text", "test" if i % 2 else "train") for i in range(100)
    ]
    report = audit(records)
    assert len(report.edges) == 99 and len(report.clusters) == 1
    assert report.summary.exposed_holdout_fraction == 1.0
    assert report.summary.candidates_verified == 0


def test_transitive_component_is_explicit() -> None:
    records = [
        row("a", "one two", "train"),
        row("b", "one two three", "validation"),
        row("c", "two three", "test"),
    ]
    report = audit(records, AuditConfig(word_ngram=1, threshold=0.6))
    assert len(report.clusters) == 1 and len(report.edges) == 2
    assert not any(e.left == "a" and e.right == "c" for e in report.edges)
    assert "transitive" in " ".join(report.warnings)


def test_label_conflicts_apply_to_exact_text_not_entity_membership() -> None:
    report = audit(
        [
            row("a", "first", label="x", group_id="entity"),
            row("b", "second", "test", label="y", group_id="entity"),
        ]
    )
    assert report.summary.group_edges == 1 and report.summary.label_conflicts == 0


def test_blank_and_punctuation_records_do_not_match_by_empty_sketch() -> None:
    report = audit(
        [row("a", " "), row("b", "\n", "test"), row("c", "!!!"), row("d", "???", "test")],
        AuditConfig(mode="lsh"),
    )
    assert not report.edges
    assert report.summary.blank_record_ids == ["a", "b"]


def test_persian_normalization_is_opt_in() -> None:
    records = [row("a", "يادگيري ماشين"), row("b", "یادگیری ماشین", "test")]
    assert not audit(records).clusters
    assert audit(records, AuditConfig(normalization="persian")).summary.exact_edges == 1


@pytest.mark.parametrize("mode", ["exhaustive", "lsh"])
def test_verified_jaccard_not_only_candidate_score(mode: str) -> None:
    records = [
        row("a", "one two three four five six seven eight nine ten"),
        row("b", "one two three four five six seven eight nine eleven", "test"),
    ]
    report = audit(records, AuditConfig(mode=mode, word_ngram=1, threshold=0.8))
    assert len(report.edges) == 1
    assert report.edges[0].score == pytest.approx(9 / 11)


def test_auto_mode_switches_to_lsh() -> None:
    records = [row("a", "alpha beta gamma"), row("b", "different token sequence")]
    assert audit(records, AuditConfig(exhaustive_limit=1)).method == "lsh"


@pytest.mark.parametrize(
    "config",
    [
        {"max_records": 1},
        {"max_edges": 1},
        {"max_candidates": 1},
        {"mode": "exhaustive", "exhaustive_limit": 1},
    ],
)
def test_limits_abort_instead_of_truncating(config: dict[str, object]) -> None:
    records = [
        row("a", "same text"),
        row("b", "same text", "test"),
        row("c", "same text"),
        row("d", "different text"),
        row("e", "another text"),
    ]
    with pytest.raises(AuditLimitError):
        audit(records, AuditConfig.model_validate(config))


def test_invalid_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        audit([])
    with pytest.raises(ValueError, match="duplicate record ID"):
        audit([row("a", "text"), row("a", "other text")])
    with pytest.raises(ValidationError):
        row(" ", "text")
    with pytest.raises(ValidationError):
        AuditConfig(candidate_threshold=0.9, threshold=0.8)


def test_fingerprint_binds_metadata_split_label_and_original_text() -> None:
    record = row("a", "Text", metadata={"revision": "r1"})
    for change in [
        {"text": "text"},
        {"label": "x"},
        {"split": "test"},
        {"metadata": {"revision": "r2"}},
    ]:
        assert dataset_digest([record.model_copy(update=change)]) != dataset_digest([record])


def test_empty_jaccard_and_short_shingles() -> None:
    assert jaccard(set(), set()) == 0.0
    assert shingles("one two", 3) == {"one\x1ftwo"}
    assert normalize("  ＡＢＣ\nDEF ") == "abc def"


def test_policy_tolerances_and_text_opt_in() -> None:
    report = audit(demo_records(), AuditConfig(include_text=True))
    assert gate(
        report, GatePolicy(max_cross_split_records=8, max_label_conflicts=1, max_blank_records=1)
    ).passed
    assert any(m.text_preview for c in report.clusters for m in c.members)
