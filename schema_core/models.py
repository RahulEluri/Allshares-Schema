"""Pydantic models for schema.json, the single source of truth."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field as PField

Layer = Literal["ref", "catalogue", "provenance", "dim", "fact", "child", "bridge"]
Owner = Literal["workbook", "app"]
Mode = Literal["NULLABLE", "REQUIRED", "REPEATED"]
Cardinality = Literal["many_to_one", "one_to_one"]

LAYERS: tuple[str, ...] = ("ref", "catalogue", "provenance", "dim", "fact", "child", "bridge")


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ValidationRule(_Base):
    """A column-level rule that BigQuery cannot enforce (documented in the export)."""

    kind: Literal["range", "pattern"]
    min: Optional[float] = None
    max: Optional[float] = None
    pattern: Optional[str] = None
    description: Optional[str] = None

    def describe(self) -> str:
        if self.description:
            return self.description
        if self.kind == "range":
            return f"range {self.min:g} to {self.max:g}"
        return f"pattern {self.pattern}"


class Column(_Base):
    name: str
    type: str = "STRING"
    mode: Mode = "NULLABLE"
    description: str = ""
    field_id: Optional[str] = None
    # Lineage copied from the catalogue (refreshed when the linked field changes).
    cdp_alias: Optional[str] = None
    protocol_id: Optional[str] = None
    priority: Optional[str] = None
    requirement: Optional[str] = None
    severity: Optional[str] = None
    validation_rule: Optional[ValidationRule] = None
    needs_confirmation: bool = False  # the brief's † marker: not in the field catalogue
    owner: Owner = "workbook"


class RefValue(_Base):
    code: str
    label: Optional[str] = None
    meaning: Optional[str] = None
    status: Optional[str] = None
    list_source: Optional[str] = None
    extra: dict[str, Any] = PField(default_factory=dict)
    owner: Owner = "workbook"


class IntRange(_Base):
    start: int
    end: int
    interval: int = 1


class Table(_Base):
    name: str
    layer: Layer
    description: str = ""
    grain: str = ""
    columns: list[Column] = PField(default_factory=list)
    primary_key: list[str] = PField(default_factory=list)
    partition_by: Optional[str] = None  # a column name
    partition_range: Optional[IntRange] = None  # required when partitioning on INT64
    cluster_by: list[str] = PField(default_factory=list)
    holds_fields: list[str] = PField(default_factory=list)  # list fields a child table carries
    rows: list[RefValue] = PField(default_factory=list)  # seed data for ref tables
    owner: Owner = "workbook"

    def column(self, name: str) -> Optional[Column]:
        return next((c for c in self.columns if c.name == name), None)


class Relationship(_Base):
    name: str
    from_table: str
    from_columns: list[str]
    to_table: str
    to_columns: list[str]
    cardinality: Cardinality = "many_to_one"
    owner: Owner = "workbook"


class DerivedColumn(_Base):
    """A value calculated from a child table, e.g. controlling_owner from company_holder."""

    name: str
    type: str = "STRING"
    expression: str  # BigQuery SQL over the source table's columns (aggregate per group)
    description: str = ""
    field_id: Optional[str] = None


class DerivedView(_Base):
    """Exported as CREATE OR REPLACE VIEW ... AS SELECT group_by, expressions FROM source GROUP BY group_by."""

    name: str
    source_table: str
    group_by: list[str]
    description: str = ""
    columns: list[DerivedColumn] = PField(default_factory=list)
    owner: Owner = "workbook"

    def column(self, name: str) -> Optional[DerivedColumn]:
        return next((c for c in self.columns if c.name == name), None)


class CatalogueField(_Base):
    name: str
    protocol_id: Optional[str] = None
    cdp_column: Optional[str] = None
    module: Optional[str] = None
    data_category: Optional[str] = None
    grain: Optional[str] = None
    field_type: Optional[str] = None  # direct | derived
    field_type_detail: Optional[str] = None  # raw workbook wording
    format: Optional[str] = None
    description: Optional[str] = None
    read_from: Optional[str] = None
    method: Optional[str] = None
    priority: Optional[str] = None
    requirement: Optional[str] = None
    severity: Optional[str] = None
    fill_of_50: Optional[int] = None
    why_it_matters: Optional[str] = None
    note: Optional[str] = None
    status: Literal["active", "new", "parked"] = "active"
    source: Optional[str] = None
    owner: Owner = "workbook"


class Check(_Base):
    code: str
    name: str
    check_fx: Optional[str] = None  # direct | derived
    check_type: Optional[str] = None  # hard | soft
    applies_to_categories: list[str] = PField(default_factory=list)
    fields_checked: Optional[int] = None
    parent_gates: list[str] = PField(default_factory=list)
    parent_relation: Optional[str] = None  # new | changed | existing (Conor's rules)
    status: str = "active"  # active, hold_off, to_do, confirmed, existing
    kind: Literal["gate", "rule"] = "gate"
    applies_when: Optional[str] = None
    result_if_not: Optional[str] = None
    proposed_change: Optional[dict[str, Any]] = None  # Conor section A on an existing gate
    undefined: bool = False  # cited by a workbook but not defined in All Checks
    remarks: Optional[str] = None
    owner: Owner = "workbook"


class FieldCheck(_Base):
    field_name: str
    check_code: str
    module: Optional[str] = None
    pass_criteria: Optional[str] = None
    fail_criteria: Optional[str] = None
    example: Optional[str] = None
    reference: Optional[str] = None
    remarks: Optional[str] = None
    score: Optional[float] = None
    weight: Optional[float] = None
    owner: Owner = "workbook"

    @property
    def key(self) -> str:
        return f"{self.field_name}|{self.check_code}"


class Note(_Base):
    """Check metadata that is not itself a check: quote matching (D), load bar (E), thresholds."""

    id: str
    kind: str
    title: str
    text: str
    owner: Owner = "workbook"


class Catalogue(_Base):
    fields: list[CatalogueField] = PField(default_factory=list)
    checks: list[Check] = PField(default_factory=list)
    field_checks: list[FieldCheck] = PField(default_factory=list)
    notes: list[Note] = PField(default_factory=list)

    def field(self, name: str) -> Optional[CatalogueField]:
        return next((f for f in self.fields if f.name == name), None)

    def check(self, code: str) -> Optional[Check]:
        return next((c for c in self.checks if c.code == code), None)

    def pair(self, field_name: str, check_code: str) -> Optional[FieldCheck]:
        return next(
            (p for p in self.field_checks if p.field_name == field_name and p.check_code == check_code),
            None,
        )


class InternalReference(_Base):
    """Internal-only data (not Allshares-approved; never attached to checks)."""

    provisional_ranges: list[dict[str, Any]] = PField(default_factory=list)
    range_notes: list[str] = PField(default_factory=list)


class Schema(_Base):
    format_version: int = 1
    tables: list[Table] = PField(default_factory=list)
    relationships: list[Relationship] = PField(default_factory=list)
    views: list[DerivedView] = PField(default_factory=list)
    catalogue: Catalogue = PField(default_factory=Catalogue)
    internal_reference: InternalReference = PField(default_factory=InternalReference)

    def table(self, name: str) -> Optional[Table]:
        return next((t for t in self.tables if t.name == name), None)

    def view(self, name: str) -> Optional[DerivedView]:
        return next((v for v in self.views if v.name == name), None)
