"""BigQuery script export: dataset, tables in dependency order, NOT ENFORCED keys, seed INSERTs."""
from __future__ import annotations

import math
import shutil
import subprocess
from typing import Any, Optional

from .models import Column, DerivedView, Schema, Table

LAYER_GROUP = {"ref": 0, "catalogue": 1, "dim": 2, "provenance": 3, "fact": 3, "child": 4, "bridge": 4}
SEED_TABLES = {"dim_field", "dim_check", "bridge_field_check"}


def _q(project: str, dataset: str, table: Optional[str] = None) -> str:
    return f"`{project}.{dataset}.{table}`" if table else f"`{project}.{dataset}`"


def _dq(s: str) -> str:
    """BigQuery double-quoted string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "") + '"'


def _sq(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "") + "'"


def _lit(v: Any) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return "NULL"
        return repr(v)
    if isinstance(v, (list, tuple)):
        return _sq(", ".join(str(x) for x in v))
    return _sq(str(v))


def column_description(col: Column) -> str:
    parts = [col.description.strip()] if col.description else []
    tags = []
    if col.protocol_id:
        tags.append(f"Protocol ID: {col.protocol_id}")
    if col.cdp_alias:
        tags.append(f"CDP alias: {col.cdp_alias}")
    if col.validation_rule:
        tags.append(f"Rule: {col.validation_rule.describe()}")
    if tags:
        parts.append(f"[{'; '.join(tags)}]")
    return " ".join(parts)


def _col_type(col: Column) -> str:
    if col.mode == "REPEATED" and not col.type.upper().startswith("ARRAY<"):
        return f"ARRAY<{col.type}>"
    return col.type


def table_order(schema: Schema) -> list[Table]:
    """Layer groups (ref, catalogue, dims, provenance+facts, children+bridges), FK-topological inside."""
    deps: dict[str, set[str]] = {t.name: set() for t in schema.tables}
    for r in schema.relationships:
        if r.from_table in deps and r.to_table in deps and r.from_table != r.to_table:
            deps[r.from_table].add(r.to_table)
    ordered: list[Table] = []
    for group in sorted(set(LAYER_GROUP.values())):
        pending = [t for t in schema.tables if LAYER_GROUP[t.layer] == group]
        while pending:
            waiting = {p.name for p in pending}
            # First table (in file order) whose same-group dependencies are already emitted; else break the cycle.
            t = next((t for t in pending if not (deps[t.name] & waiting)), pending[0])
            ordered.append(t)
            pending.remove(t)
    return ordered


def create_table_sql(schema: Schema, t: Table, project: str, dataset: str) -> str:
    lines = []
    for c in t.columns:
        nn = " NOT NULL" if c.mode == "REQUIRED" else ""
        desc = column_description(c)
        opt = f" OPTIONS(description={_dq(desc)})" if desc else ""
        lines.append(f"  {c.name} {_col_type(c)}{nn}{opt}")
    if t.primary_key:
        lines.append(f"  PRIMARY KEY ({', '.join(t.primary_key)}) NOT ENFORCED")
    for r in schema.relationships:
        if r.from_table == t.name:
            lines.append(f"  CONSTRAINT {r.name} FOREIGN KEY ({', '.join(r.from_columns)}) "
                         f"REFERENCES {_q(project, dataset, r.to_table)}({', '.join(r.to_columns)}) NOT ENFORCED")
    sql = f"CREATE TABLE IF NOT EXISTS {_q(project, dataset, t.name)} (\n" + ",\n".join(lines) + "\n)"
    if t.partition_by:
        col = t.column(t.partition_by)
        ctype = col.type.upper() if col else ""
        if ctype == "TIMESTAMP" or ctype == "DATETIME":
            sql += f"\nPARTITION BY DATE({t.partition_by})"
        elif ctype == "INT64" and t.partition_range:
            pr = t.partition_range
            sql += f"\nPARTITION BY RANGE_BUCKET({t.partition_by}, GENERATE_ARRAY({pr.start}, {pr.end}, {pr.interval}))"
        else:
            sql += f"\nPARTITION BY {t.partition_by}"
    if t.cluster_by:
        sql += f"\nCLUSTER BY {', '.join(t.cluster_by)}"
    tdesc = " ".join(x for x in [t.description.rstrip(".") + "." if t.description else "",
                                 f"Grain: {t.grain}." if t.grain else ""] if x)
    if tdesc:
        sql += f"\nOPTIONS(description={_dq(tdesc)})"
    return sql + ";"


def seed_rows(schema: Schema, t: Table) -> list[dict[str, Any]]:
    cat = schema.catalogue
    if t.layer == "ref":
        rows = []
        for r in t.rows:
            row = {"code": r.code, "label": r.label, "meaning": r.meaning, "status": r.status, "list_source": r.list_source}
            row.update(r.extra)
            rows.append(row)
        return rows
    if t.name == "dim_field":
        return [{"field_name": f.name, "protocol_id": f.protocol_id, "cdp_column": f.cdp_column, "module": f.module,
                 "data_category": f.data_category, "grain": f.grain, "field_type": f.field_type, "format": f.format,
                 "description": f.description, "read_from": f.read_from, "method": f.method, "priority": f.priority,
                 "requirement": f.requirement, "severity": f.severity, "fill_of_50": f.fill_of_50, "note": f.note,
                 "status": f.status} for f in cat.fields]
    if t.name == "dim_check":
        return [{"check_code": c.code, "check_name": c.name, "check_fx": c.check_fx, "check_type": c.check_type,
                 "applies_to_categories": ", ".join(c.applies_to_categories) or None,
                 "parent_gate": ", ".join(c.parent_gates) or None, "status": c.status, "remarks": c.remarks}
                for c in cat.checks]
    if t.name == "bridge_field_check":
        return [{"field_name": p.field_name, "check_code": p.check_code, "pass_criteria": p.pass_criteria,
                 "fail_criteria": p.fail_criteria, "example": p.example, "reference": p.reference,
                 "remarks": p.remarks, "score": p.score, "weight": p.weight} for p in cat.field_checks]
    return []


def insert_sql(schema: Schema, t: Table, project: str, dataset: str, batch: int = 200) -> list[str]:
    if t.layer != "ref" and t.name not in SEED_TABLES:
        return []
    rows = seed_rows(schema, t)
    names = [c.name for c in t.columns]
    ints = {c.name for c in t.columns if c.type.upper() == "INT64"}
    nums = {c.name for c in t.columns if c.type.upper() in ("NUMERIC", "FLOAT64", "BIGNUMERIC")}
    bools = {c.name for c in t.columns if c.type.upper() == "BOOL"}
    out = []
    if not rows:
        return [f"-- {t.name}: no seed rows"]
    for i in range(0, len(rows), batch):
        chunk = rows[i:i + batch]
        vals = []
        for row in chunk:
            cells = []
            for n in names:
                v = row.get(n)
                if v is not None and n in ints:
                    try:
                        v = int(float(v))
                    except (TypeError, ValueError):
                        v = None
                elif v is not None and n in nums:
                    try:
                        v = float(v)
                    except (TypeError, ValueError):
                        v = None
                elif v is not None and n in bools:
                    v = bool(v)
                elif v is not None and n not in ints | nums | bools and not isinstance(v, str):
                    v = str(v)
                cells.append(_lit(v))
            vals.append("  (" + ", ".join(cells) + ")")
        out.append(f"INSERT INTO {_q(project, dataset, t.name)} ({', '.join(names)}) VALUES\n" + ",\n".join(vals) + ";")
    return out


def create_view_sql(schema: Schema, v: DerivedView, project: str, dataset: str) -> str:
    src = schema.table(v.source_table)
    descs: list[tuple[str, str]] = []
    for g in v.group_by:
        col = src.column(g) if src else None
        descs.append((g, column_description(col) if col else ""))
    for c in v.columns:
        f = schema.catalogue.field(c.field_id) if c.field_id else None
        tags = [f"Derived: {c.expression}"]
        if f and f.protocol_id:
            tags.insert(0, f"Protocol ID: {f.protocol_id}")
        if f and f.cdp_column:
            tags.insert(1 if f.protocol_id else 0, f"CDP alias: {f.cdp_column}")
        text = c.description or (f.description if f else "") or ""
        descs.append((c.name, f"{text} [{'; '.join(tags)}]".strip()))
    collist = ",\n".join(f"  {n} OPTIONS(description={_dq(d)})" if d else f"  {n}" for n, d in descs)
    select = ",\n".join([f"  {g}" for g in v.group_by] + [f"  {c.expression} AS {c.name}" for c in v.columns])
    sql = f"CREATE OR REPLACE VIEW {_q(project, dataset, v.name)} (\n{collist}\n)"
    if v.description:
        sql += f"\nOPTIONS(description={_dq(v.description)})"
    sql += f"\nAS\nSELECT\n{select}\nFROM {_q(project, dataset, v.source_table)}"
    if v.group_by:
        sql += f"\nGROUP BY {', '.join(v.group_by)}"
    return sql + ";"


def export_bigquery(schema: Schema, project: str, dataset: str, location: Optional[str] = None,
                    table: Optional[str] = None, include_seeds: bool = True) -> str:
    order = table_order(schema)
    if table and schema.view(table):
        return create_view_sql(schema, schema.view(table), project, dataset) + "\n"
    if table:
        t = schema.table(table)
        if t is None:
            raise KeyError(f"Table '{table}' does not exist")
        parts = [create_table_sql(schema, t, project, dataset)]
        if include_seeds:
            parts += insert_sql(schema, t, project, dataset)
        return "\n\n".join(parts) + "\n"
    head = f"CREATE SCHEMA IF NOT EXISTS {_q(project, dataset)}"
    if location:
        head += f"\nOPTIONS(location={_dq(location)})"
    parts = [f"-- Allshares CDP schema: {len(order)} tables. Keys are NOT ENFORCED.", head + ";"]
    current = None
    for t in order:
        g = LAYER_GROUP[t.layer]
        if g != current:
            current = g
            parts.append("-- " + ["Ref tables", "Catalogue", "Dimensions", "Provenance and facts", "Children and bridges"][g])
        parts.append(create_table_sql(schema, t, project, dataset))
    if schema.views:
        parts.append("-- Derived views")
        for v in schema.views:
            parts.append(create_view_sql(schema, v, project, dataset))
    if include_seeds:
        parts.append("-- Seed data")
        for t in order:
            parts += insert_sql(schema, t, project, dataset)
    return "\n\n".join(parts) + "\n"


def parse_check(sql: str) -> dict[str, Any]:
    """Parse with sqlglot (BigQuery dialect). Every statement must parse to a real AST node."""
    import sqlglot
    from sqlglot import exp

    try:
        stmts = [s for s in sqlglot.parse(sql, read="bigquery", error_level=sqlglot.ErrorLevel.RAISE) if s is not None]
    except Exception as e:  # sqlglot.errors.ParseError and tokenizer errors
        return {"ok": False, "statements": 0, "error": str(e)[:500]}
    commands = [s.sql("bigquery")[:120] for s in stmts if isinstance(s, exp.Command)]
    if commands:
        return {"ok": False, "statements": len(stmts), "error": f"Unparsed statement(s): {commands[:3]}"}
    return {"ok": True, "statements": len(stmts), "error": None}


def bq_dry_run(sql: str, project: Optional[str] = None) -> dict[str, Any]:
    """Optional: `bq query --dry_run` if the bq CLI is installed. Needs gcloud auth."""
    bq = shutil.which("bq")
    if not bq:
        return {"ok": False, "available": False, "output": "bq CLI not found"}
    cmd = [bq, "query", "--use_legacy_sql=false", "--dry_run"]
    if project:
        cmd.insert(1, f"--project_id={project}")
    try:
        p = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=120)
    except Exception as e:
        return {"ok": False, "available": True, "output": str(e)}
    return {"ok": p.returncode == 0, "available": True, "output": (p.stdout + p.stderr)[-2000:]}


