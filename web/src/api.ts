import type { AppState, ApplyResult, Op } from "./types";

export class ConflictError extends Error {}

async function j<T>(res: Response): Promise<T> {
  if (res.status === 409) throw new ConflictError((await res.json()).message);
  if (!res.ok) {
    let msg = res.statusText;
    try { const b = await res.json(); msg = typeof b.detail === "string" ? b.detail : JSON.stringify(b.detail ?? b); } catch { /* keep */ }
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

const json = (method: string, body: unknown) => ({ method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const api = {
  state: () => fetch("/api/state").then((r) => j<AppState>(r)),
  ops: (ops: Op[], expected_version: string, reason: string, dry_run = false) =>
    fetch("/api/ops", json("POST", { ops, expected_version, reason, dry_run })).then((r) => j<ApplyResult>(r)),
  layout: (positions: Record<string, { x: number; y: number }>) => fetch("/api/layout", json("PUT", { positions })),
  settings: (s: Record<string, string>) => fetch("/api/settings", json("PUT", s)).then((r) => j<Record<string, string>>(r)),
  changelog: () => fetch("/api/changelog?limit=300").then((r) => j<Record<string, unknown>[]>(r)),
  importDiff: () => fetch("/api/import/diff").then((r) => j<ImportDiff>(r)),
  importApply: (item_ids: string[], expected_version: string) =>
    fetch("/api/import/apply", json("POST", { item_ids, expected_version })).then((r) => j<ApplyResult>(r)),
  exportSql: (table?: string, bq = false) =>
    fetch(`/api/export?${new URLSearchParams({ ...(table ? { table } : {}), ...(bq ? { bq: "true" } : {}) })}`).then((r) => j<ExportResult>(r)),
};

export interface ImportItem {
  id: string; category: string; key: string; kind: "added" | "changed" | "removed"; label: string;
  changes: Record<string, { before: unknown; after: unknown }>; app_owned: boolean; applicable: boolean; reason?: string;
}
export interface ImportDiff { version: string; summary: Record<string, Record<string, number>>; items: ImportItem[]; notices: string[] }
export interface ExportResult {
  version: string; sql: string; order: string[];
  parse_check: { ok: boolean; statements: number; error?: string };
  bq_dry_run?: { ok: boolean; available: boolean; output: string };
}
