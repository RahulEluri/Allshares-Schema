"""Turn the workbooks into a catalogue snapshot: fields, checks, pairs, notes, ref seeds.

The same snapshot feeds the first import (draft schema) and every re-import (diff).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from ..models import CatalogueField, Check, FieldCheck, InternalReference, Note, RefValue, ValidationRule
from .readers import CONFIG_DIR, WorkbookReader

GATE_CODE = re.compile(r"[A-Z]+-\d+")


def load_draft_config(path: Path | str | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "draft_schema.yaml").read_text(encoding="utf-8"))


@dataclass
class Snapshot:
    fields: list[CatalogueField] = field(default_factory=list)
    checks: list[Check] = field(default_factory=list)
    field_checks: list[FieldCheck] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    ref_values: dict[str, list[RefValue]] = field(default_factory=dict)
    rules: dict[str, ValidationRule] = field(default_factory=dict)  # Fixed Sets rows that are rules
    internal: InternalReference = field(default_factory=InternalReference)
    notices: list[str] = field(default_factory=list)
    missing_datasets: list[str] = field(default_factory=list)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _split_codes(s: Optional[str]) -> list[str]:
    return [c.strip() for c in (s or "").split(",") if c.strip()]


def _int(v: Any) -> Optional[int]:
    try:
        return int(float(v)) if v is not None else None
    except (TypeError, ValueError):
        return None


def _float(v: Any) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _str(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


def _format_from_type(t: str) -> str:
    t = (t or "").lower()
    if t.startswith("one of"):
        return "Code"
    if "integer" in t:
        return "Number"
    if "date" in t:
        return "Date"
    if "amount" in t:
        return "Money"
    if "boolean" in t:
        return "yes/no text"
    if t.startswith("list"):
        return "List (name: value)"
    if "number" in t:
        return "Number"
    return "Text"


def _rule_from_text(field_name: str, text: str) -> Optional[ValidationRule]:
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:to|-)\s*(-?\d+(?:\.\d+)?)", text or "")
    if m and "nace" not in (text or "").lower():
        return ValidationRule(kind="range", min=float(m.group(1)), max=float(m.group(2)), description=text)
    if "nn.nn" in (text or "").lower():
        return ValidationRule(kind="pattern", pattern=r"^\d{2}\.\d{2}$", description=text)
    return None


def build_snapshot(reader: Optional[WorkbookReader] = None, draft_cfg: Optional[dict] = None) -> Snapshot:
    reader = reader or WorkbookReader()
    cfg = draft_cfg or load_draft_config()
    snap = Snapshot()
    ds = {name: reader.read(name) for name in reader.mapping["datasets"]}
    for name, d in ds.items():
        if d.missing:
            sheets = reader.mapping["datasets"][name]["sheets"]
            snap.missing_datasets.append(name)
            snap.notices.append(f"Optional sheet not found for '{name}': {', '.join(sheets)}")

    # ---------------------------------------------------------------- fields
    pmap = {r["field_name"]: r for r in ds["protocol_map"].rows if r.get("field_name")}
    reqs = {r["name"]: r for r in ds["requirements"].rows if r.get("name")}
    fc_first: dict[str, dict] = {}
    for r in ds["field_checks"].rows:
        fc_first.setdefault(r["field_name"], r)

    book_checks: dict[str, list[str]] = {}
    for r in ds["fields"].rows:
        name = r["name"]
        pm, rq, fc = pmap.get(name, {}), reqs.get(name, {}), fc_first.get(name, {})
        raw_type = fc.get("field_type")
        ftype = None
        if raw_type:
            ftype = "derived" if raw_type.lower().startswith("derived") else "direct"
        elif r.get("method"):
            ftype = "derived" if "derived" in r["method"].lower() else "direct"
        snap.fields.append(CatalogueField(
            name=name,
            protocol_id=_str(pm.get("protocol_id") or r.get("protocol_id")),
            cdp_column=pm.get("cdp_column"),
            module=fc.get("module"),
            data_category=r.get("category"),
            grain=r.get("grain"),
            field_type=ftype,
            field_type_detail=raw_type if raw_type and raw_type.lower() not in ("direct", "derived") else None,
            format=r.get("format"),
            description=r.get("description"),
            read_from=r.get("read_from"),
            method=r.get("method"),
            priority=_str(rq.get("priority")),
            requirement=rq.get("requirement"),
            severity=rq.get("severity"),
            fill_of_50=_int(rq.get("fill_of_50")),
            why_it_matters=rq.get("why_it_matters"),
            note=r.get("note"),
            status="active",
            source=f"{Path(reader.paths['fields_book']).name} / {r['_sheet']}",
        ))
        book_checks[name] = _split_codes(r.get("checks_applied"))
    known = {f.name for f in snap.fields}
    for name in reqs:
        if name not in known:
            snap.notices.append(f"Sheet1 lists '{name}', which is not a catalogue field")

    grains = cfg.get("conor_field_grain", {})
    for r in ds["conor_fields"].rows:
        names = [n.strip() for n in str(r["name"]).split("/")]
        types = [t.strip() for t in str(r.get("type") or "").split("/")]
        for i, n in enumerate(names):
            if not n or n in known:
                continue
            t = types[i] if len(types) == len(names) else (r.get("type") or "")
            grain = grains.get(n, grains.get("default", "Role"))
            snap.fields.append(CatalogueField(
                name=n, format=_format_from_type(t), description=r.get("meaning"), grain=grain,
                module="Pay and role" if grain == "Role" else ("Company and ownership" if grain == "Company" else None),
                note=f"Type: {r.get('type')}. Unblocks: {r.get('unblocks')}", status="new",
                source=f"{Path(reader.paths['gates_book']).name} / Possible tracker fields",
            ))
            known.add(n)
    for p in cfg.get("parked_fields", []):
        if p["name"] not in known:
            snap.fields.append(CatalogueField(**p, status="parked", source="Conor 02 Nov (AGE rules)"))
            known.add(p["name"])

    # ---------------------------------------------------------------- checks
    for r in ds["checks"].rows:
        remarks = r.get("remarks")
        snap.checks.append(Check(
            code=r["code"], name=r["name"],
            check_fx=(r.get("check_fx") or "").lower() or None,
            check_type=(r.get("check_type") or "").lower() or None,
            applies_to_categories=_split_codes(r.get("applies_to")),
            fields_checked=_int(r.get("fields_checked")),
            status="hold_off" if remarks and "hold off" in remarks.lower() else "active",
            remarks=remarks, kind="gate",
        ))
    codes = {c.code for c in snap.checks}
    undefined: dict[str, list[str]] = {}
    for fname, cs in book_checks.items():
        for c in cs:
            if c not in codes:
                undefined.setdefault(c, []).append(fname)
    for r in ds["field_checks"].rows:
        if r["check_code"] not in codes:
            undefined.setdefault(r["check_code"], []).append(r["field_name"])
    for c, fs in sorted(undefined.items()):
        snap.checks.append(Check(code=c, name=f"Undefined check (cited for {', '.join(sorted(set(fs)))})",
                                 status="to_do", undefined=True,
                                 remarks="Cited in the field catalogue but not defined in All Checks"))
        codes.add(c)

    for r in ds["conor_rules"].rows:
        gate_text = r.get("parent_gate") or ""
        rel = "new" if "(new)" in gate_text.lower() else "changed" if "(changed)" in gate_text.lower() else "existing"
        note = r.get("note")
        result = r.get("result_if_not")
        snap.checks.append(Check(
            code=r["code"], name=r.get("passes_when") or r["code"], kind="rule",
            parent_gates=GATE_CODE.findall(gate_text), parent_relation=rel,
            applies_when=r.get("applies_when"), result_if_not=result,
            check_type=("hard" if (result or "").lower() == "fail" else "soft") if result else None,
            status="existing" if note and "existing gate" in note.lower() else "to_do",
            remarks=note,
        ))

    checks_by_code = {c.code: c for c in snap.checks}
    for r in ds["conor_gate_changes"].rows:
        gate = r.get("gate")
        change = {k: r.get(k) for k in ("today", "suggestion", "why") if r.get(k)}
        if gate in checks_by_code:
            checks_by_code[gate].proposed_change = {**change, "source": "Conor 02 Nov: Gate suggestions"}
        elif gate:
            snap.notes.append(Note(id=_slug(gate).upper(), kind="gate_suggestion", title=gate,
                                   text=" | ".join(f"{k}: {v}" for k, v in change.items())))

    # ---------------------------------------------------------------- field-check pairs
    seen: set[tuple[str, str]] = set()
    fmod = {f.name: f.module for f in snap.fields}
    for r in ds["field_checks"].rows:
        k = (r["field_name"], r["check_code"])
        if k in seen:
            snap.notices.append(f"Duplicate field-check pair {k} in Field Checks row {r['_row']}")
            continue
        seen.add(k)
        snap.field_checks.append(FieldCheck(
            field_name=k[0], check_code=k[1], module=r.get("module"),
            pass_criteria=_str(r.get("pass_criteria")), fail_criteria=_str(r.get("fail_criteria")),
            example=_str(r.get("example")), reference=_str(r.get("reference")), remarks=_str(r.get("remarks")),
            score=_float(r.get("score")), weight=_float(r.get("weight")),
        ))
    for fname, cs in book_checks.items():
        for c in cs:
            if (fname, c) not in seen:
                seen.add((fname, c))
                snap.field_checks.append(FieldCheck(field_name=fname, check_code=c, module=fmod.get(fname),
                                                    remarks="Cited in Book1 'Checks applied'; not in Field Checks"))

    # ---------------------------------------------------------------- notes (D, E)
    for r in ds["conor_quote_matching"].rows:
        step = _int(r.get("step"))
        snap.notes.append(Note(id=f"QM-{step}", kind="quote_matching", title=f"Quote matching step {step}", text=r.get("rule") or ""))
    for i, r in enumerate(ds["conor_load_bar"].rows, 1):
        snap.notes.append(Note(id=f"LB-{i}", kind="load_bar", title=r.get("gate") or f"Load bar {i}", text=r.get("text") or ""))

    # ---------------------------------------------------------------- ref seeds
    fk_by_field = _fk_targets(cfg)
    targets = cfg.get("fixed_set_targets", {})
    rule_fields = set(cfg.get("fixed_set_rules", []))
    for r in ds["fixed_sets"].rows:
        fname = r.get("field_name")
        if fname in rule_fields:
            rule = _rule_from_text(fname, _str(r.get("allowed_value")) or "")
            if rule:
                snap.rules[fname] = rule
            continue
        table = targets.get(fname) if fname in targets else fk_by_field.get(fname)
        if not table:
            snap.notices.append(f"Fixed Sets: no ref table for field '{fname}' (row {r['_row']})")
            continue
        code = _str(r.get("allowed_value"))
        if code is None:
            continue
        extra = {k: r.get(k) for k in ("source_wording", "count_in_50", "checked_by") if r.get(k) is not None}
        _add_ref(snap, table, RefValue(code=code, label=code, meaning=r.get("meaning"), status=r.get("status"),
                                       list_source=r.get("list_source"), extra=extra))

    if "ref_lti_basis" not in snap.ref_values:
        for r in ds["conor_lti_basis"].rows:
            if r.get("code"):
                _add_ref(snap, "ref_lti_basis", RefValue(
                    code=_slug(r["code"]), label=r["code"], meaning=r.get("label"), status="Proposed",
                    list_source="Conor 02 Nov: LTI basis",
                    extra={k: r[k] for k in ("stored_as", "rule") if r.get(k)}))
    if "ref_sti_max_basis" not in snap.ref_values:
        for r in ds["conor_sti_basis"].rows:
            if r.get("code"):
                _add_ref(snap, "ref_sti_max_basis", RefValue(
                    code=_slug(r["code"]), label=r["code"], meaning=r.get("label"), status="Proposed",
                    list_source="Conor 02 Nov: STI basis", extra={"effect_on_sti_1": r["effect"]} if r.get("effect") else {}))
    if "ref_quote_match" not in snap.ref_values:
        qm_type = next((r.get("type") for r in ds["conor_fields"].rows if r.get("name") == "quote_match"), None)
        step_text = " ".join(n.text for n in snap.notes if n.kind == "quote_matching")
        meanings = dict(re.findall(r"\b(exact|normalised|none)\s*\(([^)]*)\)", step_text))
        if qm_type and qm_type.lower().startswith("one of"):
            for code in _split_codes(qm_type.split(":", 1)[1]):
                _add_ref(snap, "ref_quote_match", RefValue(code=code, label=code, meaning=meanings.get(code), status="Proposed",
                                                           list_source="Conor 02 Nov: Possible tracker fields / Quote matching"))
    for table, spec in (cfg.get("static_seeds") or {}).items():
        if table in snap.ref_values:
            continue
        for row in spec["rows"]:
            _add_ref(snap, table, RefValue(status=spec.get("status"), list_source=spec.get("list_source"), **row))

    # ---------------------------------------------------------------- internal reference
    snap.internal = InternalReference(
        provisional_ranges=[{k: v for k, v in r.items() if not k.startswith("_")} for r in ds["provisional_ranges"].rows],
        range_notes=[r["text"] for r in ds["range_notes"].rows],
    )
    return snap


def _add_ref(snap: Snapshot, table: str, value: RefValue) -> None:
    rows = snap.ref_values.setdefault(table, [])
    if any(r.code == value.code for r in rows):
        snap.notices.append(f"Duplicate code '{value.code}' for {table}; kept the first")
        return
    rows.append(value)


def _fk_targets(cfg: dict) -> dict[str, str]:
    """field name -> ref table, from draft columns that link a field and FK a ref table."""
    out: dict[str, str] = {}
    for t in cfg["tables"]:
        for c in t["columns"]:
            if c.get("field") and str(c.get("fk", "")).startswith("ref_") and c["field"] not in out:
                out[c["field"]] = c["fk"]
    return out
