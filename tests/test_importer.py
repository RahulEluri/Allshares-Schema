import shutil
from pathlib import Path

import openpyxl
import pytest

from schema_core.conflicts import list_conflicts
from schema_core.importer.draft import build_draft
from schema_core.importer.readers import WorkbookReader
from schema_core.importer.reimport import apply_import_items, import_diff
from schema_core.importer.snapshot import build_snapshot
from schema_core.store import ROOT, SchemaStore
from schema_core.validation import errors, validate

INPUTS = ROOT / "inputs"


@pytest.fixture(scope="module")
def snap():
    return build_snapshot()


@pytest.fixture(scope="module")
def draft(snap):
    return build_draft(snap)


@pytest.fixture
def live(tmp_path, snap):
    store = SchemaStore(tmp_path / "schema")
    store.initialize(build_draft(snap), actor="test", reason="first import")
    return store


def _copy_books(tmp_path) -> dict[str, Path]:
    out = {}
    for key, name in [("fields_book", "Book1.xlsx"), ("checks_book", "allshares_field_checks.xlsx"),
                      ("gates_book", "Allshares_Part1_gate_reference_02Nov.xlsx")]:
        dst = tmp_path / name
        shutil.copy(INPUTS / name, dst)
        out[key] = dst
    return out


# ------------------------------------------------------------------ counts and shape

def test_catalogue_counts(snap):
    status = [f.status for f in snap.fields]
    assert status.count("active") == 55
    assert status.count("new") == 14          # 13 Conor tracker fields not in Book1 + role_code (playground)
    assert status.count("parked") == 3
    gates = [c for c in snap.checks if c.kind == "gate"]
    assert len([c for c in gates if not c.undefined]) == 37   # All Checks
    assert sorted(c.code for c in gates if c.undefined) == ["DER-10", "DER-11"]
    assert len([c for c in snap.checks if c.kind == "rule"]) == 24
    assert len(snap.field_checks) == 386


def test_importer_quirks(snap):
    names = [f.name for f in snap.fields]
    assert len(names) == len(set(names))
    assert not any(n.endswith(")") or n == "55" for n in names)           # section headers / total row skipped
    legal, other = (next(f for f in snap.fields if f.name == n) for n in ("legal_name", "other_names"))
    assert legal.protocol_id == other.protocol_id == "C01"                 # protocol IDs aren't unique
    cik = next(f for f in snap.fields if f.name == "cik")
    assert cik.protocol_id == "Not in protocol"
    assert next(f for f in snap.fields if f.name == "head_office_city").cdp_column == "hq_city"
    assert next(f for f in snap.fields if f.name == "base_salary").priority == "P1"


def test_check_names_from_all_checks_and_rules(snap):
    c = {x.code: x for x in snap.checks}
    assert c["CORE-01"].name == "Locator and verbatim snippet present"
    assert c["NUM-09"].status == "hold_off"
    assert c["STI-1"].parent_gates == ["NUM-11"] and c["STI-1"].status == "to_do"
    assert c["PAY-1"].parent_gates == ["XF-01", "XF-02"]
    assert c["LEI-1"].status == "existing"
    assert c["NUM-06"].proposed_change["suggestion"].startswith("STI and LTI")


def test_pairs_nullable_scores_and_notes(snap):
    pair = next(p for p in snap.field_checks if p.field_name == "largest_holders" and p.check_code == "DER-10")
    assert pair.score is None and pair.weight is None
    ids = {n.id for n in snap.notes}
    assert {"LB-2", "LB-4", "LB-5", "QM-4"} <= ids
    assert snap.internal.provisional_ranges and snap.internal.range_notes


def test_draft_tables(draft):
    names = {t.name for t in draft.tables}
    expected = {
        "dim_field", "dim_check", "bridge_field_check", "dim_source", "fact_field_value", "fact_check_result",
        "dim_company", "company_name_alias", "fact_company_year", "company_holder", "company_breakdown",
        "fact_pay_policy", "fact_pay_line", "pay_line_total_component",
    }
    refs = {t.name for t in draft.tables if t.layer == "ref"}
    assert len(refs) == 22 and expected <= names and len(names) == 37
    pay = draft.table("fact_pay_line")
    assert pay.column("role_title").cdp_alias == "role_title_internal"
    assert pay.column("months_in_role").validation_rule.max == 12
    assert pay.column("sti_target_value").type == "NUMERIC" and pay.column("sti_target_basis").needs_confirmation
    assert pay.column("base_salary").mode == "NULLABLE"                    # requirement is metadata only
    assert pay.column("base_salary").requirement == "Required"
    assert not any("annualised" in c.name for c in pay.columns)
    fcy = draft.table("fact_company_year")
    assert fcy.primary_key == ["company_id", "fiscal_year"]
    assert not {"controlling_owner", "ownership_type", "pe_stake_5pct", "holder_list_n"} & {c.name for c in fcy.columns}
    ffv = draft.table("fact_field_value")
    assert ffv.partition_by == "extracted_at" and ffv.cluster_by == ["company_id", "field_name"]


