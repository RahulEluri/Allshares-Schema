import { useApp } from "../ctx";
import type { DerivedView } from "../types";

/** Read-only details of a derived view. Edit views through MCP (set_view) or config/draft_schema.yaml. */
export function ViewPanel({ view: v }: { view: DerivedView }) {
  const { state, select, apply } = useApp();
  const checks = state.column_checks;
  return (
    <div className="editor">
      <div className="ed-head" style={{ borderLeftColor: "#a16207" }}>
        <span className="ed-title">{v.name}</span>
        <button className="x" onClick={() => select(null)} title="Close">×</button>
      </div>
      <p className="hint">{v.description}</p>
      <div className="grid2">
        <label>Calculated from</label>
        <div><button className="link" onClick={() => select(v.source_table)}>{v.source_table}</button></div>
        <label>One row per</label>
        <div>{v.group_by.join(", ")}</div>
      </div>
      <h4>Calculated columns ({v.columns.length})</h4>
      <table className="vtable">
        <thead><tr><th>Column</th><th>Type</th><th>Field</th><th>Calculation</th></tr></thead>
        <tbody>
          {v.columns.map((c) => {
            const cks = checks[`${v.name}.${c.name}`] ?? [];
            return (
              <tr key={c.name}>
                <td><b>{c.name}</b><div className="muted small">{c.description}</div></td>
                <td><code>{c.type}</code></td>
                <td>{c.field_id ?? "—"}{cks.length > 0 && <div className="lineage"><span className="checks" title={cks.join(", ")}>{cks.length} checks</span></div>}</td>
                <td><code className="expr">{c.expression}</code></td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="hint">Edit the calculations through Claude (MCP <code>set_view</code>) or in <code>config/draft_schema.yaml</code>.</p>
      <div className="danger">
        <button onClick={() => window.confirm(`Delete view ${v.name}?`) &&
          apply([{ op: "delete_view", name: v.name }], `UI: delete view ${v.name}`).then((ok) => ok && select(null))}>Delete view</button>
      </div>
    </div>
  );
}
