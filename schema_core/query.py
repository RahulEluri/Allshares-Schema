"""Read-side helpers shared by the MCP server and the API (compact, structured results)."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional

from .models import Schema, Table
from .validation import placed_fields


def checks_for_field(schema: Schema, field_name: str) -> list[dict[str, Any]]:
    cat = schema.catalogue
    out = []
    for p in cat.field_checks:
        if p.field_name != field_name:
            continue
        c = cat.check(p.check_code)
        out.append({
            "code": p.check_code, "name": c.name if c else None, "type": c.check_type if c else None,
            "fx": c.check_fx if c else None, "status": c.status if c else None,
            "pass": p.pass_criteria, "fail": p.fail_criteria, "score": p.score, "weight": p.weight,
        })
    # Conor's rules attached to any of those gates.
    gates = {o["code"] for o in out}
    rules = [{"code": r.code, "name": r.name, "parent_gates": r.parent_gates, "status": r.status, "result_if_not": r.result_if_not}
             for r in cat.checks if r.kind == "rule" and set(r.parent_gates) & gates]
    return out + ([{"related_rules": rules}] if rules else [])


def column_checks_map(schema: Schema) -> dict[str, list[str]]:
    """'table.column' -> check codes (derived from the column's field link)."""
    by_field: dict[str, list[str]] = defaultdict(list)
    for p in schema.catalogue.field_checks:
        by_field[p.field_name].append(p.check_code)
    out = {}
    for t in schema.tables:
        for c in t.columns:
            if c.field_id and by_field.get(c.field_id):
                out[f"{t.name}.{c.name}"] = by_field[c.field_id]
    for v in schema.views:
        for dc in v.columns:
            if dc.field_id and by_field.get(dc.field_id):
                out[f"{v.name}.{dc.name}"] = by_field[dc.field_id]
    return out


def view_summary(v) -> dict[str, Any]:
    return {"name": v.name, "source_table": v.source_table, "group_by": v.group_by, "description": v.description,
            "columns": [c.model_dump(exclude_none=True) for c in v.columns]}


def table_summary(schema: Schema, t: Table) -> dict[str, Any]:
    fks_out = [r for r in schema.relationships if r.from_table == t.name]
    fks_in = [r for r in schema.relationships if r.to_table == t.name]
    return {"name": t.name, "layer": t.layer, "grain": t.grain, "pk": t.primary_key,
            "columns": len(t.columns), "fk_out": len(fks_out), "fk_in": len(fks_in),
            **({"rows": len(t.rows)} if t.layer == "ref" else {})}


def schema_summary(schema: Schema, version: str) -> dict[str, Any]:
    by_layer: dict[str, list] = defaultdict(list)
    for t in schema.tables:
        s = table_summary(schema, t)
        s.pop("layer")
        by_layer[t.layer].append(s)
    cat = schema.catalogue
    return {
        "version": version,
        "tables": len(schema.tables), "relationships": len(schema.relationships),
        "fields": len(cat.fields), "checks": len(cat.checks), "field_checks": len(cat.field_checks),
        "by_layer": dict(by_layer),
        "views": [{"name": v.name, "source_table": v.source_table, "group_by": v.group_by,
                   "columns": [c.name for c in v.columns]} for v in schema.views],
    }


def get_table(schema: Schema, name: str) -> dict[str, Any]:
    t = schema.table(name)
    if t is None and schema.view(name):
        return {"kind": "view", **view_summary(schema.view(name))}
    if t is None:
        raise KeyError(f"Table '{name}' does not exist")
    cmap = column_checks_map(schema)
    cols = []
    for c in t.columns:
        d = c.model_dump(mode="json", exclude_none=True, exclude={"owner"})
        if not d.get("needs_confirmation"):
            d.pop("needs_confirmation", None)
        if cmap.get(f"{t.name}.{c.name}"):
            d["checks"] = cmap[f"{t.name}.{c.name}"]
        cols.append(d)
    return {
        "name": t.name, "layer": t.layer, "grain": t.grain, "description": t.description, "owner": t.owner,
        "primary_key": t.primary_key, "partition_by": t.partition_by, "cluster_by": t.cluster_by,
        "holds_fields": t.holds_fields, "columns": cols,
        "foreign_keys": [r.model_dump(exclude={"owner"}) for r in schema.relationships if r.from_table == t.name],
        "referenced_by": [f"{r.from_table}({', '.join(r.from_columns)})" for r in schema.relationships if r.to_table == t.name],
        "derived_views": [view_summary(v) for v in schema.views if v.source_table == t.name],
        **({"ref_rows": len(t.rows)} if t.layer == "ref" else {}),
    }


def get_field(schema: Schema, name: str) -> dict[str, Any]:
    f = schema.catalogue.field(name)
    if f is None:
        raise KeyError(f"Field '{name}' does not exist")
    return {
        "field": f.model_dump(mode="json", exclude_none=True),
        "placed_in": placed_fields(schema).get(name, []),
        "checks": checks_for_field(schema, name),
    }


def checks_for_column(schema: Schema, table: str, column: str) -> dict[str, Any]:
    v = schema.view(table)
    if v is not None and v.column(column):
        dc = v.column(column)
        return {"column": f"{table}.{column}", "field": dc.field_id, "derived": dc.expression,
                "checks": checks_for_field(schema, dc.field_id) if dc.field_id else []}
    t = schema.table(table)
    if t is None or t.column(column) is None:
        raise KeyError(f"Column '{table}.{column}' does not exist")
    c = t.column(column)
    if not c.field_id:
        return {"column": f"{table}.{column}", "field": None, "checks": [], "note": "Column is not linked to a catalogue field"}
    return {"column": f"{table}.{column}", "field": c.field_id, "checks": checks_for_field(schema, c.field_id)}


def columns_for_check(schema: Schema, code: str) -> dict[str, Any]:
    chk = schema.catalogue.check(code)
    if chk is None:
        raise KeyError(f"Check '{code}' does not exist")
    fields = sorted({p.field_name for p in schema.catalogue.field_checks if p.check_code == code})
    placed = placed_fields(schema)
    return {
        "check": chk.model_dump(mode="json", exclude_none=True, exclude={"owner"}),
        "fields": fields,
        "columns": sorted({loc for f in fields for loc in placed.get(f, [])}),
        "rules": [r.code for r in schema.catalogue.checks if code in r.parent_gates],
    }


def search(schema: Schema, q: str, limit: int = 40) -> list[dict[str, Any]]:
    ql = q.lower().strip()
    hits: list[dict[str, Any]] = []

    def m(*vals: Optional[str]) -> bool:
        return any(v and ql in v.lower() for v in vals)

    for t in schema.tables:
        if m(t.name, t.description):
            hits.append({"kind": "table", "name": t.name, "layer": t.layer})
        for c in t.columns:
            if m(c.name, c.description, c.cdp_alias, c.protocol_id, c.field_id):
                hits.append({"kind": "column", "name": f"{t.name}.{c.name}", "type": c.type, "field": c.field_id,
                             "cdp_alias": c.cdp_alias, "protocol_id": c.protocol_id})
    for v in schema.views:
        if m(v.name, v.description):
            hits.append({"kind": "view", "name": v.name, "source_table": v.source_table})
        for c in v.columns:
            if m(c.name, c.description, c.field_id, c.expression):
                hits.append({"kind": "view_column", "name": f"{v.name}.{c.name}", "type": c.type, "field": c.field_id,
                             "expression": c.expression})
    for f in schema.catalogue.fields:
        if m(f.name, f.description, f.cdp_column, f.protocol_id):
            hits.append({"kind": "field", "name": f.name, "protocol_id": f.protocol_id, "cdp_column": f.cdp_column, "status": f.status})
    for c in schema.catalogue.checks:
        if m(c.code, c.name):
            hits.append({"kind": "check", "name": c.code, "title": c.name, "status": c.status})
    return hits[:limit]


def list_ref_values(schema: Schema, table: str) -> dict[str, Any]:
    t = schema.table(table)
    if t is None or t.layer != "ref":
        raise KeyError(f"'{table}' is not a ref table")
    return {"table": t.name, "rows": [r.model_dump(mode="json", exclude_none=True) for r in t.rows]}
