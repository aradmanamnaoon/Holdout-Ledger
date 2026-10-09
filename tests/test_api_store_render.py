"""Persisted snapshot isolation, safe rendering, bounded bodies, and HTTP contracts."""

import asyncio
import threading
from pathlib import Path

import httpx
import pytest

from holdout_ledger.api import BodyLimit, create_app
from holdout_ledger.audit import audit
from holdout_ledger.demo import demo_records
from holdout_ledger.models import AuditConfig, Record
from holdout_ledger.render import render_report
from holdout_ledger.store import Store


def test_store_retention_and_parameterized_lookup(tmp_path: Path) -> None:
    store = Store(tmp_path / "audits.sqlite", retention=2)
    report = audit(demo_records())
    first = store.save(report)
    second = store.save(report)
    third = store.save(report)
    assert store.get(second) == report and store.get(third) == report
    with pytest.raises(KeyError):
        store.get(first)
    with pytest.raises(KeyError):
        store.get("' OR 1=1 --")
    assert len(store.list(limit=1)) == 1 and len(store.list(offset=1)) == 1
    with pytest.raises(ValueError):
        store.list(limit=0)
    with pytest.raises(ValueError):
        Store(tmp_path / "bad.sqlite", retention=0)


def test_render_escapes_record_script_tags_and_hides_text_by_default() -> None:
    attack = '</script><script>alert("x")</script>'
    rows = [Record(id="a", text=attack, split="train"), Record(id="b", text=attack, split="test")]
    html = render_report(audit(rows, AuditConfig(include_text=True)))
    assert attack not in html and "\\u003c/script\\u003e" in html
    assert attack not in render_report(audit(rows))


def test_api_workflow_and_authentication(tmp_path: Path) -> None:
    async def exercise():
        app = create_app(tmp_path / "db.sqlite", token="test-secret")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (await client.get("/health")).status_code == 200
            assert (await client.get("/")).status_code == 200
            assert (await client.get("/api/demo")).status_code == 401
            client.headers["Authorization"] = "Bearer test-secret"
            rows = (await client.get("/api/demo")).json()
            response = await client.post("/api/audits", json={"records": rows})
            assert response.status_code == 200
            key = response.json()["id"]
            assert (await client.get("/api/reports")).json()[0]["id"] == key
            assert (await client.get(f"/api/reports/{key}")).status_code == 200
            html = await client.get(f"/api/reports/{key}/html")
            assert (
                html.status_code == 200
                and "frame-ancestors" in html.headers["content-security-policy"]
            )
            assert len((await client.get(f"/api/reports/{key}/plan")).json()["removals"]) == 4
            delta = await client.post("/api/compare", json={"baseline_id": key, "current_id": key})
            assert not delta.json()["regression"]
            assert (await client.get("/api/reports/missing")).status_code == 404
            assert (await client.post("/api/audits", json={"records": []})).status_code == 422
            assert (
                await client.post("/api/audits", json={"records": [rows[0], rows[0]]})
            ).status_code == 422
            assert (await client.get("/api/reports?limit=0")).status_code == 422
            assert (
                await client.post("/api/audits", content=b"x" * (5 * 1024 * 1024 + 1))
            ).status_code == 413

    asyncio.run(exercise())


def test_capacity_rejection_releases_slot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real_audit = audit
    entered, release = threading.Event(), threading.Event()

    def waiting(rows, config):
        entered.set()
        release.wait(timeout=5)
        return real_audit(rows, config)

    monkeypatch.setattr("holdout_ledger.api.audit", waiting)

    async def exercise():
        app = create_app(tmp_path / "capacity.sqlite", concurrency=1)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            payload = {"records": [r.model_dump() for r in demo_records()]}
            first = asyncio.create_task(client.post("/api/audits", json=payload))
            assert await asyncio.to_thread(entered.wait, 2)
            try:
                assert (await client.post("/api/audits", json=payload)).status_code == 429
            finally:
                release.set()
            assert (await first).status_code == 200
            assert (await client.post("/api/audits", json=payload)).status_code == 200

    asyncio.run(exercise())


def test_chunked_request_limit_without_content_length() -> None:
    async def exercise():
        messages = iter(
            [
                {"type": "http.request", "body": b"123", "more_body": True},
                {"type": "http.request", "body": b"456", "more_body": False},
            ]
        )
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        async def endpoint(scope, receive, send):
            raise AssertionError("must not reach endpoint")

        await BodyLimit(endpoint, limit=5)({"type": "http", "method": "POST"}, receive, send)
        assert sent[0]["status"] == 413

    asyncio.run(exercise())
