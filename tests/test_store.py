import json

import pytest

from schema_core.store import VersionConflict


def test_apply_writes_changelog_and_bumps_version(store):
    v0 = store.version()
    res = store.apply([{"op": "add_column", "table": "fact_pay_line", "name": "year_of_birth", "field_id": "year_of_birth"}],
                      expected_version=v0, actor="claude", reason="demo")
    assert res.ok and res.version != v0
    col = store.load()[0].table("fact_pay_line").column("year_of_birth")
    assert col.type == "INT64" and col.owner == "app"
    entry = store.changelog()[-1]
    assert entry["actor"] == "claude" and entry["op"] == "add_column" and entry["reason"] == "demo"
    assert entry["args"]["name"] == "year_of_birth" and entry["version_after"] == res.version
    assert any(c["path"].endswith("[year_of_birth]") and c["change"] == "added" for c in res.diff)


def test_stale_version_rejected(store):
    v0 = store.version()
    store.apply([{"op": "alter_column", "table": "dim_company", "column": "legal_name", "changes": {"description": "x"}}],
                expected_version=v0, actor="ui")
    with pytest.raises(VersionConflict):
        store.apply([{"op": "alter_column", "table": "dim_company", "column": "legal_name", "changes": {"description": "y"}}],
                    expected_version=v0, actor="claude")


def test_dry_run_returns_diff_without_saving(store):
    v0 = store.version()
    before = store.schema_path.read_text()
    n = len(store.changelog())
    res = store.apply([{"op": "rename_table", "table": "dim_company", "new_name": "dim_firm"}],
                      expected_version=v0, actor="ui", dry_run=True)
    assert res.ok and res.dry_run and res.diff
    assert store.schema_path.read_text() == before and len(store.changelog()) == n


def test_validation_error_blocks_save(store):
    v0 = store.version()
    res = store.apply([{"op": "alter_column", "table": "dim_company", "column": "company_id", "changes": {"type": "VARCHAR"}}],
                      expected_version=v0, actor="ui")
    assert not res.ok and res.errors[0]["code"] == "invalid_type"
    assert store.version() == v0


def test_operation_error_reported(store):
    res = store.apply([{"op": "delete_table", "table": "dim_company"}], expected_version=store.version(), actor="ui")
    assert not res.ok and "cascade" in res.message


def test_rename_column_updates_keys_and_relationships(store):
    res = store.apply([{"op": "rename_column", "table": "dim_company", "column": "company_id", "new_name": "cdp_company_id"}],
                      expected_version=store.version(), actor="ui")
    s = store.load()[0]
    assert res.ok and s.table("dim_company").primary_key == ["cdp_company_id"]
    assert s.relationships[0].to_columns == ["cdp_company_id"]


def test_file_carries_version_hash(store):
    data = json.loads(store.schema_path.read_text())
    assert data["version"] == store.version()


def test_set_pk_makes_required_and_relationship_defaults_to_pk(store):
    v = store.version()
    res = store.apply([
        {"op": "add_table", "name": "dim_person", "layer": "dim", "columns": [{"name": "person_id"}]},
        {"op": "set_primary_key", "table": "dim_person", "columns": ["person_id"]},
        {"op": "add_column", "table": "fact_pay_line", "name": "person_id"},
        {"op": "add_relationship", "from_table": "fact_pay_line", "from_columns": ["person_id"], "to_table": "dim_person"},
    ], expected_version=v, actor="ui", reason="add person")
    assert res.ok, res.errors
    s = store.load()[0]
    assert s.table("dim_person").column("person_id").mode == "REQUIRED"
    assert any(r.to_table == "dim_person" and r.to_columns == ["person_id"] for r in s.relationships)
