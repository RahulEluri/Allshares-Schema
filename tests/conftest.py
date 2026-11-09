import pytest

from schema_core.models import CatalogueField, Column, Relationship, Schema, Table
from schema_core.store import SchemaStore


def small_schema() -> Schema:
    s = Schema()
    s.catalogue.fields = [
        CatalogueField(name="legal_name", format="Text", description="Registered legal name", protocol_id="C01"),
        CatalogueField(name="base_salary", format="Money", description="Base salary", protocol_id="R04", cdp_column="comp_base_salary"),
        CatalogueField(name="year_of_birth", format="Year", status="parked"),
    ]
    s.tables = [
        Table(name="ref_currency", layer="ref", columns=[Column(name="code", mode="REQUIRED")], primary_key=["code"]),
        Table(name="dim_company", layer="dim", primary_key=["company_id"], columns=[
            Column(name="company_id", mode="REQUIRED"),
            Column(name="legal_name", field_id="legal_name"),
        ]),
        Table(name="fact_pay_line", layer="fact", primary_key=["pay_line_id"], columns=[
            Column(name="pay_line_id", mode="REQUIRED"),
            Column(name="company_id", mode="REQUIRED"),
            Column(name="pay_currency"),
            Column(name="base_salary", type="NUMERIC", field_id="base_salary"),
            Column(name="extracted_at", type="TIMESTAMP"),
        ]),
    ]
    s.relationships = [
        Relationship(name="fk_pay_company", from_table="fact_pay_line", from_columns=["company_id"], to_table="dim_company", to_columns=["company_id"]),
        Relationship(name="fk_pay_currency", from_table="fact_pay_line", from_columns=["pay_currency"], to_table="ref_currency", to_columns=["code"]),
    ]
    return s


@pytest.fixture
def schema() -> Schema:
    return small_schema()


@pytest.fixture
def store(tmp_path) -> SchemaStore:
    st = SchemaStore(tmp_path / "schema")
    st.initialize(small_schema(), actor="test", reason="fixture")
    return st
