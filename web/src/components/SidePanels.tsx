import { useEffect, useMemo, useState } from "react";
import { columnsForCheck, useApp } from "../ctx";
import type { Check } from "../types";

export function FieldTray() {
  const { state, apply } = useApp();
  const [showAll, setShowAll] = useState(false);
  const [q, setQ] = useState("");
  const [adding, setAdding] = useState({ name: "", format: "Text" });
  const fields = state.schema.catalogue.fields.filter((f) =>
    (showAll || !state.placed[f.name]) && (!q || f.name.includes(q.toLowerCase()) || (f.description ?? "").toLowerCase().includes(q.toLowerCase())));
  return (
    <div className="panel">
      <p className="hint">Drag a field onto a table to add a linked column.</p>
      <div className="row">
        <input placeholder="filter" value={q} onChange={(e) => setQ(e.target.value)} />
        <label className="chk"><input type="checkbox" checked={showAll} onChange={(e) => setShowAll(e.target.checked)} /> all</label>
      </div>
      {fields.length === 0 && <p className="muted">Every field is placed.</p>}
      <ul className="tray">
        {fields.map((f) => (
          <li key={f.name} draggable onDragStart={(e) => { e.dataTransfer.setData("text/x-field", f.name); e.dataTransfer.effectAllowed = "copy"; }}
            title={`${f.description ?? ""}\n${f.note ?? ""}`}>
            <span className="fname">{f.name}</span>
            <span className={`badge ${f.status}`}>{f.status}</span>
            <span className="muted small">{[f.format, f.grain, f.protocol_id].filter(Boolean).join(" · ")}</span>
            {state.placed[f.name] && <span className="muted small">in {state.placed[f.name].join(", ")}</span>}
          </li>
        ))}
      </ul>
      <h4>New field</h4>
      <div className="row">
        <input placeholder="field_name" value={adding.name} onChange={(e) => setAdding({ ...adding, name: e.target.value })} />
        <select value={adding.format} onChange={(e) => setAdding({ ...adding, format: e.target.value })}>
          {["Text", "Code", "Date", "Money", "Number", "Number or %", "yes/no text", "Year", "List (name: value)"].map((x) => <option key={x}>{x}</option>)}
        </select>
        <button disabled={!adding.name} onClick={() => apply([{ op: "add_field", field: { name: adding.name, format: adding.format, status: "new" } }], `UI: add field ${adding.name}`)
          .then((ok) => ok && setAdding({ name: "", format: "Text" }))}>Add</button>
      </div>
    </div>
  );
}

