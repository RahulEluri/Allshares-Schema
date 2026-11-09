"""Build the first-import draft schema (brief §5) from a snapshot and config/draft_schema.yaml."""
from __future__ import annotations

from typing import Optional

from ..bqtypes import type_for_format
from ..models import Catalogue, Column, DerivedColumn, DerivedView, Relationship, Schema, Table, ValidationRule
from ..operations import apply_lineage
from .snapshot import Snapshot, load_draft_config

REF_COLUMNS = [
    ("code", "REQUIRED", "Code (primary key)"),
    ("label", "NULLABLE", "Display label"),
    ("meaning", "NULLABLE", "Meaning / when to use"),
    ("status", "NULLABLE", "In use, Proposed (confirm with Allshares) or Review"),
    ("list_source", "NULLABLE", "Where the list comes from"),
]


def build_draft(snap: Snapshot, cfg: Optional[dict] = None) -> Schema:
    cfg = cfg or load_draft_config()
    s = Schema(catalogue=Catalogue(fields=list(snap.fields), checks=list(snap.checks),
                                   field_checks=list(snap.field_checks), notes=list(snap.notes)),
               internal_reference=snap.internal)
    fields = {f.name: f for f in snap.fields}

    for name, spec in cfg["ref_tables"].items():
        cols = [Column(name=n, mode=m, description=d) for n, m, d in REF_COLUMNS]
        cols += [Column(name=e["name"], type=e.get("type", "STRING"), description=e.get("description", ""))
                 for e in spec.get("extra", [])]
        s.tables.append(Table(name=name, layer="ref", description=spec.get("description", ""),
                              grain="one row per code", columns=cols, primary_key=["code"],
                              rows=list(snap.ref_values.get(name, []))))

    for t in cfg["tables"]:
        table = Table(name=t["name"], layer=t["layer"], description=t.get("description", ""), grain=t.get("grain", ""),
                      primary_key=list(t.get("pk", [])), partition_by=t.get("partition"),
                      cluster_by=list(t.get("cluster", [])), holds_fields=list(t.get("holds", [])))
        for c in t["columns"]:
            f = fields.get(c["field"]) if c.get("field") else None
            if c.get("field") and f is None:
                raise ValueError(f"Draft column {t['name']}.{c['name']} links unknown field '{c['field']}'")
            col = Column(
                name=c["name"],
                type=c.get("type") or (type_for_format(f.format, f.name) if f else "STRING"),
                mode=c.get("mode", "NULLABLE"),
                description=c.get("description") or "",
                field_id=f.name if f else None,
                cdp_alias=c.get("alias"),
                needs_confirmation=bool(c.get("confirm")),
            )
            if f:
                apply_lineage(col, f)
                if c.get("description"):
                    col.description = c["description"]
            rule = c.get("rule")
            if rule:
                col.validation_rule = ValidationRule(**rule)
            elif f and f.name in snap.rules:
                col.validation_rule = snap.rules[f.name]
            table.columns.append(col)
            if c.get("fk"):
                s.relationships.append(Relationship(
                    name=f"fk_{t['name']}_{c['name']}", from_table=t["name"], from_columns=[c["name"]],
                    to_table=c["fk"], to_columns=[], cardinality="many_to_one"))
        s.tables.append(table)

    for r in cfg.get("relationships", []):
        s.relationships.append(Relationship(name=f"fk_{r['from']}_{'_'.join(r['cols'])}", from_table=r["from"],
                                            from_columns=list(r["cols"]), to_table=r["to"], to_columns=[]))
    # Point every FK at its target's primary key.
    for rel in s.relationships:
        target = s.table(rel.to_table)
        if target is None:
            raise ValueError(f"Draft relationship {rel.name} targets missing table {rel.to_table}")
        rel.to_columns = list(target.primary_key)

    for v in cfg.get("views", []):
        for c in v["columns"]:
            if c.get("field") and c["field"] not in fields:
                raise ValueError(f"Draft view column {v['name']}.{c['name']} links unknown field '{c['field']}'")
        s.views.append(DerivedView(
            name=v["name"], source_table=v["source_table"], group_by=list(v["group_by"]),
            description=v.get("description", ""),
            columns=[DerivedColumn(name=c["name"], type=c.get("type", "STRING"), expression=c["expression"],
                                   description=c.get("description", ""), field_id=c.get("field")) for c in v["columns"]],
        ))
    return s
