"""SQLite audit snapshots with a checksummed report and local retention limit."""

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .gates import verify_report
from .models import AuditReport


class Store:
    """Open one short-lived SQLite connection per operation; no shared cursors."""

    def __init__(self, path: Path, retention: int = 100) -> None:
        if retention < 1:
            raise ValueError("retention must be positive")
        self.path = path
        self.retention = retention
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS audits (id TEXT PRIMARY KEY, "
                "created TEXT NOT NULL, report TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10)

    def save(self, report: AuditReport) -> str:
        verify_report(report)
        key = uuid.uuid4().hex
        created = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO audits VALUES (?, ?, ?)", (key, created, report.model_dump_json())
            )
            connection.execute(
                "DELETE FROM audits WHERE id IN "
                "(SELECT id FROM audits ORDER BY created DESC, id DESC LIMIT -1 OFFSET ?)",
                (self.retention,),
            )
        return key

    def get(self, key: str) -> AuditReport:
        with self._connect() as connection:
            row = connection.execute("SELECT report FROM audits WHERE id = ?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        report = AuditReport.model_validate_json(row[0])
        verify_report(report)
        return report

    def list(self, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError("invalid pagination")
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id,created,report FROM audits "
                "ORDER BY created DESC,id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [
            {
                "id": row[0],
                "created": row[1],
                "summary": json.loads(row[2])["summary"],
                "dataset_sha256": json.loads(row[2])["dataset_sha256"],
            }
            for row in rows
        ]
