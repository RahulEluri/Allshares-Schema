"""BigQuery type checks and the catalogue Format -> type mapping."""
from __future__ import annotations

import re

SCALAR_TYPES = {
    "STRING", "BYTES", "INT64", "NUMERIC", "BIGNUMERIC", "FLOAT64", "BOOL",
    "DATE", "DATETIME", "TIME", "TIMESTAMP", "JSON", "GEOGRAPHY",
}
PARTITION_TYPES = {"DATE", "DATETIME", "TIMESTAMP"}
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")

# Fields stored as whole numbers when Format is "Number" (brief §5 type table).
INT_FIELDS = {"headcount", "shares_outstanding", "aggregate_headcount", "fiscal_year", "months_in_role", "lti_units"}


def _split_top(s: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def is_valid_type(t: str) -> bool:
    t = (t or "").strip()
    up = t.upper()
    if up in SCALAR_TYPES:
        return True
    if up.startswith("ARRAY<") and up.endswith(">"):
        inner = t[6:-1].strip()
        return not inner.upper().startswith("ARRAY<") and is_valid_type(inner)
    if up.startswith("STRUCT<") and up.endswith(">"):
        inner = t[7:-1].strip()
        if not inner:
            return False
        for member in _split_top(inner):
            bits = member.split(None, 1)
            if len(bits) != 2 or not SNAKE.match(bits[0].lower()) or not is_valid_type(bits[1]):
                return False
        return True
    return False


def is_complex(t: str) -> bool:
    up = (t or "").upper()
    return up.startswith("ARRAY<") or up.startswith("STRUCT<")


def type_for_format(fmt: str | None, field_name: str = "") -> str:
    """Default BigQuery type for a catalogue Format (brief §5)."""
    f = (fmt or "").strip().lower()
    if f in ("date",):
        return "DATE"
    if f in ("money",):
        return "NUMERIC"
    if f in ("yes/no text", "boolean", "bool"):
        return "BOOL"
    if f in ("year", "integer"):
        return "INT64"
    if f.startswith("number"):
        return "INT64" if field_name in INT_FIELDS else "NUMERIC"
    return "STRING"
