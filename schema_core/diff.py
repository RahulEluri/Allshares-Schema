"""A compact structural diff between two schema dumps.

Lists of named items (tables, columns, fields, checks, ...) are matched by their stable key,
so the diff reads like "tables.fact_pay_line.columns.year_of_birth: added".
"""
from __future__ import annotations

from typing import Any

KEY_ATTRS = ("name", "code", "id")


def _key(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    if "field_name" in item and "check_code" in item:
        return f"{item['field_name']}|{item['check_code']}"
    for k in KEY_ATTRS:
        if k in item and isinstance(item[k], str):
            return item[k]
    return None


def _keyed(items: list) -> dict[str, Any] | None:
    out: dict[str, Any] = {}
    for it in items:
        k = _key(it)
        if k is None or k in out:
            return None
        out[k] = it
    return out


def diff(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    if isinstance(before, dict) and isinstance(after, dict):
        for k in list(before) + [k for k in after if k not in before]:
            p = f"{path}.{k}" if path else k
            if k not in after:
                changes.append({"path": p, "change": "removed", "before": before[k]})
            elif k not in before:
                changes.append({"path": p, "change": "added", "after": after[k]})
            elif before[k] != after[k]:
                changes.extend(diff(before[k], after[k], p))
        return changes
    if isinstance(before, list) and isinstance(after, list) and before != after:
        kb, ka = _keyed(before), _keyed(after)
        if kb is not None and ka is not None and (kb or ka):
            for k in list(kb) + [k for k in ka if k not in kb]:
                p = f"{path}[{k}]"
                if k not in ka:
                    changes.append({"path": p, "change": "removed", "before": kb[k]})
                elif k not in kb:
                    changes.append({"path": p, "change": "added", "after": ka[k]})
                elif kb[k] != ka[k]:
                    changes.extend(diff(kb[k], ka[k], p))
            if [_key(x) for x in before if _key(x) in ka] != [_key(x) for x in after if _key(x) in kb]:
                changes.append({"path": path, "change": "reordered"})
            return changes
    if before != after:
        changes.append({"path": path, "change": "changed", "before": before, "after": after})
    return changes