def test_draft_validates_and_places_all_active_fields(draft):
    issues = validate(draft)
    assert errors(issues) == []
    assert not [i for i in issues if i.code == "field_not_placed"]


def test_conflicts_listed(draft):
    ids = {c["id"] for c in list_conflicts(draft)}
    assert {"controlling_owner_meaning", "country_list_short", "unconfirmed_values", "parked_fields",
            "module_weights", "confirm_columns", "empty_ref_tables", "undefined_checks"} <= ids


# ------------------------------------------------------------------ re-import

def test_reimport_unchanged_is_empty(live, snap):
    assert import_diff(live, snap)["items"] == []


def test_reimport_one_cell_edit(live, tmp_path):
    books = _copy_books(tmp_path)
    wb = openpyxl.load_workbook(books["fields_book"])
    ws = wb["Pay Data"]
    for row in ws.iter_rows(min_row=2):
        if row[1].value == "base_salary":
            row[5].value = "Fixed base salary (edited)"
    wb.save(books["fields_book"])
    diff = import_diff(live, build_snapshot(WorkbookReader(overrides=books)))
    assert len(diff["items"]) == 1
    item = diff["items"][0]
    assert item["id"] == "fields:base_salary" and list(item["changes"]) == ["description"]

    res = apply_import_items(live, [item["id"]], live.version(), actor="ui",
                             snap=build_snapshot(WorkbookReader(overrides=books)))
    assert res.ok
    s = live.load()[0]
    assert s.catalogue.field("base_salary").description == "Fixed base salary (edited)"
    assert s.table("fact_pay_line").column("base_salary").description == "Fixed base salary (edited)"  # lineage follows
    assert live.changelog()[-1]["source"] == "import"


def test_app_owned_edits_survive_and_removals_flag(live, tmp_path, snap):
    live.apply([{"op": "update_ref_value", "table": "ref_check_result", "code": "pass", "changes": {"label": "PASS!"}},
                {"op": "add_field", "field": {"name": "app_only_field", "format": "Text"}}],
               expected_version=live.version(), actor="ui")
    diff = import_diff(live, snap)
    by_id = {i["id"]: i for i in diff["items"]}
    assert by_id["ref_values:ref_check_result.pass"]["app_owned"] is True
    assert "fields:app_only_field" not in by_id                 # app-created items are not "removed"
    assert live.load()[0].table("ref_check_result").rows[0].label == "PASS!"

    # Remove a check from the workbook: flagged, not applicable.
    books = _copy_books(tmp_path)
    wb = openpyxl.load_workbook(books["checks_book"])
    ws = wb["All Checks"]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == "XF-03":
            ws.delete_rows(row[0].row)
            break
    wb.save(books["checks_book"])
    snap2 = build_snapshot(WorkbookReader(overrides=books))
    item = next(i for i in import_diff(live, snap2)["items"] if i["id"] == "checks:XF-03")
    assert item["kind"] == "removed" and not item["applicable"]
    with pytest.raises(ValueError):
        apply_import_items(live, ["checks:XF-03"], live.version(), actor="ui", snap=snap2)


def test_fixed_sets_sheet_is_picked_up(tmp_path):
    books = _copy_books(tmp_path)
    wb = openpyxl.load_workbook(books["checks_book"])
    ws = wb.create_sheet("Fixed Sets")
    ws.append(["Field", "Field ID", "Data category", "Checked by", "Allowed value", "Meaning / when to use",
               "Source wording seen in first 50 that maps here", "Count in first 50", "Status", "List source"])
    ws.append(["country_code", "C08", "Identity", "COD-01", "SE", "Sweden", "Sverige", 12, "In use", "ISO 3166"])
    ws.append(["country_code", "C08", "Identity", "COD-01", "FI", "Finland", None, 8, "Proposed: confirm with Allshares", "ISO 3166"])
    ws.append(["months_in_role", "", "Pay: fixed", "PAY-3", "1 to 12", "Months held", None, None, "In use", "Conor"])
    ws.append(["sector_code", "C10", "Sector", "COD-01", "NACE class 'NN.NN'", "", None, None, "In use", "NACE"])
    wb.save(books["checks_book"])
    snap = build_snapshot(WorkbookReader(overrides=books))
    assert [r.code for r in snap.ref_values["ref_country"]] == ["SE", "FI"]
    assert snap.rules["months_in_role"].max == 12 and snap.rules["sector_code"].kind == "pattern"
    assert "fixed_sets" not in snap.missing_datasets
    d = build_draft(snap)
    assert any(c["id"] == "unconfirmed_values" for c in list_conflicts(d))
