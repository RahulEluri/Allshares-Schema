"""FastAPI back end for the UI. All writes go through schema_core with actor 'ui'.

Run: uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from schema_core import query
from schema_core.conflicts import list_conflicts
from schema_core.export import bq_dry_run, export_bigquery, parse_check, table_order
from schema_core.operations import CORE_OPS
from schema_core.store import ROOT, SchemaStore, VersionConflict
from schema_core.validation import placed_fields, validate

ACTOR = "ui"
app = FastAPI(title="Schema Playground")


def store() -> SchemaStore:
    return app.state.store if hasattr(app.state, "store") else SchemaStore()


@app.exception_handler(VersionConflict)
async def _conflict(_: Request, e: VersionConflict):
    return JSONResponse(status_code=409, content={"ok": False, "error": "version_conflict", "message": str(e),
                                                  "current_version": e.actual})


class OpsBody(BaseModel):
    ops: list[dict[str, Any]]
    expected_version: str
    reason: str = ""
    dry_run: bool = False


class ImportApplyBody(BaseModel):
    item_ids: list[str]
    expected_version: str
    reason: str = ""
    dry_run: bool = False


@app.get("/api/state")
def state() -> dict[str, Any]:
    st = store()
    schema, version = st.load()
    issues = validate(schema)
    return {
        "version": version,
        "schema": schema.model_dump(mode="json", exclude_none=True),
        "layout": st.read_layout(),
        "settings": st.read_settings(),
        "issues": [i.model_dump() for i in issues],
        "conflicts": list_conflicts(schema),
        "column_checks": query.column_checks_map(schema),
        "placed": placed_fields(schema),
        "core_ops": CORE_OPS,
    }


@app.post("/api/ops")
def apply_ops(body: OpsBody) -> dict[str, Any]:
    try:
        res = store().apply(body.ops, expected_version=body.expected_version, actor=ACTOR, reason=body.reason,
                            dry_run=body.dry_run)
    except ValueError as e:  # malformed operation payload
        raise HTTPException(status_code=422, detail=str(e))
    return res.to_dict()


@app.put("/api/layout")
def put_layout(layout: dict[str, Any]) -> dict[str, Any]:
    store().write_layout(layout)
    return {"ok": True}


@app.get("/api/settings")
def get_settings() -> dict[str, Any]:
    return store().read_settings()


@app.put("/api/settings")
def put_settings(settings: dict[str, Any]) -> dict[str, Any]:
    return store().write_settings(settings)


@app.get("/api/changelog")
def changelog(limit: int = 200) -> list[dict[str, Any]]:
    return list(reversed(store().changelog(limit)))


@app.get("/api/import/diff")
def get_import_diff() -> dict[str, Any]:
    from schema_core.importer.reimport import import_diff
    return import_diff(store())


@app.post("/api/import/apply")
def post_import_apply(body: ImportApplyBody) -> dict[str, Any]:
    from schema_core.importer.reimport import apply_import_items
    try:
        res = apply_import_items(store(), body.item_ids, body.expected_version, actor=ACTOR,
                                 reason=body.reason, dry_run=body.dry_run)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    return res.to_dict()


@app.get("/api/export")
def get_export(table: Optional[str] = None, include_seeds: bool = True, bq: bool = False) -> dict[str, Any]:
    st = store()
    schema, version = st.load()
    cfg = st.read_settings()
    try:
        sql = export_bigquery(schema, cfg["project"], cfg["dataset"], cfg.get("location"), table=table,
                              include_seeds=include_seeds)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    out = {"version": version, "sql": sql, "parse_check": parse_check(sql),
           "order": [t.name for t in table_order(schema)]}
    if bq:
        out["bq_dry_run"] = bq_dry_run(sql, cfg["project"])
    return out


@app.get("/api/search")
def get_search(q: str) -> list[dict[str, Any]]:
    schema, _ = store().load()
    return query.search(schema, q)


@app.get("/api/events")
async def events(request: Request):
    """Server-sent events: 'changed' with the new version whenever schema.json changes on disk."""
    from watchfiles import awatch

    st = store()
    stop = asyncio.Event()

    async def gen():
        last = st.version() if st.exists() else ""
        yield f"event: hello\ndata: {json.dumps({'version': last})}\n\n"
        watcher = awatch(st.dir, stop_event=stop, debounce=150, yield_on_timeout=True, rust_timeout=15000)
        try:
            async for changes in watcher:
                if await request.is_disconnected():
                    break
                if not changes:
                    yield ": keep-alive\n\n"
                    continue
                if not any(Path(p).name == "schema.json" for _, p in changes):
                    continue
                try:
                    v = st.version()
                except Exception:
                    continue  # mid-write; the next event will carry it
                if v != last:
                    last = v
                    yield f"event: changed\ndata: {json.dumps({'version': v})}\n\n"
        finally:
            stop.set()

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Serve the built UI (web/dist) when present, so one process runs everything.
_dist = ROOT / "web" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=_dist, html=True), name="web")
