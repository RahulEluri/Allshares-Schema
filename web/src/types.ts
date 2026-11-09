export type Layer = "ref" | "catalogue" | "provenance" | "dim" | "fact" | "child" | "bridge";
export const LAYERS: Layer[] = ["ref", "catalogue", "provenance", "dim", "fact", "child", "bridge"];
export const DELIVERY: Layer[] = ["dim", "fact", "child"];

export interface ValidationRule { kind: "range" | "pattern"; min?: number; max?: number; pattern?: string; description?: string }

export interface Column {
  name: string; type: string; mode: "NULLABLE" | "REQUIRED" | "REPEATED"; description: string;
  field_id?: string; cdp_alias?: string; protocol_id?: string; priority?: string; requirement?: string; severity?: string;
  validation_rule?: ValidationRule; needs_confirmation: boolean; owner: "workbook" | "app";
}

export interface RefValue { code: string; label?: string; meaning?: string; status?: string; list_source?: string; extra: Record<string, unknown>; owner: string }

export interface Table {
  name: string; layer: Layer; description: string; grain: string; columns: Column[]; primary_key: string[];
  partition_by?: string; partition_range?: { start: number; end: number; interval: number }; cluster_by: string[];
  holds_fields: string[]; rows: RefValue[]; owner: string;
}

export interface Relationship { name: string; from_table: string; from_columns: string[]; to_table: string; to_columns: string[]; cardinality: string; owner: string }

export interface Field {
  name: string; protocol_id?: string; cdp_column?: string; module?: string; data_category?: string; grain?: string;
  field_type?: string; format?: string; description?: string; priority?: string; requirement?: string; severity?: string;
  fill_of_50?: number; note?: string; status: "active" | "new" | "parked"; source?: string; owner: string;
}

export interface Check {
  code: string; name: string; check_fx?: string; check_type?: string; applies_to_categories: string[];
  parent_gates: string[]; parent_relation?: string; status: string; kind: "gate" | "rule"; applies_when?: string;
  result_if_not?: string; proposed_change?: Record<string, string>; undefined: boolean; remarks?: string;
}

export interface FieldCheck { field_name: string; check_code: string; module?: string; pass_criteria?: string; fail_criteria?: string; score?: number; weight?: number }

export interface DerivedColumn { name: string; type: string; expression: string; description: string; field_id?: string }
export interface DerivedView { name: string; source_table: string; group_by: string[]; description: string; columns: DerivedColumn[]; owner: string }

export interface Schema {
  tables: Table[]; relationships: Relationship[]; views: DerivedView[];
  catalogue: { fields: Field[]; checks: Check[]; field_checks: FieldCheck[]; notes: { id: string; kind: string; title: string; text: string }[] };
}

export interface Issue { severity: "error" | "warning"; code: string; message: string; table?: string; column?: string }
export interface Conflict { id: string; title: string; detail: string; items: string[]; kind: string }

export interface AppState {
  version: string; schema: Schema; layout: { positions: Record<string, { x: number; y: number }> };
  settings: { project: string; dataset: string; location: string }; issues: Issue[]; conflicts: Conflict[];
  column_checks: Record<string, string[]>; placed: Record<string, string[]>;
}

export interface ApplyResult { ok: boolean; version: string; dry_run: boolean; diff: unknown[]; errors: Issue[]; warnings: Issue[]; message: string }

export type Op = Record<string, unknown> & { op: string };

export const BQ_TYPES = ["STRING", "INT64", "NUMERIC", "BIGNUMERIC", "FLOAT64", "BOOL", "DATE", "DATETIME", "TIME", "TIMESTAMP", "JSON", "BYTES", "GEOGRAPHY"];
