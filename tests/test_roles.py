"""Roles: ref_role list, primary role on the pay line, and pay_line_role for lines covering several roles."""
from schema_core.importer.draft import build_draft
from schema_core.importer.snapshot import build_snapshot
from schema_core.validation import placed_fields, validate


def test_role_tables():
    d = build_draft(build_snapshot())
    ref = d.table("ref_role")
    assert {r.code for r in ref.rows} >= {"ceo", "cfo", "executive_team_aggregate", "board_chair", "board_member"}
    assert all(r.status == "Proposed: confirm with Allshares" for r in ref.rows)
    assert ref.column("is_ceo").type == "BOOL" and ref.column("sort_order").type == "INT64"
    assert [r.code for r in ref.rows if r.extra.get("is_ceo")] == ["ceo"]

    plr = d.table("pay_line_role")
    assert plr.layer == "child" and plr.primary_key == ["pay_line_id", "role_code"]
    fks = {r.from_columns[0]: r.to_table for r in d.relationships if r.from_table == "pay_line_role"}
    assert fks == {"pay_line_id": "fact_pay_line", "role_code": "ref_role"}

    fpl = d.table("fact_pay_line")
    names = [c.name for c in fpl.columns]
    assert names.index("role_code") == names.index("role_title") + 1
    assert any(r.from_table == "fact_pay_line" and r.from_columns == ["role_code"] and r.to_table == "ref_role" for r in d.relationships)
    assert placed_fields(d)["role_code"] == ["fact_pay_line.role_code", "pay_line_role.role_code"]
    assert d.catalogue.field("role_code").status == "new"
    assert not [i for i in validate(d) if i.severity == "error"]
