"""Preserve the highest-priority split in each cross-split component."""

import json
import os
import shutil
import tempfile
from pathlib import Path

from .audit import audit
from .gates import verify_report
from .io import write_records
from .models import AuditReport, Record, Removal, RepairPlan, Split
from .text import dataset_digest, digest

ORDER: dict[Split, int] = {"test": 0, "validation": 1, "train": 2}


def make_plan(report: AuditReport) -> RepairPlan:
    """Propose removals only; retain every record in each component's top split."""
    verify_report(report)
    removals: list[Removal] = []
    for cluster in report.clusters:
        if not cluster.cross_split:
            continue
        protected = min((member.split for member in cluster.members), key=ORDER.__getitem__)
        for member in cluster.members:
            if member.split != protected:
                removals.append(
                    Removal(
                        record_id=member.id,
                        cluster_id=cluster.id,
                        protected_split=protected,
                        reason=f"component overlaps protected {protected} split",
                    )
                )
    removals.sort(key=lambda r: r.record_id)
    return RepairPlan(
        dataset_sha256=report.dataset_sha256,
        report_sha256=report.report_sha256,
        config=report.config,
        removals=removals,
        original_records=report.summary.records,
        retained_records=report.summary.records - len(removals),
        preserved_test_records=report.summary.split_counts.get("test", 0),
        warnings=[
            "This plan preserves test records and component-priority validation records.",
            "Within-split duplicates and conflicting labels remain for human review.",
            "Transitive components can remove records without a direct match "
            "to the protected record.",
            "Repair changes the training population; retrain and evaluate "
            "before claiming improvement.",
        ],
    )


def apply_plan(records: list[Record], plan: RepairPlan, destination: Path) -> dict[str, object]:
    """Verify source and plan, then publish a new directory; never modify originals.

    Re-auditing intentionally rejects forged removals and detector/runtime drift.
    A retained unkeyed checksum detects edits, not malicious tampering.
    """
    if dataset_digest(records) != plan.dataset_sha256:
        raise ValueError("source fingerprint changed; regenerate and review the plan")
    fresh = audit(records, plan.config)
    expected = make_plan(fresh)
    if plan != expected:
        raise ValueError("plan does not match a fresh audit; detector or plan changed")
    removed = {item.record_id for item in plan.removals}
    retained = sorted(
        (record for record in records if record.id not in removed), key=lambda r: r.id
    )
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError("repair destination must not exist")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".holdout-ledger-", dir=destination.parent))
    reserved = False
    try:
        output_hashes: dict[str, str] = {}
        for split in ORDER:
            rows = [record for record in retained if record.split == split]
            path = staging / f"{split}.jsonl"
            write_records(path, rows)
            output_hashes[path.name] = digest([record.model_dump() for record in rows])
        manifest: dict[str, object] = {
            "schema_version": 1,
            "source_sha256": plan.dataset_sha256,
            "audit_sha256": plan.report_sha256,
            "retained_sha256": dataset_digest(retained),
            "removed_ids": sorted(removed),
            "retained_records": len(retained),
            "split_hashes": output_hashes,
        }
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (staging / "reviewed-plan.json").write_text(plan.model_dump_json(indent=2) + "\n")
        destination.mkdir()  # Reserve the name without overwriting any existing output.
        reserved = True
        os.replace(staging, destination)
        return manifest
    except BaseException:
        if reserved:
            try:
                destination.rmdir()  # Remove only an empty directory reserved by this call.
            except OSError:
                pass
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
