"""MCP server (stdio) for the schema playground. Every tool goes through schema_core.

Write tools are the §6 operations (plus alter_table for layer/grain/description). Each takes
expected_version (from get_schema_summary or the last write), reason and dry_run.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from mcp.server.mcpserver import MCPServer

from schema_core import query
from schema_core.conflicts import list_conflicts as _conflicts
from schema_core.export import export_bigquery as _export, parse_check
from schema_core.operations import OpError
from schema_core.store import SchemaStore, VersionConflict
from schema_core.validation import validate as _validate

ACTOR = "claude"

mcp = MCPServer(
    name="schema-playground",
    instructions=(
        "Reads and edits the Allshares CDP BigQuery star schema (schema/schema.json). "
        "Call get_schema_summary first: it returns the current version. Every write tool needs "
        "expected_version and a short reason; use dry_run=true to preview the diff. A stale version is "
        "rejected: re-read and retry. Columns linked to a catalogue field (field_id) inherit lineage and checks."
    ),
)


def _store() -> SchemaStore:
    return SchemaStore()


def _schema():
    return _store().load()


def _write(ops: list[dict[str, Any]], expected_version: str, reason: str, dry_run: bool) -> dict[str, Any]:
    try:
        res = _store().apply(ops, expected_version=expected_version, actor=ACTOR, reason=reason, dry_run=dry_run)
    except VersionConflict as e:
        return {"ok": False, "error": "version_conflict", "message": str(e), "current_version": e.actual}
    except (OpError, ValueError) as e:
        return {"ok": False, "error": "invalid", "message": str(e)}
    out = res.to_dict()
    out["warnings"] = [w["message"] for w in out["warnings"]][:20]
    if len(out["diff"]) > 60:
        out["diff_truncated"] = len(out["diff"])
        out["diff"] = out["diff"][:60]
    return out


def _guard(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except KeyError as e:
        return {"error": str(e).strip("'\"")}


# ============================================================================ read tools

@mcp.tool()
def get_schema_summary() -> dict:
    """Tables by layer with grain, primary key and FK counts, catalogue counts and the current version."""
    s, v = _schema()
    return query.schema_summary(s, v)


@mcp.tool()
def list_tables(layer: Optional[str] = None) -> dict:
    """List tables (optionally one layer: ref, catalogue, provenance, dim, fact, child, bridge)."""
    s, v = _schema()
    return {"version": v, "tables": [query.table_summary(s, t) for t in s.tables if not layer or t.layer == layer]}


@mcp.tool()
def get_table(name: str) -> dict:
    """One table: columns (type, mode, field link, CDP alias, lineage, checks), keys, partitioning, FKs."""
    s, v = _schema()
    return {"version": v, **_guard(query.get_table, s, name)}


@mcp.tool()
def search(q: str) -> dict:
    """Search tables, columns, catalogue fields and checks by name, description, CDP alias or protocol ID."""
    s, _ = _schema()
    return {"hits": query.search(s, q)}


@mcp.tool()
def get_field(name: str) -> dict:
    """A catalogue field: attributes, where it is placed (table.column) and the checks that apply."""
    s, _ = _schema()
    return _guard(query.get_field, s, name)


@mcp.tool()
def checks_for_column(table: str, column: str) -> dict:
    """Checks that apply to a column (derived from its field link)."""
    s, _ = _schema()
    return _guard(query.checks_for_column, s, table, column)


@mcp.tool()
def columns_for_check(code: str) -> dict:
    """Fields and table columns a check applies to, plus Conor's rules that hang off it."""
    s, _ = _schema()
    return _guard(query.columns_for_check, s, code)


@mcp.tool()
def list_ref_values(table: str) -> dict:
    """Seed rows of a ref table (code, label, meaning, status, list_source, extras)."""
    s, _ = _schema()
    return _guard(query.list_ref_values, s, table)


