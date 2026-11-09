"""Ownership lives in company_holder; controlling owner etc. are calculated in a derived view."""
import pytest
import sqlglot
from sqlglot import exp

from schema_core.conflicts import list_conflicts
from schema_core.export import export_bigquery, parse_check
from schema_core.importer.draft import build_draft
from schema_core.importer.snapshot import build_snapshot
from schema_core.models import DerivedColumn
from schema_core.operations import Ctx, DeleteTable, OpError, RenameColumn, SetView
from schema_core.validation import placed_fields, validate


@pytest.fixture
def draft():
    return build_draft(build_snapshot())


def codes(s):
    return {i.code for i in validate(s) if i.severity == "error"}


def test_holder_table_carries_names_and_related_info(draft):
    h = draft.table("company_holder")
    names = [c.name for c in h.columns]
    assert names[:4] == ["company_id", "fiscal_year", "holder_rank", "holder_name"]
    assert {"holder_type", "capital_pct", "votes_pct", "holder_group", "is_tied", "as_of_date",
            "share_count_basis", "list_cutoff"} <= set(names)
    fks = {r.from_columns[0]: r.to_table for r in draft.relationships if r.from_table == "company_holder" and len(r.from_columns) == 1}
    assert fks == {"holder_type": "ref_ownership_type", "share_count_basis": "ref_share_count_basis",
                   "list_cutoff": "ref_holder_list_cutoff"}
    assert draft.table("ref_controlling_owner") is None


def test_derived_fields_are_placed_in_the_view(draft):
    v = draft.view("v_company_ownership")
    assert v.source_table == "company_holder" and v.group_by == ["company_id", "fiscal_year"]
    placed = placed_fields(draft)
    for f in ("controlling_owner", "controlling_owner_name", "pe_stake_5pct"):
        assert placed[f] == [f"v_company_ownership.{f}"]
    assert "company_holder.holder_type" in placed["ownership_type"] and "v_company_ownership.ownership_type" in placed["ownership_type"]
    assert codes(draft) == set()
    assert any(c["id"] == "controlling_owner_meaning" and "20%" in c["detail"] for c in list_conflicts(draft))


def test_view_exports_and_parses(draft):
    sql = export_bigquery(draft, "p", "d")
    assert "CREATE OR REPLACE VIEW `p.d.v_company_ownership`" in sql
    assert sql.index("CREATE OR REPLACE VIEW") > sql.rindex("CREATE TABLE IF NOT EXISTS")
    assert parse_check(sql)["ok"]
    view_sql = export_bigquery(draft, "p", "d", table="v_company_ownership")
    tree = sqlglot.parse_one(view_sql, read="bigquery")
    assert isinstance(tree, exp.Create) and "LOGICAL_OR(votes_pct >= 20) AS controlling_owner" in view_sql


def test_view_validation_errors(draft):
    v = draft.view("v_company_ownership")
    v.columns.append(DerivedColumn(name="bad", expression="SUM(no_such_column)", type="NUMERIC"))
    assert "view_missing_column" in codes(draft)
    v.columns[-1] = DerivedColumn(name="bad", expression="SUM(", type="NUMERIC")
    assert "view_expression" in codes(draft)
    v.columns.pop()
    v.group_by = ["company_id", "nope"]
    assert "view_missing_column" in codes(draft)


def test_rename_column_rewrites_view_and_delete_needs_cascade(draft):
    RenameColumn(table="company_holder", column="votes_pct", new_name="voting_pct").apply(draft, Ctx())
    v = draft.view("v_company_ownership")
    assert v.column("controlling_owner").expression == "LOGICAL_OR(voting_pct >= 20)"
    assert codes(draft) == set()
    with pytest.raises(OpError):
        DeleteTable(table="company_holder", cascade=False).apply(draft, Ctx())
    DeleteTable(table="company_holder", cascade=True).apply(draft, Ctx())
    assert draft.view("v_company_ownership") is None


def test_set_view_upserts(draft):
    SetView(name="v_company_ownership", source_table="company_holder", group_by=["company_id", "fiscal_year"],
            columns=[DerivedColumn(name="holder_count", type="INT64", expression="COUNT(*)")]).apply(draft, Ctx())
    assert [c.name for c in draft.view("v_company_ownership").columns] == ["holder_count"]
    assert len(draft.views) == 1
