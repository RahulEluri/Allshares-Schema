import { ReactFlowProvider } from "@xyflow/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, ConflictError } from "./api";
import { AppCtx, LAYER_COLOR, type Ctx, type Toast } from "./ctx";
import { DELIVERY, LAYERS, type AppState, type Layer, type Op } from "./types";
import { Canvas } from "./components/Canvas";
import { TableEditor } from "./components/TableEditor";
import { ChecksPanel, FieldTray, RefEditor } from "./components/SidePanels";
import { ChangelogPanel, ExportPanel, ImportPanel, IssuesPanel } from "./components/BottomPanels";

const LEFT_TABS = [["fields", "Field tray"], ["checks", "Checks"], ["ref", "Ref data"]] as const;
const BOTTOM_TABS = [["issues", "Conflicts & validation"], ["import", "Import diff"], ["history", "Changelog"], ["export", "Export"]] as const;

export default function App() {
  const [state, setState] = useState<AppState | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [selected, select] = useState<string | null>(null);
  const [highlight, setHl] = useState<Set<string>>(new Set());
  const [hlLabel, setHlLabel] = useState<string | undefined>();
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [left, setLeft] = useState<string | null>("fields");
  const [bottom, setBottom] = useState<string | null>("issues");
  const [refTable, setRefTable] = useState<string | null>(null);
  const [visible, setVisible] = useState<Set<Layer>>(new Set(LAYERS));
  const [search, setSearch] = useState("");
  const [live, setLive] = useState(false);
  const versionRef = useRef<string>("");

  const toast = useCallback((kind: Toast["kind"], text: string) => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t.slice(-4), { id, kind, text }]);
    window.setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), kind === "error" ? 9000 : 3500);
  }, []);

  const reload = useCallback(async () => {
    try {
      const s = await api.state();
      versionRef.current = s.version;
      setState(s);
      setLoadErr(null);
    } catch (e) { setLoadErr(String(e)); }
  }, []);

  useEffect(() => { reload(); }, [reload]);

  // Live reload: the API watches schema.json and pushes the new version (e.g. after an MCP edit).
  useEffect(() => {
    let es: EventSource | null = null;
    let retry: number | undefined;
    const connect = () => {
      es = new EventSource("/api/events");
      es.addEventListener("hello", () => setLive(true));
      es.addEventListener("changed", (ev) => {
        const v = JSON.parse((ev as MessageEvent).data).version;
        if (v !== versionRef.current) { reload(); toast("warn", "Schema changed on disk; reloaded."); }
      });
      es.onerror = () => { setLive(false); es?.close(); retry = window.setTimeout(connect, 3000); };
    };
    connect();
    return () => { es?.close(); window.clearTimeout(retry); };
  }, [reload, toast]);

  const apply = useCallback(async (ops: Op[], reason: string) => {
    try {
      const r = await api.ops(ops, versionRef.current, reason);
      if (!r.ok) { toast("error", `${r.message}: ${r.errors.map((e) => e.message).join("; ")}`); return false; }
      versionRef.current = r.version;
      await reload();
      return true;
    } catch (e) {
      if (e instanceof ConflictError) { toast("error", "Someone else changed the schema. Reloaded; please redo your change."); await reload(); }
      else toast("error", String(e));
      return false;
    }
  }, [reload, toast]);

  const ctx: Ctx | null = useMemo(() => state && {
    state, apply, reload, selected, select, highlight, toast, refTable, setRefTable,
    setHighlight: (h: Set<string>, label?: string) => { setHl(h); setHlLabel(label); },
    openTab: (side: "left" | "bottom", tab: string) => (side === "left" ? setLeft(tab) : setBottom(tab)),
  }, [state, apply, reload, selected, highlight, toast, refTable]);

  if (!state || !ctx) {
    return <div className="boot">{loadErr ? <><b>Cannot load the schema.</b><pre>{loadErr}</pre><p>Start the API: <code>uvicorn api.main:app --port 8000</code>, and run the first import if needed.</p></> : "Loading…"}</div>;
  }
  const table = state.schema.tables.find((t) => t.name === selected);
  const errCount = state.issues.filter((i) => i.severity === "error").length;
  const deliveryOnly = DELIVERY.every((l) => visible.has(l)) && visible.size === DELIVERY.length;

  return (
    <AppCtx.Provider value={ctx}>
      <div className="app">
        <header>
          <b className="brand">Schema Playground</b>
          <input className="search" placeholder="Search tables, columns, CDP alias, protocol ID…" value={search} onChange={(e) => setSearch(e.target.value)} />
          <div className="layers">
            {LAYERS.map((l) => (
              <button key={l} className={`lchip${visible.has(l) ? " on" : ""}`} style={{ "--c": LAYER_COLOR[l] } as React.CSSProperties}
                onClick={() => { const s = new Set(visible); if (s.has(l)) s.delete(l); else s.add(l); setVisible(s); }}>{l}</button>
            ))}
            <button className="lchip toggle" onClick={() => setVisible(new Set(deliveryOnly ? LAYERS : DELIVERY))}>
              {deliveryOnly ? "All layers" : "Delivery only"}
            </button>
          </div>
          {highlight.size > 0 && <button className="hlclear" onClick={() => ctx.setHighlight(new Set())}>Highlight: {hlLabel} ×</button>}
          <span className="spacer" />
          <span className={`live${live ? " on" : ""}`} title={live ? "Live: watching schema.json" : "Not connected to live updates"}>●</span>
          <span className="ver" title="Schema version hash">v {state.version.slice(0, 8)}</span>
          <span className={`errs${errCount ? " bad" : ""}`} onClick={() => setBottom("issues")}>{errCount} errors · {state.conflicts.length} conflicts</span>
        </header>
        <div className="body">
          <aside className={`left${left ? "" : " collapsed"}`}>
            <nav>
              {LEFT_TABS.map(([k, label]) => <button key={k} className={left === k ? "on" : ""} onClick={() => setLeft(left === k ? null : k)}>{label}</button>)}
            </nav>
            {left === "fields" && <FieldTray />}
            {left === "checks" && <ChecksPanel />}
            {left === "ref" && <RefEditor />}
          </aside>
          <main>
            <ReactFlowProvider>
              <Canvas visible={visible} search={search} />
            </ReactFlowProvider>
            <section className={`bottombar${bottom ? "" : " collapsed"}`}>
              <nav>
                {BOTTOM_TABS.map(([k, label]) => <button key={k} className={bottom === k ? "on" : ""} onClick={() => setBottom(bottom === k ? null : k)}>{label}</button>)}
              </nav>
              {bottom && (
                <div className="bp">
                  {bottom === "issues" && <IssuesPanel />}
                  {bottom === "import" && <ImportPanel />}
                  {bottom === "history" && <ChangelogPanel />}
                  {bottom === "export" && <ExportPanel />}
                </div>
              )}
            </section>
          </main>
          {table && <aside className="right"><TableEditor key={table.name} table={table} /></aside>}
        </div>
        <div className="toasts">{toasts.map((t) => <div key={t.id} className={`toast ${t.kind}`}>{t.text}</div>)}</div>
      </div>
    </AppCtx.Provider>
  );
}
