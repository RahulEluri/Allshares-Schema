import { useEffect, useMemo, useState } from "react";
import { api, ConflictError, type ExportResult, type ImportDiff } from "../api";
import { useApp } from "../ctx";

export function IssuesPanel() {
  const { state, select } = useApp();
  const errs = state.issues.filter((i) => i.severity === "error");
  const warns = state.issues.filter((i) => i.severity === "warning");
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="bp-split">
      <div>
        <h4>Validation · {errs.length} error(s), {warns.length} warning(s)</h4>
        <ul className="issues">
          {[...errs, ...warns].map((i, n) => (
            <li key={n} className={i.severity} onClick={() => i.table && select(i.table)}>
              <span className="sev">{i.severity}</span> <code>{i.code}</code> {i.message}
            </li>
          ))}
          {state.issues.length === 0 && <li className="muted">No issues.</li>}
        </ul>
      </div>
      <div>
        <h4>Conflicts · {state.conflicts.length} to resolve with the team</h4>
        <ul className="conflicts">
          {state.conflicts.map((c) => (
            <li key={c.id}>
              <div className="ctitle" onClick={() => setOpen(open === c.id ? null : c.id)}>
                <span className={`badge ${c.kind === "decision" ? "warn" : ""}`}>{c.kind}</span> <b>{c.title}</b>
                <span className="muted"> ({c.items.length})</span>
              </div>
              <div className="muted small">{c.detail}</div>
              {open === c.id && <ul className="items">{c.items.map((x) => <li key={x} onClick={() => select(x.split(/[.:\s]/)[0])}>{x}</li>)}</ul>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export function ImportPanel() {
  const { state, reload, toast } = useApp();
  const [diff, setDiff] = useState<ImportDiff | null>(null);
  const [sel, setSel] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState(false);
  const load = async () => {
    setBusy(true);
    try {
      const d = await api.importDiff();
      setDiff(d);
      setSel(new Set(d.items.filter((i) => i.applicable && !i.app_owned).map((i) => i.id)));
    } catch (e) { toast("error", String(e)); } finally { setBusy(false); }
  };
  useEffect(() => { load(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const groups = useMemo(() => {
    const g: Record<string, ImportDiff["items"]> = {};
    for (const i of diff?.items ?? []) (g[i.category] ??= []).push(i);
    return g;
  }, [diff]);
  const applySel = async () => {
    if (!diff) return;
    setBusy(true);
    try {
      const r = await api.importApply([...sel], state.version);
      if (r.ok) { toast("ok", r.message); await reload(); await load(); }
      else toast("error", `${r.message}: ${r.errors.map((e) => e.message).join("; ")}`);
    } catch (e) {
      toast("error", e instanceof ConflictError ? "The schema changed; diff reloaded." : String(e));
      await reload(); await load();
    } finally { setBusy(false); }
  };
  const fmt = (v: unknown) => (v === null || v === undefined ? "∅" : typeof v === "string" ? v : JSON.stringify(v));
  return (
    <div className="importp">
      <div className="row">
        <button onClick={load} disabled={busy}>Re-read workbooks</button>
        <button onClick={applySel} disabled={busy || sel.size === 0}>Apply {sel.size} selected</button>
        {diff && <span className="muted">{diff.items.length === 0 ? "No differences: schema.json matches the workbooks." : `${diff.items.length} difference(s)`}</span>}
        {diff?.notices.map((n) => <span key={n} className="badge warn" title={n}>{n}</span>)}
      </div>
      {Object.entries(groups).map(([cat, items]) => (
        <div key={cat} className="dgroup">
          <h4>{cat} <span className="muted">{Object.entries(diff!.summary[cat] ?? {}).filter(([, n]) => n).map(([k, n]) => `${n} ${k}`).join(", ")}</span></h4>
          {items.map((i) => (
            <div key={i.id} className={`ditem ${i.kind}${i.applicable ? "" : " flagged"}`}>
              <input type="checkbox" disabled={!i.applicable} checked={sel.has(i.id)} onChange={(e) => {
                const s = new Set(sel); if (e.target.checked) s.add(i.id); else s.delete(i.id); setSel(s);
              }} />
              <span className={`badge k-${i.kind}`}>{i.kind}</span>
              <b>{i.label}</b>
              {i.app_owned && <span className="badge warn" title="Edited in the app. Accepting overwrites the app edit.">app-owned</span>}
              {!i.applicable && <span className="muted small"> {i.reason}</span>}
              {Object.keys(i.changes).length > 0 && (
                <div className="dchanges">{Object.entries(i.changes).map(([k, v]) => (
                  <div key={k}><code>{k}</code>: <s>{fmt(v.before)}</s> → <span>{fmt(v.after)}</span></div>
                ))}</div>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function ChangelogPanel() {
  const { state } = useApp();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  useEffect(() => { api.changelog().then(setRows).catch(() => setRows([])); }, [state.version]);
  const target = (a: Record<string, unknown>) =>
    [a.table, a.column, a.name, a.from_table && `${a.from_table}→${a.to_table}`, a.code, a.field_name, a.check_code, (a.field as { name?: string })?.name]
      .filter(Boolean).join(" ");
  return (
    <table className="logt">
      <thead><tr><th>When (UTC)</th><th>Actor</th><th>Operation</th><th>Target</th><th>Reason</th><th>Version</th></tr></thead>
      <tbody>
        {rows.map((r, i) => {
          const a = (r.args ?? {}) as Record<string, unknown>;
          return (
            <tr key={i} title={JSON.stringify(a, null, 1)}>
              <td>{String(r.ts).replace("T", " ").replace("+00:00", "")}</td>
              <td><span className={`badge actor-${r.actor}`}>{String(r.actor)}{r.source ? ` · ${r.source}` : ""}</span></td>
              <td><code>{String(r.op)}</code></td>
              <td>{target(a)}</td>
              <td>{String(r.reason ?? "")}</td>
              <td className="muted">{String(r.version_after ?? "")}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function ExportPanel() {
  const { state, toast, reload } = useApp();
  const [res, setRes] = useState<ExportResult | null>(null);
  const [cfg, setCfg] = useState(state.settings);
  const [bq, setBq] = useState<ExportResult["bq_dry_run"] | null>(null);
  useEffect(() => { api.exportSql().then(setRes).catch((e) => toast("error", String(e))); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.version, state.settings]);
  useEffect(() => setCfg(state.settings), [state.settings]);
  const copy = async (text: string, what: string) => {
    try { await navigator.clipboard.writeText(text); toast("ok", `Copied ${what}`); } catch { toast("error", "Clipboard not available"); }
  };
  const copyTable = async (t: string) => copy((await api.exportSql(t)).sql, t);
  return (
    <div className="exportp">
      <div className="exp-side">
        <h4>Settings</h4>
        <label>Project<input value={cfg.project} onChange={(e) => setCfg({ ...cfg, project: e.target.value })} /></label>
        <label>Dataset<input value={cfg.dataset} onChange={(e) => setCfg({ ...cfg, dataset: e.target.value })} /></label>
        <label>Location<input value={cfg.location ?? ""} placeholder="optional, e.g. EU" onChange={(e) => setCfg({ ...cfg, location: e.target.value })} /></label>
        <button onClick={async () => { await api.settings(cfg); await reload(); toast("ok", "Settings saved"); }}>Save settings</button>
        <h4>Per table ({res?.order.length ?? 0}, dependency order)</h4>
        <ul className="ptab">{res?.order.map((t) => <li key={t}><span>{t}</span><button onClick={() => copyTable(t)}>Copy</button></li>)}</ul>
      </div>
      <div className="exp-main">
        <div className="row">
          <button disabled={!res} onClick={() => res && copy(res.sql, "full script")}>Copy full script</button>
          {res && (res.parse_check.ok
            ? <span className="badge ok">sqlglot (BigQuery): {res.parse_check.statements} statements parse</span>
            : <span className="badge error">sqlglot: {res.parse_check.error}</span>)}
          <button onClick={async () => { const r = await api.exportSql(undefined, true); setBq(r.bq_dry_run); }}>bq --dry_run</button>
          {bq && <span className={`badge ${bq.ok ? "ok" : "warn"}`} title={bq.output}>{bq.available ? (bq.ok ? "bq dry run OK" : "bq dry run failed (hover)") : "bq not installed"}</span>}
        </div>
        <textarea readOnly value={res?.sql ?? "Loading…"} spellCheck={false} />
      </div>
    </div>
  );
}