@mcp.tool()
def list_conflicts() -> dict:
    """Known conflicts to resolve with the team (never resolved automatically)."""
    s, _ = _schema()
    return {"conflicts": _conflicts(s)}


@mcp.tool()
def validate() -> dict:
    """Run validation. Errors would block a save; warnings do not."""
    s, v = _schema()
    issues = _validate(s)
    return {"version": v, "errors": [i.model_dump(exclude_none=True) for i in issues if i.severity == "error"],
            "warnings": [i.model_dump(exclude_none=True) for i in issues if i.severity == "warning"]}


@mcp.tool()
def get_changelog(limit: int = 20) -> dict:
    """The most recent applied operations (timestamp, actor, op, args, reason)."""
    return {"entries": _store().changelog(limit)}


# ============================================================================ workflow tools

@mcp.tool()
def import_diff() -> dict:
    """Re-import diff: what changed in the workbooks vs schema.json, per item (added/changed/removed)."""
    from schema_core.importer.reimport import import_diff as _diff
    d = _diff(_store())
    return {"version": d["version"], "summary": d["summary"], "notices": d["notices"],
            "items": [{k: i[k] for k in ("id", "kind", "label", "changes", "app_owned", "applicable", "reason")} for i in d["items"]]}


@mcp.tool()
def apply_import_items(item_ids: list[str], expected_version: str, reason: str = "", dry_run: bool = False) -> dict:
    """Apply accepted import diff items by id. Removals are flagged only and cannot be applied."""
    from schema_core.importer.reimport import apply_import_items as _apply
    try:
        res = _apply(_store(), item_ids, expected_version, actor=ACTOR, reason=reason, dry_run=dry_run)
    except VersionConflict as e:
        return {"ok": False, "error": "version_conflict", "message": str(e), "current_version": e.actual}
    except (KeyError, ValueError) as e:
        return {"ok": False, "error": "invalid", "message": str(e)}
    return {**res.to_dict(), "diff": res.diff[:60]}


@mcp.tool()
def export_bigquery(table: Optional[str] = None, include_seeds: bool = True) -> dict:
    """The BigQuery script (or one table's part), checked with sqlglot. Uses project/dataset from settings."""
    st = _store()
    s, _ = st.load()
    cfg = st.read_settings()
    try:
        sql = _export(s, cfg["project"], cfg["dataset"], cfg.get("location"), table=table, include_seeds=include_seeds)
    except KeyError as e:
        return {"error": str(e)}
    return {"parse_check": parse_check(sql), "sql": sql}


# ============================================================================ write tools (§6)


@mcp.tool()
def add_table(name: str, layer: Literal["ref", "catalogue", "provenance", "dim", "fact", "child", "bridge"],
              expected_version: str, reason: str, description: str = "", grain: str = "",
              columns: Optional[list[dict]] = None, primary_key: Optional[list[str]] = None, dry_run: bool = False) -> dict:
    """Add a table. columns: [{name, type, mode, description, field_id}]; primary_key: ordered column names."""
    return _write([{"op": "add_table", "name": name, "layer": layer, "description": description, "grain": grain,
                    "columns": columns or [], "primary_key": primary_key or []}], expected_version, reason, dry_run)


