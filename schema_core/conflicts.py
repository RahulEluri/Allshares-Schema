"""Known conflicts (brief §5e plus what the workbook inspection found). Surfaced, never resolved."""
from __future__ import annotations

import re
from typing import Any

from .models import Schema
from .validation import WEIGHT_TOLERANCE, module_weight_sums

IDENT_LIST = re.compile(r"^[a-z][a-z0-9_]*(\s*,\s*[a-z][a-z0-9_]*)*$")


def list_conflicts(schema: Schema) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cat = schema.catalogue

    def add(cid, title, detail, items=None, kind="decision"):
        out.append({"id": cid, "title": title, "detail": detail, "items": items or [], "kind": kind})

    co = cat.field("controlling_owner")
    if co:
        add("controlling_owner_meaning", "controlling_owner has two meanings",
            f"Book1 describes it as \"{co.description}\", while the Fixed Sets list is a type list that overlaps "
            "ownership_type. Modelled as an enum (FK to ref_controlling_owner) for now.",
            ["fact_company_year.controlling_owner", "fact_company_year.ownership_type"])

    country = schema.table("ref_country")
    if country is not None:
        codes = {r.code.upper() for r in country.rows}
        if not codes:
            add("country_list_short", "The country list is empty",
                "ref_country has no values (no Fixed Sets sheet). The known fixed set covers only the Nordics and "
                "Baltics, but the run includes UK and US companies.", ["ref_country"], "data")
        elif not {"GB", "US"} <= codes:
            add("country_list_short", "The country list is too short",
                f"ref_country has {len(codes)} codes and lacks {', '.join(sorted({'GB', 'US'} - codes))}; the run includes UK and US companies.",
                ["ref_country"], "data")

    proposed = [(t.name, r.code) for t in schema.tables if t.layer == "ref" for r in t.rows
                if (r.status or "").lower().startswith("proposed")]
    if proposed:
        add("unconfirmed_values", f"{len(proposed)} list values are unconfirmed",
            "Status 'Proposed: confirm with Allshares' (or Proposed from Conor's lists).",
            [f"{t}: {c}" for t, c in proposed], "data")

    empty = [t.name for t in schema.tables if t.layer == "ref" and not t.rows]
    if empty:
        add("empty_ref_tables", f"{len(empty)} ref tables have no values",
            "The workbook has no 'Fixed Sets' sheet, so these lists could not be seeded. Add the sheet and re-import.",
            empty, "data")

    parked = [f.name for f in cat.fields if f.status == "parked"]
    if parked:
        add("parked_fields", "Fields not yet in the pipeline",
            "Conor's 'add or park' fields. They sit in the field tray, not in tables.", parked)

    sums = module_weight_sums(schema)
    bad = {m: v for m, v in sums.items() if abs(v - 1) > WEIGHT_TOLERANCE}
    if bad:
        add("module_weights", "Module weights do not sum to 1 (MOD-1)",
            "Weighted scores per module should sum to 1.", [f"{m}: {v:.4f}" for m, v in sorted(bad.items())], "data")

    confirm = [f"{t.name}.{c.name}" for t in schema.tables for c in t.columns if c.needs_confirmation]
    if confirm:
        add("confirm_columns", "Column decisions to confirm (†)",
            "These columns are not in the field catalogue and need confirming with the team.", confirm)

    undefined = [f"{c.code}: {c.name}" for c in cat.checks if c.undefined]
    if undefined:
        add("undefined_checks", "Checks cited but not defined",
            "Book1 cites these codes but All Checks does not define them. Imported as placeholders with status to_do.",
            undefined, "data")

    hold = {c.code for c in cat.checks if c.status == "hold_off"}
    clash = [f"{r.code} → {g}" for r in cat.checks if r.kind == "rule" for g in r.parent_gates if g in hold]
    if clash:
        add("hold_off_parents", "New rules hang off gates marked 'hold off'",
            "Conor's rules point at parent gates whose All Checks remark says 'hold off'.", clash)

    odd = [f"{f.name} → '{f.cdp_column}'" for f in cat.fields if f.cdp_column and not IDENT_LIST.match(f.cdp_column)]
    if odd:
        add("cdp_alias_not_column", "Protocol Map entries that are not CDP column names",
            "Stored as-is on the field and its columns.", odd, "data")
    return out
