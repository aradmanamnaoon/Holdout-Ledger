"""Audit, inspect, review, repair, compare, gate, import, and serve one workspace."""

import argparse
import json
import sys
from itertools import chain
from pathlib import Path

from .audit import audit
from .demo import demo_records
from .gates import compare, gate
from .io import load_json, read_records, stream_hf, write_records
from .models import AuditConfig, AuditReport, GatePolicy, RepairPlan
from .render import render_report
from .repair import apply_plan, make_plan


def write_text_new(path: Path, text: str) -> None:
    """Never silently overwrite a reviewed artifact."""
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text + "\n")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("audit", help="Audit canonical JSONL or CSV records")
    scan.add_argument("inputs", nargs="+", type=Path)
    scan.add_argument("--config", type=Path)
    scan.add_argument("--output", type=Path, required=True)
    scan.add_argument("--html", type=Path)
    inspect = sub.add_parser("inspect", help="Print the audit summary")
    inspect.add_argument("report", type=Path)
    plan = sub.add_parser("plan", help="Create a reviewable removal plan")
    plan.add_argument("report", type=Path)
    plan.add_argument("--output", type=Path, required=True)
    apply = sub.add_parser("apply", help="Apply a reviewed plan to a new output directory")
    apply.add_argument("inputs", nargs="+", type=Path)
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--output-dir", type=Path, required=True)
    check = sub.add_parser("gate", help="Fail CI when an absolute audit policy is exceeded")
    check.add_argument("report", type=Path)
    check.add_argument("--policy", type=Path)
    diff = sub.add_parser("compare", help="Detect new ID-level holdout exposure")
    diff.add_argument("baseline", type=Path)
    diff.add_argument("current", type=Path)
    demo = sub.add_parser("demo", help="Create synthetic data, reports, and a repair plan")
    demo.add_argument("--output-dir", type=Path, default=Path("demo-output"))
    serve = sub.add_parser("serve", help="Run the local audit workbench")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--database", type=Path, default=Path(".ledger/audits.sqlite3"))
    hf = sub.add_parser("import-hf", help="Import a bounded sample from a pinned Hub revision")
    hf.add_argument("dataset")
    hf.add_argument("--revision", required=True)
    hf.add_argument("--source-split", required=True)
    hf.add_argument("--split", choices=["train", "validation", "test"], required=True)
    hf.add_argument("--text-column", required=True)
    hf.add_argument("--group-column")
    hf.add_argument("--label-column")
    hf.add_argument("--subset")
    hf.add_argument("--limit", type=int, required=True)
    hf.add_argument("--output", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    """Exit 0 on success, 1 on a policy/regression failure, 2 on invalid input."""
    arguments = parser().parse_args(argv)
    try:
        command = arguments.command
        if command == "audit":
            config = (
                AuditConfig.model_validate(load_json(arguments.config))
                if arguments.config
                else AuditConfig()
            )
            report = audit(chain.from_iterable(read_records(p) for p in arguments.inputs), config)
            write_text_new(arguments.output, report.model_dump_json(indent=2))
            if arguments.html:
                write_text_new(arguments.html, render_report(report))
            print(report.summary.model_dump_json(indent=2))
        elif command in {"inspect", "plan", "gate"}:
            report = AuditReport.model_validate(load_json(arguments.report))
            if command == "inspect":
                from .gates import verify_report

                verify_report(report)
                print(report.summary.model_dump_json(indent=2))
            elif command == "plan":
                write_text_new(arguments.output, make_plan(report).model_dump_json(indent=2))
            else:
                policy = (
                    GatePolicy.model_validate(load_json(arguments.policy))
                    if arguments.policy
                    else GatePolicy()
                )
                result = gate(report, policy)
                print(result.model_dump_json(indent=2))
                return 0 if result.passed else 1
        elif command == "apply":
            rows = list(chain.from_iterable(read_records(p) for p in arguments.inputs))
            plan = RepairPlan.model_validate(load_json(arguments.plan))
            print(json.dumps(apply_plan(rows, plan, arguments.output_dir), indent=2))
        elif command == "compare":
            delta = compare(
                AuditReport.model_validate(load_json(arguments.baseline)),
                AuditReport.model_validate(load_json(arguments.current)),
            )
            print(delta.model_dump_json(indent=2))
            return 1 if delta.regression else 0
        elif command == "demo":
            arguments.output_dir.mkdir(parents=True, exist_ok=False)
            rows = demo_records()
            report = audit(rows, AuditConfig(include_text=True))
            write_records(arguments.output_dir / "records.jsonl", rows)
            write_text_new(arguments.output_dir / "audit.json", report.model_dump_json(indent=2))
            write_text_new(arguments.output_dir / "audit.html", render_report(report))
            write_text_new(
                arguments.output_dir / "plan.json", make_plan(report).model_dump_json(indent=2)
            )
            print(f"Created {arguments.output_dir}; review audit.html and plan.json before repair.")
        elif command == "import-hf":
            write_records(
                arguments.output,
                stream_hf(
                    arguments.dataset,
                    arguments.revision,
                    arguments.source_split,
                    arguments.split,
                    arguments.text_column,
                    arguments.limit,
                    arguments.subset,
                    arguments.group_column,
                    arguments.label_column,
                ),
            )
        elif command == "serve":
            import uvicorn

            from .api import create_app

            uvicorn.run(create_app(arguments.database), host=arguments.host, port=arguments.port)
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
