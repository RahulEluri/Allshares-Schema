"""Re-import: diff the workbooks against schema.json and apply accepted items as operations.

Rules (brief §7): stable keys; a diff first; app-owned items need explicit acceptance;
removals are flagged, never applied; applying is a batch of normal operations.
"""
from __future__ import annotations

from typing import Any, Optional

from ..models import Schema
from ..store import SchemaStore
from .snapshot import Snapshot, build_snapshot

CATEGORY_ORDER = ["fields", "checks", "field_checks", "notes", "ref_values", "internal_reference"]


def _attrs(model) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude={"owner"})


def _changes(old: dict, new: dict) -> dict[str, dict[str, Any]]:
    return {k: {"before": old.get(k), "after": new.get(k)} for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)}


def _item(category, key, kind, label, *, before=None, after=None, changes=None, app_owned=False,
          applicable=True, reason=None, ops=None) -> dict[str, Any]:
    return {
        "id": f"{category}:{key}", "category": category, "key": key, "kind": kind, "label": label,
        "before": before, "after": after, "changes": changes or {}, "app_owned": app_owned,
        "applicable": applicable, "reason": reason, "ops": ops or [],
    }


def compute_diff(schema: Schema, snap: Snapshot) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cat = schema.catalogue

    def simple(category, current, incoming, key_of, label_of, add_op, update_op):
        cur = {key_of(x): x for x in current}
        new = {key_of(x): x for x in incoming}
        for k, n in new.items():
            if k not in cur:
                items.append(_item(category, k, "added", label_of(n), after=_attrs(n), ops=[add_op(n)]))
                continue
            c = cur[k]
            ch = _changes(_attrs(c), _attrs(n))
            if ch:
                items.append(_item(category, k, "changed", label_of(n), before=_attrs(c), after=_attrs(n), changes=ch,
                                   app_owned=c.owner == "app", ops=[update_op(n, {a: v["after"] for a, v in ch.items()})]))
        for k, c in cur.items():
            if k not in new and c.owner == "workbook":
                items.append(_item(category, k, "removed", label_of(c), before=_attrs(c), applicable=False,
                                   reason="Removed from the workbook; flagged only, never applied"))

    simple("fields", cat.fields, snap.fields, lambda f: f.name, lambda f: f.name,
           lambda f: {"op": "add_field", "field": _attrs(f)},
           lambda f, ch: {"op": "update_field", "name": f.name, "changes": ch})
    simple("checks", cat.checks, snap.checks, lambda c: c.code, lambda c: f"{c.code} {c.name}",
           lambda c: {"op": "add_check", "check": _attrs(c)},
           lambda c, ch: {"op": "update_check", "code": c.code, "changes": ch})
    simple("field_checks", cat.field_checks, snap.field_checks, lambda p: p.key,
           lambda p: f"{p.field_name} ← {p.check_code}",
           lambda p: {"op": "link_field_check", **{k: v for k, v in _attrs(p).items() if v is not None}},
           lambda p, ch: {"op": "update_field_check", "field_name": p.field_name, "check_code": p.check_code, "changes": ch})
    simple("notes", cat.notes, snap.notes, lambda n: n.id, lambda n: f"{n.id} {n.title}",
           lambda n: {"op": "upsert_note", "note": _attrs(n)},
           lambda n, ch: {"op": "upsert_note", "note": _attrs(n)})

    # Ref values, keyed by table + code.
    for table_name, rows in sorted(snap.ref_values.items()):
        t = schema.table(table_name)
        if t is None:
            for r in rows:
                items.append(_item("ref_values", f"{table_name}.{r.code}", "added", f"{table_name}: {r.code}",
                                   after=_attrs(r), applicable=False,
                                   reason=f"Ref table {table_name} no longer exists (renamed or deleted in the app)"))
            continue
        cur = {r.code: r for r in t.rows}
        new = {r.code: r for r in rows}
        for code, r in new.items():
            key, label = f"{table_name}.{code}", f"{table_name}: {code}"
            if code not in cur:
                args = {k: v for k, v in _attrs(r).items() if v not in (None, {})}
                items.append(_item("ref_values", key, "added", label, after=_attrs(r),
                                   ops=[{"op": "add_ref_value", "table": table_name, **args}]))
            else:
                ch = _changes(_attrs(cur[code]), _attrs(r))
                if ch:
                    items.append(_item("ref_values", key, "changed", label, before=_attrs(cur[code]), after=_attrs(r),
                                       changes=ch, app_owned=cur[code].owner == "app",
                                       ops=[{"op": "update_ref_value", "table": table_name, "code": code,
                                             "changes": {a: v["after"] for a, v in ch.items()}}]))
        for code, r in cur.items():
            if code not in new and r.owner == "workbook":
                items.append(_item("ref_values", f"{table_name}.{code}", "removed", f"{table_name}: {code}",
                                   before=_attrs(r), applicable=False,
                                   reason="Removed from the workbook; flagged only, never applied"))

    cur_ir, new_ir = schema.internal_reference.model_dump(mode="json"), snap.internal.model_dump(mode="json")
    if cur_ir != new_ir:
        items.append(_item("internal_reference", "provisional_ranges", "changed", "Provisional ranges and range notes",
                           changes={"rows": {"before": len(cur_ir["provisional_ranges"]), "after": len(new_ir["provisional_ranges"])},
                                    "notes": {"before": len(cur_ir["range_notes"]), "after": len(new_ir["range_notes"])}},
                           ops=[{"op": "set_internal_reference", **new_ir}]))
    items.sort(key=lambda i: (CATEGORY_ORDER.index(i["category"]), i["key"]))
    return items


def summarize(items: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for i in items:
        out.setdefault(i["category"], {"added": 0, "changed": 0, "removed": 0})[i["kind"]] += 1
    return out


def import_diff(store: SchemaStore, snap: Optional[Snapshot] = None) -> dict[str, Any]:
    schema, version = store.load()
    snap = snap or build_snapshot()
    items = compute_diff(schema, snap)
    return {"version": version, "summary": summarize(items), "items": items, "notices": snap.notices}


def apply_import_items(store: SchemaStore, item_ids: list[str], expected_version: str, actor: str,
                       reason: str = "", dry_run: bool = False, snap: Optional[Snapshot] = None):
    """Apply accepted diff items. App-owned items apply only when their id is listed explicitly."""
    schema, _ = store.load()
    items = {i["id"]: i for i in compute_diff(schema, snap or build_snapshot())}
    unknown = [i for i in item_ids if i not in items]
    if unknown:
        raise KeyError(f"Not in the current import diff: {', '.join(unknown)}")
    chosen = [items[i] for i in item_ids]
    blocked = [i["id"] for i in chosen if not i["applicable"]]
    if blocked:
        raise ValueError(f"These items are flagged only and cannot be applied: {', '.join(blocked)}")
    chosen.sort(key=lambda i: CATEGORY_ORDER.index(i["category"]))
    ops = [op for i in chosen for op in i["ops"]]
    return store.apply(ops, expected_version=expected_version, actor=actor,
                       reason=reason or f"Accepted {len(chosen)} import item(s)", dry_run=dry_run,
                       owner="workbook", source="import")