@mcp.tool()
def alter_table(table: str, changes: dict, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Change a table's layer, description, grain or holds_fields."""
    return _write([{"op": "alter_table", "table": table, "changes": changes}], expected_version, reason, dry_run)


@mcp.tool()
def rename_table(table: str, new_name: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Rename a table (relationships follow)."""
    return _write([{"op": "rename_table", "table": table, "new_name": new_name}], expected_version, reason, dry_run)


@mcp.tool()
def delete_table(table: str, expected_version: str, reason: str, cascade: bool = False, dry_run: bool = False) -> dict:
    """Delete a table. Fails if a relationship references it, unless cascade=true."""
    return _write([{"op": "delete_table", "table": table, "cascade": cascade}], expected_version, reason, dry_run)


@mcp.tool()
def add_column(table: str, name: str, expected_version: str, reason: str, type: Optional[str] = None,
               mode: Literal["NULLABLE", "REQUIRED", "REPEATED"] = "NULLABLE", description: Optional[str] = None,
               field_id: Optional[str] = None, cdp_alias: Optional[str] = None, position: Optional[int] = None,
               dry_run: bool = False) -> dict:
    """Add a column. With field_id, the type defaults from the field's Format and lineage is copied."""
    op = {"op": "add_column", "table": table, "name": name, "type": type, "mode": mode, "description": description,
          "field_id": field_id, "cdp_alias": cdp_alias, "position": position}
    return _write([{k: v for k, v in op.items() if v is not None}], expected_version, reason, dry_run)


@mcp.tool()
def alter_column(table: str, column: str, changes: dict, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Change type, mode, description, cdp_alias, validation_rule ({kind: range|pattern, min, max, pattern}) or needs_confirmation."""
    return _write([{"op": "alter_column", "table": table, "column": column, "changes": changes}], expected_version, reason, dry_run)


@mcp.tool()
def rename_column(table: str, column: str, new_name: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Rename a column (keys, clustering and relationships follow)."""
    return _write([{"op": "rename_column", "table": table, "column": column, "new_name": new_name}], expected_version, reason, dry_run)


@mcp.tool()
def delete_column(table: str, column: str, expected_version: str, reason: str, cascade: bool = False, dry_run: bool = False) -> dict:
    """Delete a column. Fails if a relationship references it, unless cascade=true."""
    return _write([{"op": "delete_column", "table": table, "column": column, "cascade": cascade}], expected_version, reason, dry_run)


@mcp.tool()
def set_primary_key(table: str, columns: list[str], expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Set the (ordered, possibly composite) primary key. Its columns become REQUIRED."""
    return _write([{"op": "set_primary_key", "table": table, "columns": columns}], expected_version, reason, dry_run)


@mcp.tool()
def add_relationship(from_table: str, from_columns: list[str], to_table: str, expected_version: str, reason: str,
                     to_columns: Optional[list[str]] = None, cardinality: Literal["many_to_one", "one_to_one"] = "many_to_one",
                     name: Optional[str] = None, dry_run: bool = False) -> dict:
    """Add a foreign key. to_columns defaults to the target's full primary key."""
    op = {"op": "add_relationship", "from_table": from_table, "from_columns": from_columns, "to_table": to_table,
          "to_columns": to_columns, "cardinality": cardinality, "name": name}
    return _write([{k: v for k, v in op.items() if v is not None}], expected_version, reason, dry_run)


@mcp.tool()
def delete_relationship(name: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Delete a relationship by name."""
    return _write([{"op": "delete_relationship", "name": name}], expected_version, reason, dry_run)


@mcp.tool()
def set_partition(table: str, expected_version: str, reason: str, column: Optional[str] = None,
                  range_start: Optional[int] = None, range_end: Optional[int] = None, range_interval: int = 1,
                  dry_run: bool = False) -> dict:
    """Partition on a DATE/DATETIME/TIMESTAMP column, or INT64 with a range. column=null clears it."""
    op: dict[str, Any] = {"op": "set_partition", "table": table, "column": column}
    if range_start is not None and range_end is not None:
        op["range"] = {"start": range_start, "end": range_end, "interval": range_interval}
    return _write([op], expected_version, reason, dry_run)


@mcp.tool()
def set_clustering(table: str, columns: list[str], expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Set clustering columns (at most 4)."""
    return _write([{"op": "set_clustering", "table": table, "columns": columns}], expected_version, reason, dry_run)


@mcp.tool()
def link_column_field(table: str, column: str, expected_version: str, reason: str, field_name: Optional[str] = None,
                      dry_run: bool = False) -> dict:
    """Link a column to a catalogue field (copies lineage; checks follow). field_name=null unlinks."""
    return _write([{"op": "link_column_field", "table": table, "column": column, "field_name": field_name}], expected_version, reason, dry_run)


@mcp.tool()
def add_ref_value(table: str, code: str, expected_version: str, reason: str, label: Optional[str] = None,
                  meaning: Optional[str] = None, status: Optional[str] = None, list_source: Optional[str] = None,
                  extra: Optional[dict] = None, dry_run: bool = False) -> dict:
    """Add a value to a ref table."""
    op = {"op": "add_ref_value", "table": table, "code": code, "label": label, "meaning": meaning, "status": status,
          "list_source": list_source, "extra": extra or {}}
    return _write([{k: v for k, v in op.items() if v is not None}], expected_version, reason, dry_run)


@mcp.tool()
def update_ref_value(table: str, code: str, changes: dict, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Change label, meaning, status, list_source, extra (or code) of a ref value."""
    return _write([{"op": "update_ref_value", "table": table, "code": code, "changes": changes}], expected_version, reason, dry_run)


@mcp.tool()
def delete_ref_value(table: str, code: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Delete a ref value."""
    return _write([{"op": "delete_ref_value", "table": table, "code": code}], expected_version, reason, dry_run)


@mcp.tool()
def add_field(name: str, expected_version: str, reason: str, format: Optional[str] = None, description: Optional[str] = None,
              grain: Optional[str] = None, module: Optional[str] = None, data_category: Optional[str] = None,
              protocol_id: Optional[str] = None, cdp_column: Optional[str] = None,
              status: Literal["active", "new", "parked"] = "new", dry_run: bool = False) -> dict:
    """Add a catalogue field (it then shows in the field tray until placed in a table)."""
    f = {"name": name, "format": format, "description": description, "grain": grain, "module": module,
         "data_category": data_category, "protocol_id": protocol_id, "cdp_column": cdp_column, "status": status}
    return _write([{"op": "add_field", "field": {k: v for k, v in f.items() if v is not None}}], expected_version, reason, dry_run)


@mcp.tool()
def link_field_check(field_name: str, check_code: str, expected_version: str, reason: str,
                     pass_criteria: Optional[str] = None, fail_criteria: Optional[str] = None,
                     score: Optional[float] = None, weight: Optional[float] = None, dry_run: bool = False) -> dict:
    """Apply a check to a field."""
    op = {"op": "link_field_check", "field_name": field_name, "check_code": check_code, "pass_criteria": pass_criteria,
          "fail_criteria": fail_criteria, "score": score, "weight": weight}
    return _write([{k: v for k, v in op.items() if v is not None}], expected_version, reason, dry_run)


@mcp.tool()
def unlink_field_check(field_name: str, check_code: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Remove a check from a field."""
    return _write([{"op": "unlink_field_check", "field_name": field_name, "check_code": check_code}], expected_version, reason, dry_run)


@mcp.tool()
def set_view(name: str, source_table: str, group_by: list[str], columns: list[dict], expected_version: str, reason: str,
             description: str = "", dry_run: bool = False) -> dict:
    """Create or replace a derived view calculated from a (child) table, exported as CREATE OR REPLACE VIEW.
    columns: [{name, type, expression (BigQuery aggregate over source columns), description, field_id}].
    Example: controlling_owner = LOGICAL_OR(votes_pct >= 20) over company_holder grouped by company_id, fiscal_year."""
    return _write([{"op": "set_view", "name": name, "source_table": source_table, "group_by": group_by,
                    "columns": columns, "description": description}], expected_version, reason, dry_run)


@mcp.tool()
def delete_view(name: str, expected_version: str, reason: str, dry_run: bool = False) -> dict:
    """Delete a derived view."""
    return _write([{"op": "delete_view", "name": name}], expected_version, reason, dry_run)


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
