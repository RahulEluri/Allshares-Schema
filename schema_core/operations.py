"""Typed operations. Every change from the UI, MCP or the importer goes through these.

Each operation mutates a Schema in place. The store wraps a batch of operations with the
version check, validation, the file lock and the changelog.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field as PField, TypeAdapter

from .bqtypes import type_for_format
from .models import (
    Cardinality, CatalogueField, Check, Column, DerivedColumn, DerivedView, FieldCheck, IntRange, Layer,
    Mode, Note, RefValue, Relationship, Schema, Table, ValidationRule,
)


class OpError(ValueError):
    """An operation cannot be applied (missing table, referenced column, ...)."""


class Ctx:
    """How an operation marks ownership. UI and Claude edits make items app-owned."""

    def __init__(self, owner: str = "app"):
        self.owner = owner


class _Op(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def apply(self, s: Schema, ctx: Ctx) -> None:  # pragma: no cover - abstract
        raise NotImplementedError

    def args(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"op"}, exclude_none=True)


# ---------------------------------------------------------------------------- helpers

def _table(s: Schema, name: str) -> Table:
    t = s.table(name)
    if t is None:
        raise OpError(f"Table '{name}' does not exist")
    return t


def _column(t: Table, name: str) -> Column:
    c = t.column(name)
    if c is None:
        raise OpError(f"Column '{name}' does not exist in {t.name}")
    return c


def _field(s: Schema, name: str) -> CatalogueField:
    f = s.catalogue.field(name)
    if f is None:
        raise OpError(f"Field '{name}' does not exist in the catalogue")
    return f


def apply_lineage(col: Column, f: CatalogueField, old: Optional[CatalogueField] = None) -> None:
    """Copy catalogue lineage onto a column. Explicit column overrides are kept."""
    col.protocol_id = f.protocol_id
    col.priority = f.priority
    col.requirement = f.requirement
    col.severity = f.severity
    if col.cdp_alias is None or (old is not None and col.cdp_alias == old.cdp_column):
        col.cdp_alias = f.cdp_column
    if not col.description or (old is not None and col.description == (old.description or "")):
        col.description = f.description or ""


def _clear_lineage(col: Column) -> None:
    col.field_id = None
    col.protocol_id = col.priority = col.requirement = col.severity = None


def _rels_touching_table(s: Schema, table: str) -> list[Relationship]:
    return [r for r in s.relationships if table in (r.from_table, r.to_table)]


def _rels_touching_column(s: Schema, table: str, column: str) -> list[Relationship]:
    return [
        r for r in s.relationships
        if (r.from_table == table and column in r.from_columns) or (r.to_table == table and column in r.to_columns)
    ]


def rename_in_expression(expression: str, old: str, new: str) -> str:
    """Rename a column reference inside a BigQuery expression (used when a source column is renamed)."""
    import sqlglot
    from sqlglot import exp

    tree = sqlglot.parse_one(expression, read="bigquery")
    tree = tree.transform(lambda n: exp.column(new) if isinstance(n, exp.Column) and n.name == old else n)
    return tree.sql("bigquery")


def _views_on(s: Schema, table: str) -> list[DerivedView]:
    return [v for v in s.views if v.source_table == table]


def _unique_rel_name(s: Schema, base: str) -> str:
    names = {r.name for r in s.relationships}
    if base not in names:
        return base
    i = 2
    while f"{base}_{i}" in names:
        i += 1
    return f"{base}_{i}"


ALTERABLE_COLUMN = {"type", "mode", "description", "cdp_alias", "validation_rule", "needs_confirmation"}
ALTERABLE_TABLE = {"layer", "description", "grain", "holds_fields"}
ALTERABLE_REF = {"label", "meaning", "status", "list_source", "extra"}
ALTERABLE_FIELD = set(CatalogueField.model_fields) - {"name", "owner"}
ALTERABLE_CHECK = set(Check.model_fields) - {"code", "owner"}
ALTERABLE_PAIR = set(FieldCheck.model_fields) - {"field_name", "check_code", "owner"}


def _set_attrs(obj: BaseModel, changes: dict[str, Any], allowed: set[str], what: str) -> None:
    bad = set(changes) - allowed
    if bad:
        raise OpError(f"Cannot change {', '.join(sorted(bad))} on {what}; allowed: {', '.join(sorted(allowed))}")
    for k, v in changes.items():
        setattr(obj, k, v)


# ---------------------------------------------------------------------------- tables

class AddTable(_Op):
    op: Literal["add_table"] = "add_table"
    name: str
    layer: Layer
    description: str = ""
    grain: str = ""
    columns: list[Column] = PField(default_factory=list)
    primary_key: list[str] = PField(default_factory=list)

    def apply(self, s, ctx):
        if s.table(self.name):
            raise OpError(f"Table '{self.name}' already exists")
        cols = [c.model_copy(update={"owner": ctx.owner}) for c in self.columns]
        s.tables.append(Table(name=self.name, layer=self.layer, description=self.description, grain=self.grain,
                              columns=cols, primary_key=list(self.primary_key), owner=ctx.owner))


class AlterTable(_Op):
    op: Literal["alter_table"] = "alter_table"
    table: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        t = _table(s, self.table)
        _set_attrs(t, self.changes, ALTERABLE_TABLE, f"table {t.name}")
        t.owner = ctx.owner


class RenameTable(_Op):
    op: Literal["rename_table"] = "rename_table"
    table: str
    new_name: str

    def apply(self, s, ctx):
        t = _table(s, self.table)
        if s.table(self.new_name):
            raise OpError(f"Table '{self.new_name}' already exists")
        for r in s.relationships:
            if r.from_table == t.name:
                r.from_table = self.new_name
            if r.to_table == t.name:
                r.to_table = self.new_name
        for v in _views_on(s, t.name):
            v.source_table = self.new_name
        t.name = self.new_name
        t.owner = ctx.owner


class DeleteTable(_Op):
    op: Literal["delete_table"] = "delete_table"
    table: str
    cascade: bool = False

    def apply(self, s, ctx):
        t = _table(s, self.table)
        rels = _rels_touching_table(s, t.name)
        views = _views_on(s, t.name)
        if (rels or views) and not self.cascade:
            used = [r.name for r in rels] + [f"view {v.name}" for v in views]
            raise OpError(f"{t.name} is used by {', '.join(used)}; pass cascade=true to delete them too")
        s.relationships = [r for r in s.relationships if r not in rels]
        s.views = [v for v in s.views if v not in views]
        s.tables = [x for x in s.tables if x.name != t.name]


# ---------------------------------------------------------------------------- columns

class AddColumn(_Op):
    op: Literal["add_column"] = "add_column"
    table: str
    name: str
    type: Optional[str] = None  # inferred from the linked field's Format when omitted
    mode: Mode = "NULLABLE"
    description: Optional[str] = None
    field_id: Optional[str] = None
    cdp_alias: Optional[str] = None
    validation_rule: Optional[ValidationRule] = None
    needs_confirmation: bool = False
    position: Optional[int] = None

    def apply(self, s, ctx):
        t = _table(s, self.table)
        if t.column(self.name):
            raise OpError(f"Column '{self.name}' already exists in {t.name}")
        f = _field(s, self.field_id) if self.field_id else None
        col = Column(
            name=self.name,
            type=self.type or (type_for_format(f.format, f.name) if f else "STRING"),
            mode=self.mode, description=self.description or "", field_id=self.field_id,
            cdp_alias=self.cdp_alias, validation_rule=self.validation_rule,
            needs_confirmation=self.needs_confirmation, owner=ctx.owner,
        )
        if f:
            apply_lineage(col, f)
        if self.position is None:
            t.columns.append(col)
        else:
            t.columns.insert(self.position, col)


class AlterColumn(_Op):
    op: Literal["alter_column"] = "alter_column"
    table: str
    column: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        t = _table(s, self.table)
        c = _column(t, self.column)
        changes = dict(self.changes)
        if "type" in changes and isinstance(changes["type"], str):
            changes["type"] = changes["type"].strip()
        if changes.get("validation_rule") is not None and not isinstance(changes["validation_rule"], ValidationRule):
            changes["validation_rule"] = ValidationRule(**changes["validation_rule"])
        _set_attrs(c, changes, ALTERABLE_COLUMN, f"column {t.name}.{c.name}")
        c.owner = ctx.owner


class RenameColumn(_Op):
    op: Literal["rename_column"] = "rename_column"
    table: str
    column: str
    new_name: str

    def apply(self, s, ctx):
        t = _table(s, self.table)
        c = _column(t, self.column)
        if t.column(self.new_name):
            raise OpError(f"Column '{self.new_name}' already exists in {t.name}")
        old = c.name

        def sub(names: list[str]) -> list[str]:
            return [self.new_name if n == old else n for n in names]

        t.primary_key = sub(t.primary_key)
        t.cluster_by = sub(t.cluster_by)
        if t.partition_by == old:
            t.partition_by = self.new_name
        for r in s.relationships:
            if r.from_table == t.name:
                r.from_columns = sub(r.from_columns)
            if r.to_table == t.name:
                r.to_columns = sub(r.to_columns)
        for v in _views_on(s, t.name):
            v.group_by = sub(v.group_by)
            for dc in v.columns:
                dc.expression = rename_in_expression(dc.expression, old, self.new_name)
        c.name = self.new_name
        c.owner = ctx.owner


class DeleteColumn(_Op):
    op: Literal["delete_column"] = "delete_column"
    table: str
    column: str
    cascade: bool = False

    def apply(self, s, ctx):
        t = _table(s, self.table)
        c = _column(t, self.column)
        rels = _rels_touching_column(s, t.name, c.name)
        if rels and not self.cascade:
            raise OpError(f"{t.name}.{c.name} is used by relationship(s) {', '.join(r.name for r in rels)}; pass cascade=true to delete them too")
        s.relationships = [r for r in s.relationships if r not in rels]
        t.columns = [x for x in t.columns if x.name != c.name]
        t.primary_key = [n for n in t.primary_key if n != c.name]
        t.cluster_by = [n for n in t.cluster_by if n != c.name]
        if t.partition_by == c.name:
            t.partition_by, t.partition_range = None, None


# ---------------------------------------------------------------------------- keys and layout

class SetPrimaryKey(_Op):
    op: Literal["set_primary_key"] = "set_primary_key"
    table: str
    columns: list[str]
    make_required: bool = True  # PK columns must be REQUIRED; set them so by default

    def apply(self, s, ctx):
        t = _table(s, self.table)
        for n in self.columns:
            c = _column(t, n)
            if self.make_required and c.mode != "REQUIRED":
                c.mode = "REQUIRED"
                c.owner = ctx.owner
        t.primary_key = list(self.columns)
        t.owner = ctx.owner


class AddRelationship(_Op):
    op: Literal["add_relationship"] = "add_relationship"
    from_table: str
    from_columns: list[str]
    to_table: str
    to_columns: Optional[list[str]] = None  # defaults to the target's primary key
    cardinality: Cardinality = "many_to_one"
    name: Optional[str] = None

    def apply(self, s, ctx):
        src, dst = _table(s, self.from_table), _table(s, self.to_table)
        for n in self.from_columns:
            _column(src, n)
        to_cols = list(self.to_columns or dst.primary_key)
        for n in to_cols:
            _column(dst, n)
        if self.name and any(r.name == self.name for r in s.relationships):
            raise OpError(f"Relationship '{self.name}' already exists")
        name = self.name or _unique_rel_name(s, f"fk_{src.name}_{'_'.join(self.from_columns)}")
        s.relationships.append(Relationship(
            name=name, from_table=src.name, from_columns=list(self.from_columns), to_table=dst.name,
            to_columns=to_cols, cardinality=self.cardinality, owner=ctx.owner,
        ))


class DeleteRelationship(_Op):
    op: Literal["delete_relationship"] = "delete_relationship"
    name: str

    def apply(self, s, ctx):
        if not any(r.name == self.name for r in s.relationships):
            raise OpError(f"Relationship '{self.name}' does not exist")
        s.relationships = [r for r in s.relationships if r.name != self.name]


class SetPartition(_Op):
    op: Literal["set_partition"] = "set_partition"
    table: str
    column: Optional[str] = None  # None clears partitioning
    range: Optional[IntRange] = None

    def apply(self, s, ctx):
        t = _table(s, self.table)
        if self.column:
            _column(t, self.column)
        t.partition_by = self.column
        t.partition_range = self.range if self.column else None
        t.owner = ctx.owner


class SetClustering(_Op):
    op: Literal["set_clustering"] = "set_clustering"
    table: str
    columns: list[str]

    def apply(self, s, ctx):
        t = _table(s, self.table)
        for n in self.columns:
            _column(t, n)
        t.cluster_by = list(self.columns)
        t.owner = ctx.owner


# ---------------------------------------------------------------------------- catalogue and ref data

class LinkColumnField(_Op):
    op: Literal["link_column_field"] = "link_column_field"
    table: str
    column: str
    field_name: Optional[str] = None  # None unlinks

    def apply(self, s, ctx):
        t = _table(s, self.table)
        c = _column(t, self.column)
        if self.field_name is None:
            _clear_lineage(c)
        else:
            f = _field(s, self.field_name)
            c.field_id = f.name
            apply_lineage(c, f)
        c.owner = ctx.owner


def _ref_table(s: Schema, name: str) -> Table:
    t = _table(s, name)
    if t.layer != "ref":
        raise OpError(f"{name} is not a ref table")
    return t


class AddRefValue(_Op):
    op: Literal["add_ref_value"] = "add_ref_value"
    table: str
    code: str
    label: Optional[str] = None
    meaning: Optional[str] = None
    status: Optional[str] = None
    list_source: Optional[str] = None
    extra: dict[str, Any] = PField(default_factory=dict)

    def apply(self, s, ctx):
        t = _ref_table(s, self.table)
        if any(r.code == self.code for r in t.rows):
            raise OpError(f"Code '{self.code}' already exists in {t.name}")
        t.rows.append(RefValue(code=self.code, label=self.label, meaning=self.meaning, status=self.status,
                               list_source=self.list_source, extra=dict(self.extra), owner=ctx.owner))


class UpdateRefValue(_Op):
    op: Literal["update_ref_value"] = "update_ref_value"
    table: str
    code: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        t = _ref_table(s, self.table)
        row = next((r for r in t.rows if r.code == self.code), None)
        if row is None:
            raise OpError(f"Code '{self.code}' does not exist in {t.name}")
        changes = dict(self.changes)
        new_code = changes.pop("code", None)
        _set_attrs(row, changes, ALTERABLE_REF, f"{t.name}.{self.code}")
        if new_code is not None:
            row.code = new_code
        row.owner = ctx.owner


class DeleteRefValue(_Op):
    op: Literal["delete_ref_value"] = "delete_ref_value"
    table: str
    code: str

    def apply(self, s, ctx):
        t = _ref_table(s, self.table)
        if not any(r.code == self.code for r in t.rows):
            raise OpError(f"Code '{self.code}' does not exist in {t.name}")
        t.rows = [r for r in t.rows if r.code != self.code]


class AddField(_Op):
    op: Literal["add_field"] = "add_field"
    field: CatalogueField

    def apply(self, s, ctx):
        if s.catalogue.field(self.field.name):
            raise OpError(f"Field '{self.field.name}' already exists")
        s.catalogue.fields.append(self.field.model_copy(update={"owner": ctx.owner}))


class UpdateField(_Op):
    """Change catalogue attributes of a field; linked columns get refreshed lineage."""

    op: Literal["update_field"] = "update_field"
    name: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        f = _field(s, self.name)
        old = f.model_copy()
        _set_attrs(f, self.changes, ALTERABLE_FIELD, f"field {f.name}")
        f.owner = ctx.owner
        for t in s.tables:
            for c in t.columns:
                if c.field_id == f.name:
                    apply_lineage(c, f, old)


class AddCheck(_Op):
    op: Literal["add_check"] = "add_check"
    check: Check

    def apply(self, s, ctx):
        if s.catalogue.check(self.check.code):
            raise OpError(f"Check '{self.check.code}' already exists")
        s.catalogue.checks.append(self.check.model_copy(update={"owner": ctx.owner}))


class UpdateCheck(_Op):
    op: Literal["update_check"] = "update_check"
    code: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        c = s.catalogue.check(self.code)
        if c is None:
            raise OpError(f"Check '{self.code}' does not exist")
        _set_attrs(c, self.changes, ALTERABLE_CHECK, f"check {c.code}")
        c.owner = ctx.owner


class LinkFieldCheck(_Op):
    op: Literal["link_field_check"] = "link_field_check"
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

    def apply(self, s, ctx):
        _field(s, self.field_name)
        if s.catalogue.check(self.check_code) is None:
            raise OpError(f"Check '{self.check_code}' does not exist")
        if s.catalogue.pair(self.field_name, self.check_code):
            raise OpError(f"{self.field_name} is already linked to {self.check_code}")
        s.catalogue.field_checks.append(FieldCheck(**self.args(), owner=ctx.owner))


class UpdateFieldCheck(_Op):
    op: Literal["update_field_check"] = "update_field_check"
    field_name: str
    check_code: str
    changes: dict[str, Any]

    def apply(self, s, ctx):
        p = s.catalogue.pair(self.field_name, self.check_code)
        if p is None:
            raise OpError(f"{self.field_name} is not linked to {self.check_code}")
        _set_attrs(p, self.changes, ALTERABLE_PAIR, f"pair {p.key}")
        p.owner = ctx.owner


class UnlinkFieldCheck(_Op):
    op: Literal["unlink_field_check"] = "unlink_field_check"
    field_name: str
    check_code: str

    def apply(self, s, ctx):
        if s.catalogue.pair(self.field_name, self.check_code) is None:
            raise OpError(f"{self.field_name} is not linked to {self.check_code}")
        s.catalogue.field_checks = [
            p for p in s.catalogue.field_checks
            if not (p.field_name == self.field_name and p.check_code == self.check_code)
        ]


class SetView(_Op):
    """Create or replace a derived view (values calculated from a child table)."""

    op: Literal["set_view"] = "set_view"
    name: str
    source_table: str
    group_by: list[str]
    columns: list[DerivedColumn]
    description: str = ""

    def apply(self, s, ctx):
        if s.table(self.name):
            raise OpError(f"'{self.name}' is already a table name")
        _table(s, self.source_table)
        view = DerivedView(name=self.name, source_table=self.source_table, group_by=list(self.group_by),
                           columns=[c.model_copy() for c in self.columns], description=self.description, owner=ctx.owner)
        for i, v in enumerate(s.views):
            if v.name == self.name:
                s.views[i] = view
                return
        s.views.append(view)


class DeleteView(_Op):
    op: Literal["delete_view"] = "delete_view"
    name: str

    def apply(self, s, ctx):
        if s.view(self.name) is None:
            raise OpError(f"View '{self.name}' does not exist")
        s.views = [v for v in s.views if v.name != self.name]


class UpsertNote(_Op):
    op: Literal["upsert_note"] = "upsert_note"
    note: Note

    def apply(self, s, ctx):
        notes = s.catalogue.notes
        new = self.note.model_copy(update={"owner": ctx.owner})
        for i, n in enumerate(notes):
            if n.id == new.id:
                notes[i] = new
                return
        notes.append(new)


class SetInternalReference(_Op):
    op: Literal["set_internal_reference"] = "set_internal_reference"
    provisional_ranges: list[dict[str, Any]]
    range_notes: list[str]

    def apply(self, s, ctx):
        s.internal_reference.provisional_ranges = list(self.provisional_ranges)
        s.internal_reference.range_notes = list(self.range_notes)


Operation = Annotated[
    Union[
        AddTable, AlterTable, RenameTable, DeleteTable,
        AddColumn, AlterColumn, RenameColumn, DeleteColumn,
        SetPrimaryKey, AddRelationship, DeleteRelationship, SetPartition, SetClustering,
        LinkColumnField, AddRefValue, UpdateRefValue, DeleteRefValue,
        AddField, UpdateField, AddCheck, UpdateCheck,
        LinkFieldCheck, UpdateFieldCheck, UnlinkFieldCheck,
        SetView, DeleteView, UpsertNote, SetInternalReference,
    ],
    PField(discriminator="op"),
]
_OP_ADAPTER = TypeAdapter(Operation)

# The §6 operations; the rest exist so accepted import diffs are ordinary operations too.
CORE_OPS = [
    "add_table", "rename_table", "delete_table", "add_column", "alter_column", "rename_column",
    "delete_column", "set_primary_key", "add_relationship", "delete_relationship", "set_partition",
    "set_clustering", "link_column_field", "add_ref_value", "update_ref_value", "delete_ref_value",
    "add_field", "link_field_check", "unlink_field_check",
]


def parse_op(data: dict[str, Any] | _Op) -> _Op:
    if isinstance(data, _Op):
        return data
    return _OP_ADAPTER.validate_python(data)
