"""One test per §6 error case, plus the warnings."""
import pytest

from schema_core.bqtypes import is_valid_type
from schema_core.models import Column, IntRange, RefValue, Relationship, Table
from schema_core.operations import Ctx, DeleteColumn, DeleteTable, OpError
from schema_core.validation import validate


def codes(schema, severity="error"):
    return {i.code for i in validate(schema) if i.severity == severity}


def test_clean_fixture_has_no_errors(schema):
    assert codes(schema) == set()


@pytest.mark.parametrize("t", ["STRING", "INT64", "NUMERIC", "BIGNUMERIC", "FLOAT64", "BOOL", "DATE", "DATETIME",
                               "TIME", "TIMESTAMP", "JSON", "GEOGRAPHY", "BYTES", "ARRAY<STRING>",
                               "STRUCT<a INT64, b ARRAY<STRING>>"])
def test_valid_types(t):
    assert is_valid_type(t)


@pytest.mark.parametrize("t", ["VARCHAR", "INTEGER(10)", "ARRAY<ARRAY<INT64>>", "STRUCT<>", "STRUCT<a FOO>", ""])
def test_invalid_types(t):
    assert not is_valid_type(t)


def test_invalid_column_type(schema):
    schema.table("dim_company").column("legal_name").type = "VARCHAR"
    assert "invalid_type" in codes(schema)


def test_duplicate_table_name(schema):
    schema.tables.append(Table(name="dim_company", layer="dim"))
    assert "duplicate_table" in codes(schema)


def test_duplicate_column_name(schema):
    schema.table("dim_company").columns.append(Column(name="legal_name"))
    assert "duplicate_column" in codes(schema)


def test_table_name_not_snake_case(schema):
    schema.table("dim_company").name = "DimCompany"
    assert "name_not_snake_case" in codes(schema)


def test_column_name_not_snake_case(schema):
    schema.table("dim_company").column("legal_name").name = "Legal Name"
    assert "name_not_snake_case" in codes(schema)


def test_pk_column_not_required(schema):
    schema.table("dim_company").column("company_id").mode = "NULLABLE"
    assert "pk_not_required" in codes(schema)


def test_fk_target_not_full_pk(schema):
    t = schema.table("dim_company")
    t.columns.append(Column(name="fiscal_year", type="INT64", mode="REQUIRED"))
    t.primary_key = ["company_id", "fiscal_year"]  # now the FK targets only part of the PK
    assert "fk_target_not_pk" in codes(schema)


def test_fk_column_count_mismatch(schema):
    schema.relationships.append(Relationship(name="bad", from_table="fact_pay_line", from_columns=["company_id", "pay_currency"],
                                             to_table="dim_company", to_columns=["company_id"]))
    assert "fk_column_count" in codes(schema)


def test_fk_type_mismatch(schema):
    schema.table("fact_pay_line").column("pay_currency").type = "INT64"
    assert "fk_type_mismatch" in codes(schema)


def test_partition_on_wrong_type(schema):
    schema.table("fact_pay_line").partition_by = "pay_currency"
    assert "partition_type" in codes(schema)


def test_partition_on_timestamp_ok_and_int_needs_range(schema):
    t = schema.table("fact_pay_line")
    t.partition_by = "extracted_at"
    assert "partition_type" not in codes(schema)
    t.columns.append(Column(name="fiscal_year", type="INT64"))
    t.partition_by = "fiscal_year"
    assert "partition_type" in codes(schema)
    t.partition_range = IntRange(start=2000, end=2100)
    assert "partition_type" not in codes(schema)


def test_more_than_four_cluster_columns(schema):
    t = schema.table("fact_pay_line")
    for n in ("a", "b"):
        t.columns.append(Column(name=n))
    t.cluster_by = ["pay_line_id", "company_id", "pay_currency", "a", "b"]
    assert "cluster_too_many" in codes(schema)


def test_unknown_field_id(schema):
    schema.table("dim_company").column("legal_name").field_id = "no_such_field"
    assert "unknown_field" in codes(schema)


def test_duplicate_ref_codes(schema):
    schema.table("ref_currency").rows = [RefValue(code="EUR"), RefValue(code="EUR")]
    assert "ref_duplicate_code" in codes(schema)


def test_delete_referenced_table_needs_cascade(schema):
    with pytest.raises(OpError):
        DeleteTable(table="dim_company").apply(schema, Ctx())
    DeleteTable(table="dim_company", cascade=True).apply(schema, Ctx())
    assert all(r.to_table != "dim_company" for r in schema.relationships)


def test_delete_referenced_column_needs_cascade(schema):
    with pytest.raises(OpError):
        DeleteColumn(table="fact_pay_line", column="pay_currency").apply(schema, Ctx())
    DeleteColumn(table="fact_pay_line", column="pay_currency", cascade=True).apply(schema, Ctx())
    assert not any(r.name == "fk_pay_currency" for r in schema.relationships)


# --- warnings ---------------------------------------------------------------------------

def test_layer_prefix_warning(schema):
    schema.table("dim_company").layer = "fact"
    assert "layer_prefix" in codes(schema, "warning")


def test_unplaced_field_warning_skips_parked(schema):
    schema.table("dim_company").columns.pop()  # legal_name no longer placed
    warn = [i for i in validate(schema) if i.code == "field_not_placed"]
    assert [w.message for w in warn] == ["Catalogue field 'legal_name' is not placed in any table"]


def test_array_warning(schema):
    schema.table("dim_company").columns.append(Column(name="tags", type="ARRAY<STRING>"))
    assert "complex_type" in codes(schema, "warning")


def test_fact_without_relationship_warning(schema):
    schema.relationships = []
    assert "fact_no_relationship" in codes(schema, "warning")
