import re

import pytest
import sqlglot
from sqlglot import exp

from schema_core.export import LAYER_GROUP, export_bigquery, parse_check, table_order
from schema_core.importer.draft import build_draft
from schema_core.importer.snapshot import build_snapshot
from schema_core.models import Column


@pytest.fixture(scope="module")
def draft():
    return build_draft(build_snapshot())


@pytest.fixture(scope="module")
def sql(draft):
    return export_bigquery(draft, "proj", "allshares_cdp", "EU")


def test_export_parses_with_sqlglot_bigquery(sql):
    stmts = sqlglot.parse(sql, read="bigquery", error_level=sqlglot.ErrorLevel.RAISE)
    assert stmts and not any(isinstance(s, exp.Command) for s in stmts if s is not None)
    assert parse_check(sql)["ok"]


def test_opens_with_dataset(sql):
    first = next(l for l in sql.splitlines() if l and not l.startswith("--"))
    assert first == "CREATE SCHEMA IF NOT EXISTS `proj.allshares_cdp`"


def test_tables_in_dependency_order(draft, sql):
    created = re.findall(r"CREATE TABLE IF NOT EXISTS `proj\.allshares_cdp\.(\w+)`", sql)
    assert len(created) == len(draft.tables)
    groups = [LAYER_GROUP[draft.table(n).layer] for n in created]
    assert groups == sorted(groups)
    pos = {n: i for i, n in enumerate(created)}
    for r in draft.relationships:
        assert pos[r.to_table] < pos[r.from_table], r.name
    assert [t.name for t in table_order(draft)] == created


def test_all_keys_not_enforced(draft, sql):
    pk = len(re.findall(r"PRIMARY KEY \(", sql))
    fk = len(re.findall(r"FOREIGN KEY \(", sql))
    assert pk == sum(1 for t in draft.tables if t.primary_key)
    assert fk == len(draft.relationships)
    assert len(re.findall(r"\) NOT ENFORCED", sql)) == pk + fk


def test_partition_cluster_and_descriptions(sql):
    assert "PARTITION BY DATE(extracted_at)\nCLUSTER BY company_id, field_name" in sql
    assert "PARTITION BY DATE(checked_at)" in sql
    assert "base_salary NUMERIC OPTIONS(description=\"Fixed base salary only (no board fees or benefits) [Protocol ID: R04; CDP alias: comp_base_salary]\")" in sql


def test_seed_inserts(draft, sql):
    for t in ("dim_field", "dim_check", "bridge_field_check", "ref_check_result", "ref_lti_basis"):
        assert f"INSERT INTO `proj.allshares_cdp.{t}`" in sql
    assert "-- ref_country: no seed rows" in sql
    rows = len(re.findall(r"^\s+\(", sql.split("-- Seed data", 1)[1], flags=re.M))
    expected = len(draft.catalogue.fields) + len(draft.catalogue.checks) + len(draft.catalogue.field_checks) + \
        sum(len(t.rows) for t in draft.tables if t.layer == "ref")
    assert rows == expected


def test_per_table_export_and_quoting(draft):
    d = draft.model_copy(deep=True)
    d.table("dim_company").columns.append(Column(name="weird", description='He said "hi" \\ it\'s\nnew'))
    part = export_bigquery(d, "p", "d", table="dim_company")
    assert part.startswith("CREATE TABLE IF NOT EXISTS `p.d.dim_company`")
    assert parse_check(part)["ok"]


def test_int64_range_partition(draft):
    d = draft.model_copy(deep=True)
    t = d.table("fact_company_year")
    from schema_core.models import IntRange
    t.partition_by, t.partition_range = "fiscal_year", IntRange(start=2000, end=2100)
    part = export_bigquery(d, "p", "d", table="fact_company_year")
    assert "PARTITION BY RANGE_BUCKET(fiscal_year, GENERATE_ARRAY(2000, 2100, 1))" in part
    assert parse_check(part)["ok"]
