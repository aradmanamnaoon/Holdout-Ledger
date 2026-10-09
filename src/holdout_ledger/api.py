"""Bounded local dashboard API; file paths and Python imports are not client inputs."""

import asyncio
import hmac
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import Field
from starlette.concurrency import run_in_threadpool
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .audit import AuditLimitError, audit
from .demo import demo_records
from .gates import compare
from .models import AuditConfig, Contract, Record
from .render import render_report
from .repair import make_plan
from .store import Store


class BodyLimit:
    """Enforce actual streamed bytes, including chunked bodies without Content-Length."""

    def __init__(self, app: ASGIApp, limit: int = 5 * 1024 * 1024) -> None:
        self.app, self.limit = app, limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.limit:
                await JSONResponse({"detail": "Request exceeds 5 MiB"}, status_code=413)(
                    scope, receive, send
                )
                return
            if not message.get("more_body", False):
                break
        sent = False

        async def replay() -> Message:
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


class AuditRequest(Contract):
    records: list[Record] = Field(min_length=1, max_length=5000)
    config: AuditConfig = Field(default_factory=AuditConfig)


class CompareRequest(Contract):
    baseline_id: str = Field(min_length=1, max_length=100)
    current_id: str = Field(min_length=1, max_length=100)


def create_app(
    database_path: Path | None = None, concurrency: int = 2, token: str | None = None
) -> FastAPI:
    """Serve a single local workspace; use authentication before shared deployment."""
    if concurrency < 1:
        raise ValueError("concurrency must be positive")
    path = database_path or Path(os.environ.get("HOLDOUT_LEDGER_DB", ".ledger/audits.sqlite3"))
    store = Store(path)
    semaphore = asyncio.Semaphore(concurrency)
    token = token if token is not None else os.environ.get("HOLDOUT_LEDGER_TOKEN")
    app = FastAPI(title="Holdout Ledger", version="0.1.0")
    app.add_middleware(BodyLimit)

    @app.middleware("http")
    async def protect(request: Request, call_next: Any) -> Any:
        if token and request.url.path.startswith("/api/"):
            provided = request.headers.get("authorization", "")
            if not hmac.compare_digest(provided, f"Bearer {token}"):
                return JSONResponse({"detail": "Authentication required"}, status_code=401)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; frame-ancestors 'none'"
        )
        return response

    def find(key: str) -> Any:
        try:
            return store.get(key)
        except KeyError as exc:
            raise HTTPException(404, "Report not found") from exc

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        return (Path(__file__).parent / "static" / "index.html").read_text()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/api/demo")
    def demo() -> list[Record]:
        return demo_records()

    @app.post("/api/audits")
    async def evaluate(payload: AuditRequest) -> dict[str, Any]:
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=0.1)
        except TimeoutError as exc:
            raise HTTPException(429, "Audit capacity reached; retry later") from exc
        try:
            report = await run_in_threadpool(audit, payload.records, payload.config)
            key = await run_in_threadpool(store.save, report)
            return {
                "id": key,
                "report": report.model_dump(),
                "plan": make_plan(report).model_dump(),
            }
        except AuditLimitError as exc:
            raise HTTPException(422, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        finally:
            semaphore.release()

    @app.get("/api/reports")
    def list_reports(
        limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)
    ) -> list[dict[str, Any]]:
        return store.list(limit, offset)

    @app.get("/api/reports/{key}")
    def get_report(key: str) -> Any:
        return find(key)

    @app.get("/api/reports/{key}/html", response_class=HTMLResponse)
    def html(key: str) -> str:
        return render_report(find(key))

    @app.get("/api/reports/{key}/plan")
    def plan(key: str) -> Any:
        return make_plan(find(key))

    @app.post("/api/compare")
    def delta(payload: CompareRequest) -> Any:
        try:
            return compare(find(payload.baseline_id), find(payload.current_id))
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    return app
