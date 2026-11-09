import { createContext, useContext } from "react";
import type { AppState, Op } from "./types";

export interface Toast { id: number; kind: "ok" | "error" | "warn"; text: string }

export interface Ctx {
  state: AppState;
  apply: (ops: Op[], reason: string) => Promise<boolean>;
  reload: () => Promise<void>;
  selected: string | null;
  select: (table: string | null) => void;
  highlight: Set<string>; // "table" or "table.column"
  setHighlight: (h: Set<string>, label?: string) => void;
  toast: (kind: Toast["kind"], text: string) => void;
  openTab: (side: "left" | "bottom", tab: string) => void;
  refTable: string | null;
  setRefTable: (t: string | null) => void;
}

export const AppCtx = createContext<Ctx | null>(null);

export function useApp(): Ctx {
  const c = useContext(AppCtx);
  if (!c) throw new Error("AppCtx missing");
  return c;
}

export const LAYER_COLOR: Record<string, string> = {
  ref: "#64748b", catalogue: "#7c3aed", provenance: "#0d9488", dim: "#2563eb", fact: "#ea580c", child: "#16a34a", bridge: "#db2777",
};

export function columnsForCheck(state: AppState, code: string): Set<string> {
  const fields = new Set(state.schema.catalogue.field_checks.filter((p) => p.check_code === code).map((p) => p.field_name));
  const out = new Set<string>();
  for (const t of state.schema.tables) {
    for (const c of t.columns) if (c.field_id && fields.has(c.field_id)) { out.add(`${t.name}.${c.name}`); out.add(t.name); }
    for (const f of t.holds_fields) if (fields.has(f)) out.add(t.name);
  }
  return out;
}
