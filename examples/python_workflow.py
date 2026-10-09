"""Use the same engine from a data preparation or training pipeline."""

from holdout_ledger import AuditConfig, audit, make_plan
from holdout_ledger.demo import demo_records
from holdout_ledger.gates import gate


def main() -> None:
    report = audit(demo_records(), AuditConfig())
    print(report.summary.model_dump_json(indent=2))
    print(gate(report).model_dump_json(indent=2))
    plan = make_plan(report)
    print("Review these removals:", [r.record_id for r in plan.removals])


if __name__ == "__main__":
    main()
