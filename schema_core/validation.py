"""Validation that runs before every save. Errors block the save; warnings do not."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Literal, Optional

from pydantic import BaseModel

from .bqtypes import PARTITION_TYPES, SNAKE, is_complex, is_valid_type
from .models import Schema

LAYER_PREFIX = {
    "ref": ("ref_",),
    "dim": ("dim_",),
    "fact": ("fact_",),
    "bridge": ("bridge_",),
    "catalogue": ("dim_", "bridge_"),
    "provenance": ("dim_", "fact_"),
}
WEIGHT_TOLERANCE = 1e-3


class Issue(BaseModel):
    severity: Literal["error", "warning"]
    code: str
    message: str
    table: Optional[str] = None
    column: Optional[str] = None


def _err(code, msg, table=None, column=None) -> Issue:
    return Issue(severity="error", code=code, message=msg, table=table, column=column)


def _warn(code, msg, table=None, column=None) -> Issue:
    return Issue(severity="warning", code=code, message=msg, table=table, column=column)


def placed_fields(schema: Schema) -> dict[str, list[str]]:
    """field name -> list of 'table.column' (or 'table' for child tables that hold it)."""
    out: dict[str, list[str]] = defaultdict(list)
    for t in schema.tables:
        for c in t.columns:
            if c.field_id:
                out[c.field_id].append(f"{t.name}.{c.name}")
        for f in t.holds_fields:
            if not any(p.startswith(f"{t.name}.") for p in out.get(f, [])):
                out[f].append(t.name)
    return out


def module_weight_sums(schema: Schema) -> dict[str, float]:
    sums: dict[str, float] = defaultdict(float)
    has_weight: dict[str, bool] = defaultdict(bool)
    for p in schema.catalogue.field_checks:
        mod = p.module or "(no module)"
        if p.weight is not None:
            sums[mod] += p.weight
            has_weight[mod] = True
        else:
            sums.setdefault(mod, 0.0)
    return dict(sums)


def validate(schema: Schema) -> list[Issue]:
    issues: list[Issue] = []
    field_names = {f.name for f in schema.catalogue.fields}

    # --- tables -------------------------------------------------------------------------
    for name, n in Counter(t.name for t in schema.tables).items():
        if n > 1:
            issues.append(_err("duplicate_table", f"Table name '{name}' is used {n} times", name))

    for t in schema.tables:
        if not SNAKE.match(t.name):
            issues.append(_err("name_not_snake_case", f"Table name '{t.name}' is not snake_case", t.name))
        prefixes = LAYER_PREFIX.get(t.layer)
        if prefixes and not t.name.startswith(prefixes):
            issues.append(_warn("layer_prefix", f"'{t.name}' is in layer '{t.layer}' but does not start with {' or '.join(prefixes)}", t.name))

        for cname, n in Counter(c.name for c in t.columns).items():
            if n > 1:
                issues.append(_err("duplicate_column", f"Column '{cname}' appears {n} times in {t.name}", t.name, cname))
        for c in t.columns:
            if not SNAKE.match(c.name):
                issues.append(_err("name_not_snake_case", f"Column '{t.name}.{c.name}' is not snake_case", t.name, c.name))
            if not is_valid_type(c.type):
                issues.append(_err("invalid_type", f"'{c.type}' is not a valid BigQuery type ({t.name}.{c.name})", t.name, c.name))
            elif is_complex(c.type) or c.mode == "REPEATED":
                issues.append(_warn("complex_type", f"{t.name}.{c.name} is {c.type if is_complex(c.type) else 'REPEATED'}; Power BI handles ARRAY/STRUCT badly", t.name, c.name))
            if c.field_id and c.field_id not in field_names:
                issues.append(_err("unknown_field", f"{t.name}.{c.name} links to field '{c.field_id}', which is not in dim_field", t.name, c.name))

        for pk in t.primary_key:
            col = t.column(pk)
            if col is None:
                issues.append(_err("pk_missing_column", f"Primary key column '{pk}' does not exist in {t.name}", t.name, pk))
            elif col.mode != "REQUIRED":
                issues.append(_err("pk_not_required", f"Primary key column {t.name}.{pk} must be REQUIRED", t.name, pk))
        if len(set(t.primary_key)) != len(t.primary_key):
            issues.append(_err("pk_duplicate", f"Primary key of {t.name} lists a column twice", t.name))

        if t.partition_by:
            col = t.column(t.partition_by)
            if col is None:
                issues.append(_err("partition_missing_column", f"Partition column '{t.partition_by}' does not exist in {t.name}", t.name))
            elif col.type.upper() in PARTITION_TYPES:
                pass
            elif col.type.upper() == "INT64" and t.partition_range is not None:
                pass
            else:
                issues.append(_err("partition_type", f"{t.name} partitions on {col.name} ({col.type}); must be DATE, DATETIME, TIMESTAMP, or INT64 with a range", t.name, col.name))
        if len(t.cluster_by) > 4:
            issues.append(_err("cluster_too_many", f"{t.name} clusters on {len(t.cluster_by)} columns; BigQuery allows at most 4", t.name))
        for cc in t.cluster_by:
            col = t.column(cc)
            if col is None:
                issues.append(_err("cluster_missing_column", f"Cluster column '{cc}' does not exist in {t.name}", t.name))
            elif is_complex(col.type) or col.mode == "REPEATED":
                issues.append(_err("cluster_type", f"{t.name} cannot cluster on {cc} ({col.type})", t.name, cc))

        if t.layer == "ref":
            for code, n in Counter(r.code for r in t.rows).items():
                if n > 1:
                    issues.append(_err("ref_duplicate_code", f"Code '{code}' appears {n} times in {t.name}", t.name))

    # --- relationships ------------------------------------------------------------------
    for name, n in Counter(r.name for r in schema.relationships).items():
        if n > 1:
            issues.append(_err("duplicate_relationship", f"Relationship name '{name}' is used {n} times"))
    in_rel: set[str] = set()
    for r in schema.relationships:
        in_rel.update((r.from_table, r.to_table))
        src, dst = schema.table(r.from_table), schema.table(r.to_table)
        if src is None or dst is None:
            issues.append(_err("fk_missing_table", f"Relationship {r.name} references a missing table", r.from_table))
            continue
        if len(r.from_columns) != len(r.to_columns):
            issues.append(_err("fk_column_count", f"Relationship {r.name}: {len(r.from_columns)} column(s) point at {len(r.to_columns)}", r.from_table))
            continue
        if not dst.primary_key or list(r.to_columns) != list(dst.primary_key):
            issues.append(_err("fk_target_not_pk", f"Relationship {r.name}: target ({', '.join(r.to_columns)}) is not the full primary key of {dst.name} ({', '.join(dst.primary_key) or 'none'})", r.from_table))
        for fc, tc in zip(r.from_columns, r.to_columns):
            a, b = src.column(fc), dst.column(tc)
            if a is None or b is None:
                issues.append(_err("fk_missing_column", f"Relationship {r.name}: column {src.name}.{fc} or {dst.name}.{tc} does not exist", r.from_table, fc))
            elif a.type.upper() != b.type.upper():
                issues.append(_err("fk_type_mismatch", f"Relationship {r.name}: {src.name}.{fc} is {a.type} but {dst.name}.{tc} is {b.type}", r.from_table, fc))

    for t in schema.tables:
        if t.layer == "fact" and t.name not in in_rel:
            issues.append(_warn("fact_no_relationship", f"Fact table {t.name} has no relationship", t.name))

    # --- catalogue ----------------------------------------------------------------------
    placed = placed_fields(schema)
    for f in schema.catalogue.fields:
        if f.status != "parked" and f.name not in placed:
            issues.append(_warn("field_not_placed", f"Catalogue field '{f.name}' is not placed in any table"))
    for mod, total in sorted(module_weight_sums(schema).items()):
        if abs(total - 1.0) > WEIGHT_TOLERANCE:
            issues.append(_warn("module_weights", f"Weights in module '{mod}' sum to {total:.4f}, not 1 (MOD-1)"))
    return issues


def errors(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == "error"]
