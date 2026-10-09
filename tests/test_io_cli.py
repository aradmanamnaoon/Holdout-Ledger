"""Bounded input, pinned imports, artifact protection, and complete CLI workflow."""

import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from holdout_ledger.cli import main
from holdout_ledger.demo import demo_records
from holdout_ledger.io import load_json, read_records, stream_hf, write_records
from holdout_ledger.models import Record


def test_failed_stream_removes_partial_file_and_preserves_existing(tmp_path: Path) -> None:
    def interrupted():
        yield demo_records()[0]
        raise ValueError("remote stream interrupted")

    output = tmp_path / "import.jsonl"
    with pytest.raises(ValueError, match="interrupted"):
        write_records(output, interrupted())
    assert not output.exists()
    output.write_text("existing data")
    with pytest.raises(FileExistsError):
        write_records(output, interrupted())
    assert output.read_text() == "existing data"


def test_jsonl_csv_roundtrip(tmp_path: Path) -> None:
    rows = demo_records()
    path = tmp_path / "data.jsonl"
    write_records(path, rows)
    assert list(read_records(path)) == rows
    csv_path = tmp_path / "data.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(Record.model_fields))
        writer.writeheader()
        for record in rows:
            payload = record.model_dump()
            payload["metadata"] = json.dumps(payload["metadata"])
            writer.writerow(payload)
    assert list(read_records(csv_path)) == rows


@pytest.mark.parametrize(
    "suffix,content",
    [
        (".txt", "no"),
        (".jsonl", "{broken}"),
        (".jsonl", "{}"),
        (".csv", "text,split\na,train"),
        (".csv", "id,text,split,unknown\na,b,train,c"),
        (".csv", "id,text,split\na,b"),
        (".csv", "id,text,split\na,b,train,extra"),
    ],
)
def test_invalid_records(tmp_path: Path, suffix: str, content: str) -> None:
    path = tmp_path / ("bad" + suffix)
    path.write_text(content)
    with pytest.raises(ValueError):
        list(read_records(path))


def test_oversized_line_and_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "big.jsonl"
    path.write_text("x" * 1_048_577)
    with pytest.raises(ValueError, match="1 MiB"):
        list(read_records(path))
    path.write_text("\n" + demo_records()[0].model_dump_json() + "\n\n")
    assert len(list(read_records(path))) == 1


def test_import_hf_requires_pinned_revision_and_explicit_limit() -> None:
    for revision, limit in [("main", 3), ("a" * 40, 0)]:
        with pytest.raises(ValueError):
            list(stream_hf("team/data", revision, "train", "train", "text", limit))


def test_hf_adapter_streams_only_requested_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    received = {}

    def loader(path, **kwargs):
        received.update(kwargs)
        return iter(
            [
                {"body": "first", "group": 1, "label": 0},
                {"body": "second", "group": 2, "label": 1},
                {"body": "never read"},
            ]
        )

    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(load_dataset=loader))
    rows = list(
        stream_hf(
            "team/data",
            "a" * 40,
            "validation",
            "test",
            "body",
            2,
            group_column="group",
            label_column="label",
        )
    )
    assert len(rows) == 2 and rows[0].group_id == "1" and rows[0].label == "0"
    assert rows[0].metadata["revision"] == "a" * 40
    assert received["streaming"] is True and received["revision"] == "a" * 40
    assert rows[0].split == "test"


def test_hf_short_dataset_and_invalid_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(load_dataset=lambda *a, **k: []))
    assert list(stream_hf("data", "a" * 40, "test", "test", "text", 2)) == []
    monkeypatch.setitem(
        sys.modules, "datasets", SimpleNamespace(load_dataset=lambda *a, **k: [{"text": 7}])
    )
    with pytest.raises(ValueError, match="must be text"):
        list(stream_hf("data", "a" * 40, "test", "test", "text", 2))


def test_cli_full_workflow_and_exit_codes(tmp_path: Path) -> None:
    demo = tmp_path / "demo"
    assert main(["demo", "--output-dir", str(demo)]) == 0
    report = demo / "audit.json"
    assert main(["inspect", str(report)]) == 0
    assert main(["gate", str(report)]) == 1
    assert main(["compare", str(report), str(report)]) == 0
    assert main(["plan", str(report), "--output", str(tmp_path / "plan.json")]) == 0
    assert (
        main(
            [
                "apply",
                str(demo / "records.jsonl"),
                "--plan",
                str(demo / "plan.json"),
                "--output-dir",
                str(tmp_path / "fixed"),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "audit",
                str(tmp_path / "fixed/train.jsonl"),
                str(tmp_path / "fixed/test.jsonl"),
                str(tmp_path / "fixed/validation.jsonl"),
                "--output",
                str(tmp_path / "fixed.json"),
                "--html",
                str(tmp_path / "fixed.html"),
            ]
        )
        == 0
    )
    assert main(["demo", "--output-dir", str(demo)]) == 2
    assert main(["plan", str(report), "--output", str(tmp_path / "plan.json")]) == 2
    assert (
        main(["audit", str(tmp_path / "missing.jsonl"), "--output", str(tmp_path / "bad.json")])
        == 2
    )
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps({"max_cross_split_records": 8, "max_label_conflicts": 1, "max_blank_records": 1})
    )
    assert main(["gate", str(report), "--policy", str(policy)]) == 0


def test_json_artifact_size_limit(tmp_path: Path) -> None:
    path = tmp_path / "huge.json"
    with path.open("wb") as handle:
        handle.truncate(51 * 1024 * 1024)
    with pytest.raises(ValueError, match="50 MiB"):
        load_json(path)
