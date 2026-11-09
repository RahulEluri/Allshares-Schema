"""Build examples/worked_example_3_companies.xlsx: every table of schema.json on its own sheet,
colour-coded by layer and filled with a worked example for three FICTIONAL companies.

Run:  .venv/Scripts/python examples/build_worked_example.py
Table and column definitions are read from schema/schema.json, so the workbook always matches the schema.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema_core.export import table_order  # noqa: E402
from schema_core.store import SchemaStore  # noqa: E402
import worked_example_data as D  # noqa: E402

OUT = ROOT / "examples" / "worked_example_3_companies.xlsx"
FONT = "Arial"
LAYER_COLOR = {"ref": "64748B", "catalogue": "7C3AED", "provenance": "0D9488", "dim": "2563EB", "fact": "EA580C",
               "child": "16A34A", "bridge": "DB2777", "view": "A16207"}
LAYER_TINT = {"ref": "EEF1F5", "catalogue": "F1EAFE", "provenance": "E3F5F3", "dim": "E6EEFD", "fact": "FDEDE3",
              "child": "E6F6EA", "bridge": "FCE7F1", "view": "FBF1DC"}
LAYER_LABEL = {"dim": "Delivery: dimension", "fact": "Delivery: fact", "child": "Delivery: child", "view": "Derived view",
               "provenance": "Provenance", "catalogue": "Catalogue", "ref": "Reference list", "bridge": "Bridge"}
RESULT_FILL = {"pass": "C6EFCE", "fail": "FFC7CE", "review": "FFEB9C", "incomplete": "FCE4D6", "not_run": "E7E6E6"}
FIRST_DATA_ROW = 5
THIN = Side(style="thin", color="D9DDE3")

schema, VERSION = SchemaStore().load()
cat = schema.catalogue
FIELD = {f.name: f for f in cat.fields}


def f(size=10, bold=False, color="1F2933", italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def fill(hex_):
    return PatternFill("solid", start_color=hex_, end_color=hex_)


# =============================================================================== data per table
data: dict[str, list[dict]] = {
    "dim_company": D.DIM_COMPANY, "company_name_alias": D.COMPANY_NAME_ALIAS,
    "fact_company_year": D.FACT_COMPANY_YEAR, "company_holder": D.COMPANY_HOLDER,
    "company_breakdown": D.COMPANY_BREAKDOWN, "fact_pay_policy": D.FACT_PAY_POLICY,
    "fact_pay_line": D.FACT_PAY_LINE, "pay_line_role": D.PAY_LINE_ROLE,
    "pay_line_total_component": D.PAY_LINE_TOTAL_COMPONENT, "dim_source": D.DIM_SOURCE,
}

# Ref tables: real seeds from schema.json where they exist, example values otherwise.
for t in schema.tables:
    if t.layer != "ref":
        continue
    if t.rows:
        names = {c.name for c in t.columns}  # extra attributes without a column are not exported (same as the SQL)
        data[t.name] = [{k: v for k, v in {"code": r.code, "label": r.label, "meaning": r.meaning, "status": r.status,
                                           "list_source": r.list_source, **r.extra}.items() if k in names} for r in t.rows]
    else:
        data[t.name] = D.REF.get(t.name, [])

# Catalogue tables straight from schema.json.
data["dim_field"] = [dict(field_name=x.name, protocol_id=x.protocol_id, cdp_column=x.cdp_column, module=x.module,
                          data_category=x.data_category, grain=x.grain, field_type=x.field_type, format=x.format,
                          description=x.description, read_from=x.read_from, method=x.method, priority=x.priority,
                          requirement=x.requirement, severity=x.severity, fill_of_50=x.fill_of_50, note=x.note,
                          status=x.status) for x in cat.fields]
data["dim_check"] = [dict(check_code=c.code, check_name=c.name, check_fx=c.check_fx, check_type=c.check_type,
                          applies_to_categories=", ".join(c.applies_to_categories) or None,
                          parent_gate=", ".join(c.parent_gates) or None, status=c.status, remarks=c.remarks)
                     for c in cat.checks]
data["bridge_field_check"] = [dict(field_name=p.field_name, check_code=p.check_code, pass_criteria=p.pass_criteria,
                                   fail_criteria=p.fail_criteria, example=p.example, reference=p.reference,
                                   remarks=p.remarks, score=p.score, weight=p.weight) for p in cat.field_checks]

# =============================================================================== provenance: fact_field_value
SOURCE_BY_CATEGORY = {
    "Identity": ("LEI", "GLEIF LEI record"), "Listing and market": ("AR", "AR p.12, Share and shareholders"),
    "Sector": ("AR", "AR p.2, About the company"), "Reporting basis": ("AR", "AR p.60, Note 1 Accounting principles"),
    "Financials": ("AR", "AR p.58, Consolidated income statement"), "Workforce": ("AR", "AR p.41, Employees"),
    "Ownership and control": ("AR", "AR p.14, Largest shareholders"),
    "Segment and geography": ("AR", "AR p.95, Note 3 Operating segments"),
    "Pay policy": ("RR", "RR p.3, Remuneration policy"),
}
AR_IDENTITY = {"website", "business_id"}
FLOW_FIELDS = {"revenue", "ebitda", "revenue_by_segment", "revenue_by_country"}
MONEY_FORMATS = {"Money"}
BREAKDOWN_FIELD = {("segment", "revenue"): "revenue_by_segment", ("segment", "staff"): "staff_by_segment",
                   ("country", "revenue"): "revenue_by_country", ("country", "staff"): "staff_by_country"}
QUOTE_NONE = {("FJM", "coo", "base_salary")}  # one quote the checker cannot find -> SRC-1 fail


def fmt_value(v):
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, (int, float)):
        return f"{v:,.1f}" if isinstance(v, float) and not float(v).is_integer() else f"{int(v):,}"
    if isinstance(v, dt.date):
        return v.strftime("%d %B %Y")
    return str(v)


def typed(v):
    out = {"value_string": None, "value_numeric": None, "value_date": None, "value_bool": None}
    if isinstance(v, bool):
        out["value_bool"] = v
    elif isinstance(v, (int, float)):
        out["value_numeric"] = v
    elif isinstance(v, dt.date):
        out["value_date"] = v
    else:
        out["value_string"] = v
    return out


ffv: list[dict] = []
VALUE_INDEX: dict[tuple, dict] = {}


def emit(cid, field, value, *, pay_line=None, item=None, source=None, locator=None, snippet=None, currency=None,
         units=None, as_of=None, period=None, quote="exact", formula=None):
    vid = D.value_id(pay_line or f"{cid}|{D.FY}", field, item or "")
    src_kind = source.split("-")[0] if source else None
    row = dict(value_id=vid, company_id=cid, fiscal_year=D.FY, pay_line_id=pay_line, field_name=field, item_key=item,
               **typed(value), currency=currency, units=units, source_id=source, locator=locator, snippet=snippet,
               quote_match=quote if source else None, as_of_date=as_of,
               period_start=period[0] if period else None, period_end=period[1] if period else None,
               source_type={"AR": "annual_report", "RR": "remuneration_report", "LEI": "lei_record"}.get(src_kind),
               formula_version=formula, extraction_run_id=D.RUN_ID, extracted_at=D.EXTRACTED_AT)
    ffv.append(row)
    VALUE_INDEX[(cid, pay_line, field, item)] = row
    return row


def source_for(cid, field):
    fd = FIELD[field]
    kind, loc = SOURCE_BY_CATEGORY.get(fd.data_category, ("RR", "RR p.5, Table 1 Remuneration"))
    if fd.data_category == "Identity" and field in AR_IDENTITY:
        kind, loc = "AR", "AR p.2, About the company"
    return f"{kind}-2025-{cid}" if kind != "LEI" else f"LEI-{cid}", loc


def linked_columns(table_name):
    """(column, field) pairs for catalogue-linked columns, one per field (prefer the column named like the field)."""
    t = schema.table(table_name)
    by_field: dict[str, str] = {}
    for c in t.columns:
        if c.field_id and c.field_id not in by_field:
            by_field[c.field_id] = c.name
        if c.field_id and c.name == c.field_id:
            by_field[c.field_id] = c.name
    return [(col, fld) for fld, col in by_field.items()]


for row in D.DIM_COMPANY:
    cid = row["company_id"]
    for col, fld in linked_columns("dim_company"):
        if row.get(col) is None:
            continue
        src, loc = source_for(cid, fld)
        emit(cid, fld, row[col], source=src, locator=f"{loc}: {fld}", snippet=f"{fld.replace('_', ' ').title()}: {fmt_value(row[col])}")
for row in D.COMPANY_NAME_ALIAS:
    emit(row["company_id"], "other_names", row["alias"], item=row["alias"], source=f"AR-2025-{row['company_id']}",
         locator="AR p.2, Company history", snippet=f"formerly / also known as {row['alias']}")
for row in D.FACT_COMPANY_YEAR:
    cid = row["company_id"]
    for col, fld in linked_columns("fact_company_year"):
        v = row.get(col)
        if v is None:
            continue
        money = FIELD[fld].format in MONEY_FORMATS
        if fld == "market_cap_band":
            emit(cid, fld, v, locator="Derived: shares_outstanding x share_price, converted to EUR",
                 formula="market_cap_band_v1", as_of=D.FY_END)
            continue
        src, loc = source_for(cid, fld)
        emit(cid, fld, v, source=src, locator=loc, snippet=f"{fld.replace('_', ' ').capitalize()} {fmt_value(v)}",
             currency=row["reporting_currency"] if money else None,
             units=("units" if fld == "share_price" else row["units"]) if money else None,
             as_of=None if fld in FLOW_FIELDS else D.FY_END,
             period=(D.FY_START, D.FY_END) if fld in FLOW_FIELDS else None)
for row in D.COMPANY_HOLDER:
    cid = row["company_id"]
    emit(cid, "largest_holders", row["capital_pct"], item=row["holder_name"], source=f"AR-2025-{cid}",
         locator=f"AR p.14, Largest shareholders, row {row['holder_rank']}",
         snippet=f"{row['holder_name']} {row['capital_pct']:.1f}% of capital, {row['votes_pct']:.1f}% of votes",
         as_of=row["as_of_date"])
for row in D.COMPANY_BREAKDOWN:
    cid, fld = row["company_id"], BREAKDOWN_FIELD[(row["breakdown_type"], row["metric"])]
    fcy = next(x for x in D.FACT_COMPANY_YEAR if x["company_id"] == cid)
    money = row["metric"] == "revenue"
    emit(cid, fld, row["value"], item=row["item_name"], source=f"AR-2025-{cid}", locator="AR p.95, Note 3 Operating segments",
         snippet=f"{row['item_name']} {fmt_value(row['value'])}", currency=fcy["reporting_currency"] if money else None,
         units="millions" if money else "units", as_of=None if money else D.FY_END,
         period=(D.FY_START, D.FY_END) if money else None)
for row in D.FACT_PAY_POLICY:
    cid = row["company_id"]
    for col, fld in linked_columns("fact_pay_policy"):
        if row.get(col) is not None:
            emit(cid, fld, row[col], source=f"RR-2025-{cid}", locator="RR p.3, Remuneration policy",
                 snippet=f"{fld.replace('_', ' ').capitalize()}: {row[col]}")
for row in D.FACT_PAY_LINE:
    cid, pid = row["company_id"], row["pay_line_id"]
    end = dt.date(2025, 3, 31) if row.get("months_in_role") == 3 else D.FY_END
    for col, fld in linked_columns("fact_pay_line"):
        v = row.get(col)
        if v is None:
            continue
        money = FIELD[fld].format in MONEY_FORMATS
        quote = "none" if (cid, row["role_code"], col) in QUOTE_NONE else ("normalised" if cid == "SRS" and money else "exact")
        shown = f"{v:,}".replace(",", " ") if cid == "SRS" and money else fmt_value(v)
        emit(cid, fld, v, pay_line=pid, source=f"RR-2025-{cid}",
             locator=f"RR p.5, Table 1, row '{row['role_title']}', column '{col.replace('_', ' ')}'",
             snippet=f"{row['role_title']}: {col.replace('_', ' ')} {shown}",
             currency=row["pay_currency"] if money else None, units=row["units"] if money else None,
             period=(D.FY_START, end), quote=quote)

# =============================================================================== provenance: fact_check_result
fcr: list[dict] = []


def result(vrow, code, res, note=None, incomplete_reason=None, review_decision=None, reviewed_by=None, reviewed_at=None):
    fcr.append(dict(result_id=D.result_id(vrow["value_id"], code), value_id=vrow["value_id"], check_code=code,
                    company_id=vrow["company_id"], field_name=vrow["field_name"], result=res,
                    score={"pass": 1, "fail": 0}.get(res), note=note, incomplete_reason=incomplete_reason,
                    review_decision=review_decision, reviewed_by=reviewed_by, reviewed_at=reviewed_at,
                    checked_at=D.CHECKED_AT))


for v in ffv:  # SRC-1: the quoted source text is found in the document (Conor 02 Nov)
    if v["source_id"]:
        result(v, "SRC-1", "pass" if v["quote_match"] in ("exact", "normalised") else "fail",
               note=None if v["quote_match"] != "none" else "Quote not found in RR-2025 p.5; value kept as extracted")
for v in ffv:
    fld = v["field_name"]
    if fld == "lei":
        result(v, "LEI-1", "pass")
    if fld == "base_salary":
        result(v, "NUM-04", "not_run", note="Plausible ranges not approved by Allshares (gate stays NOT RUN)")
    if fld == "headcount":
        fcy = next(x for x in D.FACT_COMPANY_YEAR if x["company_id"] == v["company_id"])
        ok = fcy["fte"] <= fcy["headcount"]
        result(v, "NUM-05", "pass" if ok else "fail",
               note=None if ok else f"FTE {fcy['fte']:,} is above headcount {fcy['headcount']:,}; recorded, not corrected")
    if fld == "revenue_by_segment" and v["item_key"] == next(r["item_name"] for r in D.COMPANY_BREAKDOWN
                                                              if r["company_id"] == v["company_id"] and r["metric"] == "revenue" and r["breakdown_type"] == "segment"):
        segs = sum(r["value"] for r in D.COMPANY_BREAKDOWN if r["company_id"] == v["company_id"]
                   and r["breakdown_type"] == "segment" and r["metric"] == "revenue")
        rev = next(x["revenue"] for x in D.FACT_COMPANY_YEAR if x["company_id"] == v["company_id"])
        gap = abs(segs - rev) / rev
        result(v, "SEG-1", "pass" if gap <= 0.01 else "review",
               note=f"Segments sum to {segs:,.1f} vs revenue {rev:,.1f} ({gap:.1%})" if gap > 0.01 else None,
               review_decision="Accepted: gap is the unallocated and eliminations line" if gap > 0.01 else None,
               reviewed_by="Allshares D&A team" if gap > 0.01 else None,
               reviewed_at=dt.datetime(2026, 11, 9, 10, 30) if gap > 0.01 else None)
holders_seen = set()
for v in ffv:
    if v["field_name"] != "largest_holders" or v["company_id"] in holders_seen:
        continue
    holders_seen.add(v["company_id"])
    hs = [h for h in D.COMPANY_HOLDER if h["company_id"] == v["company_id"]]
    total = sum(h["capital_pct"] for h in hs)
    result(v, "NUM-07", "pass" if total <= 100 else "fail", note=f"Listed holders hold {total:.1f}% of capital")
    dates = {h["as_of_date"] for h in hs}
    result(v, "DER-07", "pass" if len(dates) == 1 else "review",
           note=None if len(dates) == 1 else "Holdings have different as-of dates (" + ", ".join(sorted(d.isoformat() for d in dates)) + ")")
for p in D.FACT_PAY_LINE:
    pid, cid = p["pay_line_id"], p["company_id"]
    tot = VALUE_INDEX.get((cid, pid, "total_remuneration", None))
    parts = [p.get(k) for k in ("base_salary", "benefits_value", "pension_contribution", "sti_paid")]
    if tot is not None:
        if all(x is None for x in parts):
            result(tot, "XF-01", "not_run", note="No components disclosed (board fee only)")
        else:
            s = sum(x or 0 for x in parts)
            ok = abs(s - p["total_remuneration"]) <= 0.005 * p["total_remuneration"]
            result(tot, "XF-01", "pass" if ok else "fail",
                   note=None if ok else f"Components sum to {s:,} vs stated total {p['total_remuneration']:,}; "
                                        f"the document's total includes items not listed (PAY-1)")
    cur = VALUE_INDEX.get((cid, pid, "pay_currency", None))
    home = next(r["currency_code"] for r in D.REF["ref_country_currency"]
                if r["code"] == next(c["country"] for c in D.COMPANIES if c["company_id"] == cid))
    if cur is not None:
        ok = p["pay_currency"] in (home, "EUR", "USD", "GBP", "CHF")
        result(cur, "CUR-1", "pass" if ok else "review",
               note=None if ok else f"{p['pay_currency']} is not the country's currency ({home}) or EUR/USD/GBP/CHF",
               review_decision=None if ok else "Pending: confirm the COO is paid from the Singapore office")
    ah = VALUE_INDEX.get((cid, pid, "aggregate_headcount", None))
    if p.get("is_aggregated"):
        result(ah, "PAY-5", "pass" if p.get("aggregate_headcount") else "fail")
    mir = VALUE_INDEX.get((cid, pid, "months_in_role", None))
    if p.get("period_coverage") == "part_year" and mir is not None:
        result(mir, "PAY-3", "pass", note="Part-year line: amount as paid, months_in_role = 3 (not annualised)")

data["fact_field_value"] = ffv
data["fact_check_result"] = fcr

# =============================================================================== workbook
wb = Workbook()
wb.remove(wb.active)
SHEET_ROWS: dict[str, dict] = {}  # table -> {key tuple: excel row}


def column_meta(t):
    pk = set(t.primary_key)
    fks = {}
    for r in schema.relationships:
        if r.from_table == t.name:
            for c, tc in zip(r.from_columns, r.to_columns):
                fks.setdefault(c, f"→ {r.to_table}")
    return pk, fks


def number_format(col_type, name, values):
    ty = col_type.upper()
    if ty == "DATE":
        return "yyyy-mm-dd"
    if ty == "TIMESTAMP":
        return "yyyy-mm-dd hh:mm:ss"
    if ty == "INT64":
        return "0" if name in ("fiscal_year", "holder_rank", "role_order", "sort_order", "months_in_role") else "#,##0"
    if ty == "NUMERIC":
        if name.endswith("_pct"):
            return "0.0"
        if name in ("score", "weight"):
            return "General"
        nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        return "#,##0" if all(float(v).is_integer() for v in nums) else "#,##0.0"
    return "General"


MIN_WIDTH = {"TIMESTAMP": 20, "DATE": 12}


def header_block(ws, title, layer, subtitle, ncols):
    color = LAYER_COLOR[layer]
    ws.sheet_properties.tabColor = color
    ws.cell(1, 1, title).font = f(14, True, "FFFFFF")
    ws.cell(1, max(ncols, 6), LAYER_LABEL[layer]).font = f(10, True, "FFFFFF")
    ws.cell(1, max(ncols, 6)).alignment = Alignment(horizontal="right")
    for c in range(1, max(ncols, 6) + 1):
        ws.cell(1, c).fill = fill(color)
        ws.cell(2, c).fill = fill(LAYER_TINT[layer])
    ws.cell(2, 1, subtitle).font = f(9, italic=True, color="44505C")
    ws.row_dimensions[1].height = 22


def write_table(t, rows):
    ws = wb.create_sheet(t.name[:31])
    cols = t.columns
    pk, fks = column_meta(t)
    sub = f"{t.description.rstrip('.')}. Grain: {t.grain}." if t.description else f"Grain: {t.grain}."
    header_block(ws, t.name, t.layer, sub, len(cols))
    tint = LAYER_TINT[t.layer]
    for j, c in enumerate(cols, 1):
        meta = [c.type + ("" if c.mode == "NULLABLE" else f" {c.mode}")]
        if c.name in pk:
            meta.append("PK")
        if c.name in fks:
            meta.append(fks[c.name])
        if c.field_id:
            meta.append(f"field: {c.field_id}")
        if c.needs_confirmation:
            meta.append("† confirm")
        m = ws.cell(3, j, " · ".join(meta))
        m.font = f(8, italic=True, color="5B6573")
        m.fill = fill("F7F8FA")
        h = ws.cell(4, j, c.name)
        h.font = f(10, True, "FFFFFF")
        h.fill = fill(LAYER_COLOR[t.layer] if c.name not in pk else "1F2933")
        h.border = Border(bottom=THIN)
        if c.description:
            h.comment = Comment(c.description[:300], "schema.json")
    unknown = {k for r in rows for k in r} - {c.name for c in cols}
    if unknown:
        raise KeyError(f"{t.name}: data has columns not in the schema: {sorted(unknown)}")
    formats = {c.name: number_format(c.type, c.name, [r.get(c.name) for r in rows]) for c in cols}
    for i, r in enumerate(rows, FIRST_DATA_ROW):
        for j, c in enumerate(cols, 1):
            v = r.get(c.name)
            cell = ws.cell(i, j, v)
            cell.font = f(9, bold=c.name in pk)
            cell.number_format = formats[c.name]
            cell.border = Border(bottom=THIN)
            if c.name in pk:
                cell.fill = fill(tint)
    finish_sheet(ws, cols, len(rows))
    for j, c in enumerate(cols, 1):
        letter = get_column_letter(j)
        ws.column_dimensions[letter].width = max(ws.column_dimensions[letter].width, MIN_WIDTH.get(c.type.upper(), 0))
    if t.name == "fact_check_result":
        col = get_column_letter([c.name for c in cols].index("result") + 1)
        rng = f"{col}{FIRST_DATA_ROW}:{col}{FIRST_DATA_ROW + max(len(rows), 1) - 1}"
        for val, hexc in RESULT_FILL.items():
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{val}"'], fill=fill(hexc)))
    return ws


def finish_sheet(ws, cols, nrows):
    last_col = get_column_letter(max(len(cols), 1))
    ws.freeze_panes = ws.cell(FIRST_DATA_ROW, 1)
    ws.auto_filter.ref = f"A4:{last_col}{FIRST_DATA_ROW + max(nrows, 1) - 1}"
    for j in range(1, len(cols) + 1):
        letter = get_column_letter(j)
        width = max(len(str(ws.cell(r, j).value or "")) for r in range(4, FIRST_DATA_ROW + max(nrows, 1)))
        meta_w = len(str(ws.cell(3, j).value or "")) * 0.8
        ws.column_dimensions[letter].width = min(max(width + 2, meta_w, 9), 55)


# --- order: delivery, derived view, provenance, catalogue, ref --------------------------------
preferred = ["dim_company", "company_name_alias", "fact_company_year", "company_holder", "VIEW", "company_breakdown",
             "fact_pay_policy", "fact_pay_line", "pay_line_role", "pay_line_total_component",
             "dim_source", "fact_field_value", "fact_check_result", "dim_field", "dim_check", "bridge_field_check"]
rest = [t.name for t in table_order(schema) if t.name not in preferred]
order = preferred + rest

readme = wb.create_sheet("README", 0)
trace = wb.create_sheet("Trace", 1)
written: dict[str, object] = {}
for name in order:
    if name == "VIEW":
        continue
    t = schema.table(name)
    if t is None:
        continue
    written[name] = write_table(t, data.get(name, []))
    if name == "company_holder":
        pass

# --- derived view with live formulas -----------------------------------------------------------
view = schema.view("v_company_ownership")
holder = schema.table("company_holder")
hcol = {c.name: get_column_letter(i) for i, c in enumerate(holder.columns, 1)}
last = FIRST_DATA_ROW + len(D.COMPANY_HOLDER) + 50   # spare rows so added holders are included


def R(col):
    return f"company_holder!${hcol[col]}${FIRST_DATA_ROW}:${hcol[col]}${last}"


vws = wb.create_sheet(view.name, order.index("VIEW") + 2)
vcols = view.group_by + [c.name for c in view.columns]
header_block(vws, view.name, "view", f"{view.description}. Live Excel formulas over company_holder, "
             "mirroring the SQL view; add or edit a holder and these values change.", len(vcols))
expr = {c.name: c for c in view.columns}
for j, name in enumerate(vcols, 1):
    m = vws.cell(3, j, "key" if name in view.group_by else f"{expr[name].type} · ƒ {expr[name].expression}")
    m.font = f(8, italic=True, color="5B6573")
    m.fill = fill("F7F8FA")
    h = vws.cell(4, j, name)
    h.font = f(10, True, "FFFFFF")
    h.fill = fill(LAYER_COLOR["view"])
    if name in expr and expr[name].description:
        h.comment = Comment(expr[name].description, "schema.json")
for i, c in enumerate(D.COMPANIES, FIRST_DATA_ROW):
    key = f"{R('company_id')},$A{i},{R('fiscal_year')},$B{i}"
    maxv = f"_xlfn.MAXIFS({R('votes_pct')},{key})"
    top_row = f"SUMPRODUCT(MAX(({R('company_id')}=$A{i})*({R('fiscal_year')}=$B{i})*({R('votes_pct')}={maxv})*ROW({R('votes_pct')})))"
    formulas = {
        "company_id": c["company_id"],
        "fiscal_year": D.FY,
        "holder_count": f"=COUNTIFS({key})",
        "controlling_owner": f'=COUNTIFS({key},{R("votes_pct")},">=20")>0',
        "controlling_owner_name": f'=IF(D{i},INDEX(company_holder!${hcol["holder_name"]}:${hcol["holder_name"]},{top_row}),"")',
        "ownership_type": f'=IF(D{i},INDEX(company_holder!${hcol["holder_type"]}:${hcol["holder_type"]},{top_row}),"")',
        "pe_stake_5pct": f'=COUNTIFS({key},{R("holder_type")},"private_equity",{R("capital_pct")},">=5")>0',
        "ownership_as_of": f"=_xlfn.MAXIFS({R('as_of_date')},{key})",
        "as_of_consistent": f"=COUNTIFS({key},{R('as_of_date')},H{i})=C{i}",
        "capital_listed_pct": f"=SUMIFS({R('capital_pct')},{key})",
        "votes_listed_pct": f"=SUMIFS({R('votes_pct')},{key})",
    }
    for j, name in enumerate(vcols, 1):
        cell = vws.cell(i, j, formulas[name])
        cell.font = f(9, bold=name in view.group_by)
        cell.border = Border(bottom=THIN)
        cell.number_format = {"ownership_as_of": "yyyy-mm-dd", "capital_listed_pct": "0.0", "votes_listed_pct": "0.0",
                              "fiscal_year": "0"}.get(name, "General")
note_row = FIRST_DATA_ROW + len(D.COMPANIES) + 1
vws.cell(note_row, 3, "Rules to confirm with Allshares: controlling owner = a holder with 20% or more of the votes; "
         "PE stake = a 'private_equity' holder with 5% or more of the capital. If two holders tie on the top votes, "
         "the name shown is the lower one in company_holder.").font = f(8, italic=True, color="5B6573")
finish_sheet(vws, vcols, len(D.COMPANIES))
for j, name in enumerate(vcols, 1):
    vws.column_dimensions[get_column_letter(j)].width = max(16, min(len(name) + 4, 30))
vws.column_dimensions["E"].width = 28

# --- README --------------------------------------------------------------------------------------
readme.sheet_properties.tabColor = "111827"
readme.column_dimensions["A"].width = 30
readme.column_dimensions["B"].width = 26
readme.column_dimensions["C"].width = 12
readme.column_dimensions["D"].width = 90
readme["A1"] = "Allshares CDP schema: worked example (FY2025)"
readme["A1"].font = f(16, True)
readme["A2"] = (f"Every table in schema/schema.json (version {VERSION}) on its own sheet, filled for three FICTIONAL "
                "companies. All names, people, holders, IDs and numbers are invented to show how the schema is used.")
readme["A2"].font = f(9, italic=True, color="B91C1C")
r = 4
readme.cell(r, 1, "Companies").font = f(11, True)
r += 1
for c, what in zip(D.COMPANIES, [
        "Controlling family foundation with dual-class votes, a PE holder, a part-year CEO, an aggregate executive line, and the CEO also on the board (two pay lines, one person).",
        "No controlling owner, a PE stake, a CEO who is also acting CFO (one pay line, two roles in pay_line_role), and a total that does not reconcile (XF-01 fail).",
        "State-controlled, a holder with a different as-of date (DER-07 review), FTE above headcount (NUM-05 fail), a COO paid in SGD (CUR-1 review), and a quote not found (SRC-1 fail)."]):
    readme.cell(r, 1, f"{c['company_id']}: {c['name']}").font = f(10, True)
    readme.cell(r, 2, f"{c['country']} · {c['currency']}").font = f(9)
    readme.cell(r, 4, what).font = f(9)
    readme.cell(r, 4).alignment = Alignment(wrap_text=True, vertical="top")
    readme.row_dimensions[r].height = 26
    r += 1
r += 1
readme.cell(r, 1, "Colour legend (tab and header colour = layer)").font = f(11, True)
r += 1
for layer in ["dim", "fact", "child", "view", "provenance", "catalogue", "ref"]:
    readme.cell(r, 1, LAYER_LABEL[layer]).font = f(10, True, "FFFFFF")
    readme.cell(r, 1).fill = fill(LAYER_COLOR[layer])
    readme.cell(r, 4, {
        "dim": "Stable company attributes (dim_company).",
        "fact": "Values per company-year or per pay line (fact_company_year, fact_pay_policy, fact_pay_line).",
        "child": "One row per list item: holders, aliases, breakdowns, roles per pay line, total components.",
        "view": "Calculated from a child table, never stored. In this workbook: live Excel formulas.",
        "provenance": "Where every value came from (fact_field_value) and what the checks said (fact_check_result).",
        "catalogue": "The field catalogue, check catalogue and which checks apply to which fields (from the workbooks).",
        "ref": "Allowed values for coded columns. 'Example (worked example, fictional)' marks values made up for this file.",
    }[layer]).font = f(9)
    r += 1
r += 1
readme.cell(r, 1, "Inside each sheet").font = f(11, True)
r += 1
for a, b in [("Row 3 (grey, italic)", "BigQuery type and mode · PK · → FK target · catalogue field · † = column to confirm"),
             ("Dark header cell", "Primary-key column (its values are bold on a tinted background)"),
             ("Header comment", "Hover a column header to read its description from schema.json"),
             ("Check results", "fact_check_result.result: green pass · red fail · yellow review · grey not_run"),
             ("IDs", "pay_line_id, value_id and result_id are deterministic UUID v5 (same key, same ID on every re-run)")]:
    readme.cell(r, 1, a).font = f(9, True)
    readme.cell(r, 4, b).font = f(9)
    r += 1
r += 1
readme.cell(r, 1, "Sheets").font = f(11, True)
readme.cell(r, 2, "Layer").font = f(9, True)
readme.cell(r, 3, "Rows").font = f(9, True)
readme.cell(r, 4, "Grain").font = f(9, True)
r += 1
for name in ["Trace"] + [n if n != "VIEW" else view.name for n in order if n == "VIEW" or schema.table(n)]:
    if name == "Trace":
        layer, grain = None, "Follows one value (NVK CEO base salary) through every table"
    elif name == view.name:
        layer, grain = "view", "one row per company per fiscal year"
    else:
        t = schema.table(name)
        layer, grain = t.layer, t.grain
    link = readme.cell(r, 1, name)
    link.hyperlink = f"#'{name}'!A1"
    link.font = f(9, color="1D4ED8")
    if layer:
        readme.cell(r, 2, LAYER_LABEL[layer]).font = f(9, color=LAYER_COLOR[layer], bold=True)
        readme.cell(r, 3, f"=COUNTA('{name}'!A{FIRST_DATA_ROW}:A5000)").font = f(9)
    readme.cell(r, 4, grain).font = f(9)
    r += 1

# --- Trace: one value through every table (cross-sheet links in green) --------------------------
GREEN = "008000"
trace.sheet_properties.tabColor = "111827"
trace.column_dimensions["A"].width = 26
trace.column_dimensions["B"].width = 34
trace.column_dimensions["C"].width = 60
trace["A1"] = "Trace: Nordvik Kraft (NVK), CEO Anna Lind, base salary FY2025"
trace["A1"].font = f(14, True)
trace["A2"] = "Each green cell links to the cell in the table sheet; change the table and this page follows."
trace["A2"].font = f(9, italic=True, color="5B6573")
ceo = D.FACT_PAY_LINE[0]
pl_sheet, pl_cols = written["fact_pay_line"], [c.name for c in schema.table("fact_pay_line").columns]
ffv_cols = [c.name for c in schema.table("fact_field_value").columns]
fcr_cols = [c.name for c in schema.table("fact_check_result").columns]
v_base = VALUE_INDEX[("NVK", ceo["pay_line_id"], "base_salary", None)]
ffv_row = FIRST_DATA_ROW + ffv.index(v_base)
fcr_rows = [FIRST_DATA_ROW + i for i, x in enumerate(fcr) if x["value_id"] == v_base["value_id"]]
pl_row = FIRST_DATA_ROW
src_row = FIRST_DATA_ROW + [s["source_id"] for s in D.DIM_SOURCE].index(v_base["source_id"])
src_cols = [c.name for c in schema.table("dim_source").columns]


PRIO = get_column_letter([c.name for c in schema.table("dim_field").columns].index("priority") + 1)


def link(sheet, col_names, row, col):
    return f"='{sheet}'!{get_column_letter(col_names.index(col) + 1)}{row}"


steps = [
    ("1. Source document", "dim_source.title", link("dim_source", src_cols, src_row, "title"), "Registered source the value was read from"),
    ("", "dim_source.gcs_path", link("dim_source", src_cols, src_row, "gcs_path"), ""),
    ("2. Extracted value", "fact_field_value.value_numeric", link("fact_field_value", ffv_cols, ffv_row, "value_numeric"),
     "As read, in the pay table's currency and units, never corrected"),
    ("", "fact_field_value.currency / units", f"={link('fact_field_value', ffv_cols, ffv_row, 'currency')[1:]}&\" \"&{link('fact_field_value', ffv_cols, ffv_row, 'units')[1:]}", ""),
    ("", "fact_field_value.locator", link("fact_field_value", ffv_cols, ffv_row, "locator"), "Where in the document"),
    ("", "fact_field_value.snippet", link("fact_field_value", ffv_cols, ffv_row, "snippet"), "Verbatim text"),
    ("", "fact_field_value.quote_match", link("fact_field_value", ffv_cols, ffv_row, "quote_match"), "Result of the quote check"),
]
for k, rr in enumerate(fcr_rows):
    steps.append(("3. Check results" if k == 0 else "", link("fact_check_result", fcr_cols, rr, "check_code"),
                  link("fact_check_result", fcr_cols, rr, "result"), "fact_check_result: one row per check run on this value"))
steps += [
    ("4. Delivered value", "fact_pay_line.base_salary", link("fact_pay_line", pl_cols, pl_row, "base_salary"), "Wide delivery table used for benchmarking"),
    ("", "fact_pay_line.role_code", link("fact_pay_line", pl_cols, pl_row, "role_code"), "Primary role (→ ref_role)"),
    ("", "fact_pay_line.pay_line_id", link("fact_pay_line", pl_cols, pl_row, "pay_line_id"),
     "UUID v5 of NVK|2025|individual_executive|ceo|anna lind"),
    ("5. Catalogue", "dim_field: base_salary priority",
     f"=INDEX(dim_field!${PRIO}:${PRIO},MATCH(\"base_salary\",dim_field!$A:$A,0))", "P1 · Required · High (Sheet1 overlay)"),
    ("", "Checks that apply (bridge_field_check)", '=COUNTIFS(bridge_field_check!$A:$A,"base_salary")', "Rows in bridge_field_check for base_salary"),
]
trace.cell(4, 1, "Step").font = f(9, True)
trace.cell(4, 2, "Where").font = f(9, True)
trace.cell(4, 3, "Value").font = f(9, True)
trace.cell(4, 4, "Why").font = f(9, True)
trace.column_dimensions["D"].width = 60
for i, (a, b, c, d) in enumerate(steps, 5):
    trace.cell(i, 1, a).font = f(9, True)
    cb = trace.cell(i, 2, b)
    cb.font = f(9, color=GREEN if str(b).startswith("=") else "1F2933")
    cc = trace.cell(i, 3, c)
    cc.font = f(9, color=GREEN)
    cc.alignment = Alignment(horizontal="left")
    trace.cell(i, 4, d).font = f(9, italic=True, color="5B6573")

wb.calculation.fullCalcOnLoad = True
OUT.parent.mkdir(exist_ok=True)
wb.save(OUT)
print(f"Wrote {OUT} with {len(wb.sheetnames)} sheets; fact_field_value {len(ffv)} rows, fact_check_result {len(fcr)} rows")
