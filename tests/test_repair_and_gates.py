"""Holdout preservation, stale-plan rejection, and regression semantics."""

from pathlib import Path

import pytest

from holdout_ledger.audit import audit
from holdout_ledger.demo import demo_records
from holdout_ledger.gates import compare, gate, verify_report
from holdout_ledger.io import read_records
from holdout_ledger.models import AuditConfig, Record, Removal
from holdout_ledger.repair import apply_plan, make_plan


def test_repair_preserves_all_test_records_and_removes_boundary_overlap(tmp_path: Path) -> None:
    records = demo_records()
    plan = make_plan(audit(records))
    assert [r.record_id for r in plan.removals] == [
        "train-exact",
        "train-fa",
        "train-group",
        "train-near",
    ]
    original = {r.id: r.model_dump() for r in records if r.split == "test"}
    result = apply_plan(records, plan, tmp_path / "repaired")
    test = list(read_records(tmp_path / "repaired/test.jsonl"))
    assert {r.id: r.model_dump() for r in test} == original
    repaired = [
        r
        for split in ["train", "validation", "test"]
        for r in read_records(tmp_path / f"repaired/{split}.jsonl")
    ]
    assert audit(repaired).summary.cross_split_records == 0
    # Other issues remain visible rather than being silently "fixed".
    assert not gate(audit(repaired)).passed
    assert result["retained_records"] == 10


def test_preserves_highest_priority_validation_records(tmp_path: Path) -> None:
    records = [
        Record(id="a", text="same", split="train"),
        Record(id="b", text="same", split="validation"),
    ]
    plan = make_plan(audit(records))
    assert plan.removals[0].protected_split == "validation"
    apply_plan(records, plan, tmp_path / "out")
    assert list(read_records(tmp_path / "out/train.jsonl")) == []
    assert list(read_records(tmp_path / "out/validation.jsonl")) == [records[1]]


def test_stale_source_and_forged_plan_rejected(tmp_path: Path) -> None:
    records = demo_records()
    plan = make_plan(audit(records))
    changed = [
        r.model_copy(update={"text": "changed"}) if r.id == "test-exact" else r for r in records
    ]
    with pytest.raises(ValueError, match="fingerprint"):
        apply_plan(changed, plan, tmp_path / "stale")
    forged = plan.model_copy(
        update={
            "removals": [
                Removal(
                    record_id="test-exact", cluster_id="bad", protected_split="train", reason="bad"
                )
            ]
        }
    )
    with pytest.raises(ValueError, match="fresh audit"):
        apply_plan(records, forged, tmp_path / "forged")
    assert not (tmp_path / "forged").exists()


def test_existing_output_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "out"
    path.mkdir()
    (path / "important").write_text("keep")
    records = demo_records()
    with pytest.raises(FileExistsError):
        apply_plan(records, make_plan(audit(records)), path)
    assert (path / "important").read_text() == "keep"


def test_output_failure_cleans_owned_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(*args: object) -> None:
        raise OSError("simulated write failure")

    monkeypatch.setattr("holdout_ledger.repair.write_records", broken)
    rows = demo_records()
    with pytest.raises(OSError):
        apply_plan(rows, make_plan(audit(rows)), tmp_path / "out")
    assert list(tmp_path.iterdir()) == []


def test_report_checksum_detects_edits() -> None:
    report = audit(demo_records())
    modified = report.model_copy(update={"dataset_sha256": "changed"})
    for fn in [verify_report, make_plan, gate]:
        with pytest.raises(ValueError, match="checksum"):
            fn(modified)


def test_delta_uses_ids_and_rejects_detector_changes() -> None:
    rows = demo_records()
    clean = [
        r for r in rows if r.id not in {"train-exact", "train-fa", "train-group", "train-near"}
    ]
    baseline = audit(clean)
    current = audit(rows)
    delta = compare(baseline, current)
    assert delta.regression and len(delta.new_exposed_holdout_ids) == 4
    assert not compare(current, baseline).regression
    with pytest.raises(ValueError, match="configurations"):
        compare(current, audit(rows, AuditConfig(threshold=0.9)))
    alternate = current.model_copy(update={"environment": {"python": "other"}})
    from holdout_ledger.text import digest

    alternate = alternate.model_copy(
        update={"report_sha256": digest(alternate.model_dump(exclude={"report_sha256"}))}
    )
    with pytest.raises(ValueError, match="runtime"):
        compare(current, alternate)
