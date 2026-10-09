"""Self-contained HTML evidence explorer with safe JSON embedding."""

import json
from pathlib import Path

from .gates import verify_report
from .models import AuditReport


def render_report(report: AuditReport) -> str:
    """Embed report data without allowing record text to terminate a script tag."""
    verify_report(report)
    data = json.dumps(report.model_dump(), ensure_ascii=False)
    data = data.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    template = (Path(__file__).parent / "static" / "report.html").read_text()
    return template.replace("__AUDIT_DATA__", data)
