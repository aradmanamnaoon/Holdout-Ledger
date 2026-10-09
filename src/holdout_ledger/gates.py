"""Absolute quality policies and ID-level audit regression checks."""

from .models import AuditReport, GatePolicy, GateResult, ReportDelta
from .text import digest


def verify_report(report: AuditReport) -> None:
    """Detect accidental report edits; this unkeyed checksum is not a signature."""
    payload = report.model_dump(exclude={"report_sha256"})
    if digest(payload) != report.report_sha256:
        raise ValueError("report checksum mismatch")


def gate(report: AuditReport, policy: GatePolicy | None = None) -> GateResult:
    verify_report(report)
    policy = policy or GatePolicy()
    measurements = {
        "cross_split_records": (report.summary.cross_split_records, policy.max_cross_split_records),
        "label_conflicts": (report.summary.label_conflicts, policy.max_label_conflicts),
        "blank_records": (len(report.summary.blank_record_ids), policy.max_blank_records),
    }
    violations = [
        f"{name}:{value}>{maximum}"
        for name, (value, maximum) in measurements.items()
        if value > maximum
    ]
    return GateResult(passed=not violations, violations=violations)


def compare(baseline: AuditReport, current: AuditReport) -> ReportDelta:
    """Compare the same detector contract; this is not an accuracy comparison."""
    verify_report(baseline)
    verify_report(current)
    if baseline.config != current.config or baseline.method != current.method:
        raise ValueError("reports use different detector configurations or modes")
    if baseline.environment != current.environment:
        raise ValueError("reports use different runtime versions")
    previous = set(baseline.summary.exposed_holdout_ids)
    present = set(current.summary.exposed_holdout_ids)
    new = sorted(present - previous)
    conflict_delta = current.summary.label_conflicts - baseline.summary.label_conflicts
    return ReportDelta(
        baseline_sha256=baseline.report_sha256,
        current_sha256=current.report_sha256,
        new_exposed_holdout_ids=new,
        resolved_holdout_ids=sorted(previous - present),
        record_delta=current.summary.records - baseline.summary.records,
        cross_split_record_delta=current.summary.cross_split_records
        - baseline.summary.cross_split_records,
        label_conflict_delta=conflict_delta,
        regression=bool(new or conflict_delta > 0),
    )
