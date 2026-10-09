# API

Start with `holdout-ledger serve`. Open `/docs` for the generated OpenAPI schema.
Set `HOLDOUT_LEDGER_TOKEN` to require `Authorization: Bearer <token>` on `/api/*`.
The landing page and health endpoint contain no dataset content.

| Method | Route | Result |
|---|---|---|
| GET | /health | Service version and liveness |
| GET | / | Audit workbench |
| GET | /api/demo | Invented canonical records |
| POST | /api/audits | Saved snapshot ID, audit report, and removal plan |
| GET | /api/reports | Paginated snapshot summaries |
| GET | /api/reports/{id} | Checksummed report |
| GET | /api/reports/{id}/html | Offline-compatible evidence explorer |
| GET | /api/reports/{id}/plan | Reviewable removal plan |
| POST | /api/compare | ID-level changes between compatible snapshots |

Audit request:

```json
{
  "records": [
    {"id":"a","text":"The same document","split":"train"},
    {"id":"b","text":"The same document","split":"test"}
  ],
  "config": {"mode":"auto","threshold":0.8,"include_text":false}
}
```

Compare request uses `baseline_id` and `current_id`, returned by previous audits.
Body limit is 5 MiB even without Content-Length. Audits accept 1–5,000 records.
Unknown fields and malformed inputs return 422. Missing reports return 404;
missing authentication returns 401; exhausted audit capacity returns 429.

The API deliberately has no filesystem repair route. Repair is a CLI operation
over user-selected local files, after review. Clients cannot select server file
paths or submit executable code. Uploaded full records are processed in memory;
only the report is stored. Opt-in previews can expose text in stored reports.