export function ChecksPanel() {
  const { state, setHighlight, highlight } = useApp();
  const [f, setF] = useState({ type: "", fx: "", status: "", kind: "", q: "" });
  const [active, setActive] = useState<string | null>(null);
  const checks = state.schema.catalogue.checks;
  const statuses = useMemo(() => [...new Set(checks.map((c) => c.status))].sort(), [checks]);
  const counts = useMemo(() => {
    const m: Record<string, number> = {};
    for (const p of state.schema.catalogue.field_checks) m[p.check_code] = (m[p.check_code] ?? 0) + 1;
    return m;
  }, [state.schema.catalogue.field_checks]);
  useEffect(() => { if (highlight.size === 0) setActive(null); }, [highlight]);
  const shown = checks.filter((c) =>
    (!f.type || c.check_type === f.type) && (!f.fx || c.check_fx === f.fx) && (!f.status || c.status === f.status) &&
    (!f.kind || c.kind === f.kind) && (!f.q || `${c.code} ${c.name}`.toLowerCase().includes(f.q.toLowerCase())));
  const pick = (c: Check) => {
    if (active === c.code) { setActive(null); setHighlight(new Set()); return; }
    setActive(c.code);
    const codes = c.kind === "rule" ? c.parent_gates : [c.code];
    const all = new Set<string>();
    for (const code of codes) for (const x of columnsForCheck(state, code)) all.add(x);
    setHighlight(all, c.code);
  };
  return (
    <div className="panel">
      <div className="filters">
        <select value={f.type} onChange={(e) => setF({ ...f, type: e.target.value })}><option value="">hard/soft</option><option>hard</option><option>soft</option></select>
        <select value={f.fx} onChange={(e) => setF({ ...f, fx: e.target.value })}><option value="">direct/derived</option><option>direct</option><option>derived</option></select>
        <select value={f.status} onChange={(e) => setF({ ...f, status: e.target.value })}><option value="">status</option>{statuses.map((s) => <option key={s}>{s}</option>)}</select>
        <select value={f.kind} onChange={(e) => setF({ ...f, kind: e.target.value })}><option value="">gates+rules</option><option value="gate">gates</option><option value="rule">Conor rules</option></select>
        <input placeholder="search" value={f.q} onChange={(e) => setF({ ...f, q: e.target.value })} />
      </div>
      <p className="hint">{shown.length} of {checks.length}. Click a check to highlight its columns.</p>
      <ul className="checks">
        {shown.map((c) => (
          <li key={c.code} className={active === c.code ? "on" : ""} onClick={() => pick(c)}>
            <div><b>{c.code}</b> {c.name}</div>
            <div className="meta">
              {c.check_type && <span className={`badge ${c.check_type}`}>{c.check_type}</span>}
              {c.check_fx && <span className="badge">{c.check_fx}</span>}
              <span className={`badge st-${c.status}`}>{c.status}</span>
              {c.kind === "rule" && <span className="muted small">→ {c.parent_gates.join(", ")} {c.parent_relation ? `(${c.parent_relation})` : ""}</span>}
              {counts[c.code] !== undefined && <span className="muted small">{counts[c.code]} fields</span>}
              {c.undefined && <span className="badge warn">undefined</span>}
            </div>
            {active === c.code && (
              <div className="detail">
                {c.applies_when && <div><i>Applies when:</i> {c.applies_when}</div>}
                {c.result_if_not && <div><i>Result if not:</i> {c.result_if_not}</div>}
                {c.remarks && <div><i>Remarks:</i> {c.remarks}</div>}
                {c.proposed_change && <div><i>Proposed change:</i> {c.proposed_change.suggestion} <span className="muted">({c.proposed_change.why})</span></div>}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function RefEditor() {
  const { state, apply, refTable, setRefTable } = useApp();
  const refs = state.schema.tables.filter((t) => t.layer === "ref");
  const t = refs.find((x) => x.name === refTable) ?? refs[0];
  const [row, setRow] = useState({ code: "", label: "", meaning: "", status: "Proposed: confirm with Allshares" });
  if (!t) return <div className="panel muted">No ref tables.</div>;
  const upd = (code: string, changes: Record<string, unknown>) =>
    apply([{ op: "update_ref_value", table: t.name, code, changes }], `UI: edit ${t.name}.${code}`);
  return (
    <div className="panel">
      <select value={t.name} onChange={(e) => setRefTable(e.target.value)}>
        {refs.map((r) => <option key={r.name} value={r.name}>{r.name} ({r.rows.length})</option>)}
      </select>
      <p className="hint">{t.description}</p>
      <table className="reft">
        <thead><tr><th>code</th><th>label</th><th>meaning</th><th>status</th><th /></tr></thead>
        <tbody>
          {t.rows.map((r) => (
            <tr key={r.code} title={`${r.list_source ?? ""}${Object.keys(r.extra).length ? "\n" + JSON.stringify(r.extra) : ""}`}>
              <td><b>{r.code}</b></td>
              <td><RefCell v={r.label ?? ""} on={(v) => upd(r.code, { label: v })} /></td>
              <td><RefCell v={r.meaning ?? ""} on={(v) => upd(r.code, { meaning: v })} /></td>
              <td>
                <select value={r.status ?? ""} onChange={(e) => upd(r.code, { status: e.target.value })}>
                  {[...new Set([r.status ?? "", "In use", "Proposed: confirm with Allshares", "Proposed", "Review"])].map((s) => <option key={s} value={s}>{s || "—"}</option>)}
                </select>
              </td>
              <td><button className="x" onClick={() => window.confirm(`Delete ${r.code}?`) && apply([{ op: "delete_ref_value", table: t.name, code: r.code }], `UI: delete ${t.name}.${r.code}`)}>×</button></td>
            </tr>
          ))}
          {t.rows.length === 0 && <tr><td colSpan={5} className="muted">No values (no Fixed Sets sheet in the workbook).</td></tr>}
        </tbody>
      </table>
      <div className="row">
        <input placeholder="code" value={row.code} onChange={(e) => setRow({ ...row, code: e.target.value })} />
        <input placeholder="label" value={row.label} onChange={(e) => setRow({ ...row, label: e.target.value })} />
        <input placeholder="meaning" value={row.meaning} onChange={(e) => setRow({ ...row, meaning: e.target.value })} />
        <button disabled={!row.code} onClick={() => apply([{ op: "add_ref_value", table: t.name, ...row, list_source: "Schema playground" }], `UI: add ${t.name}.${row.code}`)
          .then((ok) => ok && setRow({ ...row, code: "", label: "", meaning: "" }))}>Add</button>
      </div>
    </div>
  );
}

function RefCell({ v, on }: { v: string; on: (v: string) => void }) {
  const [x, setX] = useState(v);
  useEffect(() => setX(v), [v]);
  return <input value={x} onChange={(e) => setX(e.target.value)} onBlur={() => x !== v && on(x)} onKeyDown={(e) => e.key === "Enter" && (e.target as HTMLInputElement).blur()} />;
}
