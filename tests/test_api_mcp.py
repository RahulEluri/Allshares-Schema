"""UI (API) and MCP writes share one store: same changelog shape, same diff, stale versions rejected."""
import pytest
from fastapi.testclient import TestClient

import mcp_server.server as srv
from api.main import app
from schema_core.importer.draft import build_draft
from schema_core.importer.snapshot import build_snapshot
from schema_core.store import SchemaStore

SNAP = build_snapshot()


def _fresh(tmp_path, name):
    st = SchemaStore(tmp_path / name)
    st.initialize(build_draft(SNAP), actor="test", reason="init")
    return st


@pytest.fixture
def client(tmp_path):
    app.state.store = _fresh(tmp_path, "api")
    yield TestClient(app)
    del app.state.store


@pytest.fixture
def mcp_store(tmp_path, monkeypatch):
    st = _fresh(tmp_path, "mcp")
    monkeypatch.setattr(srv, "_store", lambda: st)
    return st


OP = {"op": "add_column", "table": "fact_pay_line", "name": "year_of_birth", "field_id": "year_of_birth"}


def test_ui_and_mcp_produce_same_diff_and_changelog(client, mcp_store):
    v = client.get("/api/state").json()["version"]
    ui = client.post("/api/ops", json={"ops": [OP], "expected_version": v, "reason": "demo"}).json()
    claude = srv.add_column(table="fact_pay_line", name="year_of_birth", field_id="year_of_birth",
                            expected_version=mcp_store.version(), reason="demo")
    assert ui["ok"] and claude["ok"]
    assert ui["diff"] == claude["diff"] and ui["version"] == claude["version"]
    a, b = app.state.store.changelog()[-1], mcp_store.changelog()[-1]
    strip = lambda e: {k: v for k, v in e.items() if k not in ("ts", "actor")}
    assert strip(a) == strip(b) and a["actor"] == "ui" and b["actor"] == "claude"
    col = mcp_store.load()[0].table("fact_pay_line").column("year_of_birth")
    assert col.type == "INT64" and col.field_id == "year_of_birth"


def test_stale_version_rejected_api_and_mcp(client, mcp_store):
    v = client.get("/api/state").json()["version"]
    client.post("/api/ops", json={"ops": [OP], "expected_version": v})
    r = client.post("/api/ops", json={"ops": [{**OP, "name": "x2"}], "expected_version": v})
    assert r.status_code == 409 and r.json()["error"] == "version_conflict"

    v2 = mcp_store.version()
    srv.rename_table(table="dim_source", new_name="dim_document", expected_version=v2, reason="r")
    out = srv.rename_table(table="dim_document", new_name="dim_source", expected_version=v2, reason="r")
    assert out["ok"] is False and out["error"] == "version_conflict"


def test_mcp_reads(mcp_store):
    f = srv.get_field("base_salary")
    assert f["placed_in"] == ["fact_pay_line.base_salary"]
    assert {"NUM-01", "NUM-12"} <= {c["code"] for c in f["checks"] if "code" in c}
    assert srv.columns_for_check("NUM-11")["rules"] == ["STI-1", "STI-2", "STI-3", "LTI-1"]
    assert srv.get_schema_summary()["fields"] == 71
    assert srv.export_bigquery(table="dim_company")["parse_check"]["ok"]
    assert srv.import_diff()["items"] == []
    assert any(h["kind"] == "column" and h["name"] == "dim_company.head_office_city" for h in srv.search("hq_city")["hits"])


def test_api_state_export_and_dry_run(client):
    s = client.get("/api/state").json()
    assert len(s["schema"]["tables"]) == 36 and s["conflicts"]
    e = client.get("/api/export").json()
    assert e["parse_check"]["ok"] and e["order"][0].startswith("ref_")
    r = client.post("/api/ops", json={"ops": [{"op": "delete_table", "table": "dim_company", "cascade": True}],
                                      "expected_version": s["version"], "dry_run": True}).json()
    assert r["ok"] and r["dry_run"] and client.get("/api/state").json()["version"] == s["version"]
