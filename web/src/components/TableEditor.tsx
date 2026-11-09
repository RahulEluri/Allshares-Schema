import { useEffect, useState } from "react";
import { LAYER_COLOR, useApp } from "../ctx";
import { BQ_TYPES, LAYERS, type Column, type Op, type Table } from "../types";

/** Text input that commits on blur / Enter, and resets when the source value changes. */
function Cell({ value, onCommit, placeholder, list, className, disabled }: {
  value: string; onCommit: (v: string) => void; placeholder?: string; list?: string; className?: string; disabled?: boolean;
}) {
  const [v, setV] = useState(value);
  useEffect(() => setV(value), [value]);
  const commit = () => { if (v !== value) onCommit(v); };
  return (
    <input className={className} value={v} placeholder={placeholder} list={list} disabled={disabled}
      onChange={(e) => setV(e.target.value)} onBlur={commit}
      onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); if (e.key === "Escape") setV(value); }} />
  );
}

export function TableEditor({ table: t }: { table: Table }) {
  const { state, apply, select, setRefTable, openTab } = useApp();
  const fields = state.schema.catalogue.fields;
  const checks = state.column_checks;
  const rels = state.schema.relationships;
  const outgoing = rels.filter((r) => r.from_table === t.name);
  const incoming = rels.filter((r) => r.to_table === t.name);
  const [newCol, setNewCol] = useState({ name: "", type: "STRING", field: "" });
  const [fk, setFk] = useState<{ to: string; cols: string[] }>({ to: "", cols: [] });
  const go = (ops: Op[], reason: string) => apply(ops, `UI: ${reason}`);
  const alterCol = (c: Column, changes: Record<string, unknown>) =>
    go([{ op: "alter_column", table: t.name, column: c.name, changes }], `alter ${t.name}.${c.name}`);
  const fieldOf = (id?: string) => fields.find((f) => f.name === id);
  const partitionable = t.columns.filter((c) => ["DATE", "DATETIME", "TIMESTAMP", "INT64"].includes(c.type.toUpperCase()));
  const target = state.schema.tables.find((x) => x.name === fk.to);

  const togglePk = (name: string) => {
    const next = t.primary_key.includes(name) ? t.primary_key.filter((x) => x !== name) : [...t.primary_key, name];
    go([{ op: "set_primary_key", table: t.name, columns: next }], `primary key of ${t.name}`);
  };
  const movePk = (i: number, d: -1 | 1) => {
    const k = [...t.primary_key]; const j = i + d;
    if (j < 0 || j >= k.length) return;
    [k[i], k[j]] = [k[j], k[i]];
    go([{ op: "set_primary_key", table: t.name, columns: k }], `reorder primary key of ${t.name}`);
  };

  return (
    <div className="editor">
      <div className="ed-head" style={{ borderLeftColor: LAYER_COLOR[t.layer] }}>
        <Cell className="ed-title" value={t.name} onCommit={(v) => go([{ op: "rename_table", table: t.name, new_name: v }], `rename ${t.name}`).then((ok) => ok && select(v))} />
        <button className="x" onClick={() => select(null)} title="Close">×</button>
      </div>
      <div className="grid2">
        <label>Layer</label>
        <select value={t.layer} onChange={(e) => go([{ op: "alter_table", table: t.name, changes: { layer: e.target.value } }], `layer of ${t.name}`)}>
          {LAYERS.map((l) => <option key={l}>{l}</option>)}
        </select>
        <label>Grain</label>
        <Cell value={t.grain} placeholder="one row per …" onCommit={(v) => go([{ op: "alter_table", table: t.name, changes: { grain: v } }], `grain of ${t.name}`)} />
        <label>Description</label>
        <Cell value={t.description} onCommit={(v) => go([{ op: "alter_table", table: t.name, changes: { description: v } }], `description of ${t.name}`)} />
        <label>Primary key</label>
        <div className="chips">
          {t.primary_key.map((k, i) => (
            <span key={k} className="chip pk">{k}
              <button onClick={() => movePk(i, -1)} title="Move left">‹</button>
              <button onClick={() => movePk(i, 1)} title="Move right">›</button>
              <button onClick={() => togglePk(k)} title="Remove">×</button>
            </span>
          ))}
          <select value="" onChange={(e) => e.target.value && togglePk(e.target.value)}>
            <option value="">+ add</option>
            {t.columns.filter((c) => !t.primary_key.includes(c.name)).map((c) => <option key={c.name}>{c.name}</option>)}
          </select>
        </div>
        <label>Partition</label>
        <div className="row">
          <select value={t.partition_by ?? ""} onChange={(e) => {
            const col = t.columns.find((c) => c.name === e.target.value);
            const op: Op = { op: "set_partition", table: t.name, column: e.target.value || null };
            if (col?.type.toUpperCase() === "INT64") op.range = { start: 2000, end: 2100, interval: 1 };
            go([op], `partition of ${t.name}`);
          }}>
            <option value="">none</option>
            {partitionable.map((c) => <option key={c.name} value={c.name}>{c.name} ({c.type})</option>)}
          </select>
          {t.partition_range && <span className="muted">range {t.partition_range.start}–{t.partition_range.end} step {t.partition_range.interval}</span>}
        </div>
        <label>Cluster ({t.cluster_by.length}/4)</label>
        <div className="chips">
          {t.cluster_by.map((k) => (
            <span key={k} className="chip">{k}<button onClick={() => go([{ op: "set_clustering", table: t.name, columns: t.cluster_by.filter((x) => x !== k) }], `clustering of ${t.name}`)}>×</button></span>
          ))}
          {t.cluster_by.length < 4 && (
            <select value="" onChange={(e) => e.target.value && go([{ op: "set_clustering", table: t.name, columns: [...t.cluster_by, e.target.value] }], `clustering of ${t.name}`)}>
              <option value="">+ add</option>
              {t.columns.filter((c) => !t.cluster_by.includes(c.name)).map((c) => <option key={c.name}>{c.name}</option>)}
            </select>
          )}
        </div>
        {t.holds_fields.length > 0 && (<><label>Holds fields</label><div className="muted">{t.holds_fields.join(", ")}</div></>)}
        {t.layer === "ref" && (<><label>Ref data</label><div><button className="link" onClick={() => { setRefTable(t.name); openTab("left", "ref"); }}>Edit {t.rows.length} value(s)</button></div></>)}
      </div>

      <datalist id="bqtypes">{BQ_TYPES.map((x) => <option key={x} value={x} />)}<option value="ARRAY<STRING>" /><option value="STRUCT<a STRING>" /></datalist>
      <datalist id="fieldnames">{fields.map((f) => <option key={f.name} value={f.name}>{f.status !== "active" ? f.status : ""}</option>)}</datalist>

      <h4>Columns ({t.columns.length})</h4>
      <div className="colgrid">
        <div className="cg-h">Name</div><div className="cg-h">Type</div><div className="cg-h">Mode</div>
        <div className="cg-h">Field</div><div className="cg-h">CDP alias</div><div className="cg-h" />
        {t.columns.map((c) => {
          const f = fieldOf(c.field_id);
          const cks = checks[`${t.name}.${c.name}`] ?? [];
          return (
            <div className="cg-row" key={c.name}>
              <Cell value={c.name} className={c.needs_confirmation ? "confirm" : ""} onCommit={(v) => go([{ op: "rename_column", table: t.name, column: c.name, new_name: v }], `rename ${t.name}.${c.name}`)} />
              <Cell value={c.type} list="bqtypes" onCommit={(v) => alterCol(c, { type: v })} />
              <select value={c.mode} onChange={(e) => alterCol(c, { mode: e.target.value })}>
                <option>NULLABLE</option><option>REQUIRED</option><option>REPEATED</option>
              </select>
              <Cell value={c.field_id ?? ""} list="fieldnames" placeholder="—" onCommit={(v) => go([{ op: "link_column_field", table: t.name, column: c.name, field_name: v || null }], `link ${t.name}.${c.name}`)} />
              <Cell value={c.cdp_alias ?? ""} placeholder="—" onCommit={(v) => alterCol(c, { cdp_alias: v || null })} />
              <button className="x" title="Delete column" onClick={() => {
                const used = rels.some((r) => (r.from_table === t.name && r.from_columns.includes(c.name)) || (r.to_table === t.name && r.to_columns.includes(c.name)));
                if (!window.confirm(used ? `${c.name} is used by a relationship. Delete it and the relationship?` : `Delete ${t.name}.${c.name}?`)) return;
                go([{ op: "delete_column", table: t.name, column: c.name, cascade: used }], `delete ${t.name}.${c.name}`);
              }}>×</button>
              <div className="cg-sub">
                <Cell value={c.description} placeholder="description" className="desc" onCommit={(v) => alterCol(c, { description: v })} />
                <div className="lineage">
                  {c.protocol_id && <span title="Protocol ID">{c.protocol_id}</span>}
                  {c.priority && <span title="Priority">{c.priority}</span>}
                  {c.requirement && <span title="Requirement (metadata only)" className={c.requirement.startsWith("Required") ? "req" : ""}>{c.requirement}</span>}
                  {c.severity && <span title="Severity">{c.severity}</span>}
                  {c.validation_rule && <span title="Validation rule">rule: {c.validation_rule.description ?? c.validation_rule.kind}</span>}
                  {c.needs_confirmation && <span className="confirm" title="Not in the field catalogue; confirm with the team">† confirm</span>}
                  {f && f.status !== "active" && <span>{f.status}</span>}
                  {cks.length > 0 && <span className="checks" title={cks.join(", ")}>{cks.length} checks</span>}
                  {c.owner === "app" && <span className="app" title="Edited in the app; protected on re-import">app</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="addrow">
        <input placeholder="new_column" value={newCol.name} onChange={(e) => setNewCol({ ...newCol, name: e.target.value })} />
        <input list="bqtypes" value={newCol.type} onChange={(e) => setNewCol({ ...newCol, type: e.target.value })} />
        <input list="fieldnames" placeholder="field (optional)" value={newCol.field} onChange={(e) => setNewCol({ ...newCol, field: e.target.value })} />
        <button disabled={!newCol.name} onClick={() => {
          const op: Op = { op: "add_column", table: t.name, name: newCol.name };
          if (newCol.field) op.field_id = newCol.field; else op.type = newCol.type;
          go([op], `add ${t.name}.${newCol.name}`).then((ok) => ok && setNewCol({ name: "", type: "STRING", field: "" }));
        }}>Add column</button>
      </div>

      <h4>Relationships</h4>
      <ul className="rels">
        {outgoing.map((r) => (
          <li key={r.name}>({r.from_columns.join(", ")}) → <button className="link" onClick={() => select(r.to_table)}>{r.to_table}</button>({r.to_columns.join(", ")})
            <span className="muted"> {r.cardinality}</span>
            <button className="x" title="Delete" onClick={() => go([{ op: "delete_relationship", name: r.name }], `delete ${r.name}`)}>×</button></li>
        ))}
        {incoming.map((r) => (
          <li key={r.name} className="muted">← <button className="link" onClick={() => select(r.from_table)}>{r.from_table}</button>({r.from_columns.join(", ")})</li>
        ))}
      </ul>
      <div className="addrow">
        <select value={fk.to} onChange={(e) => {
          const tgt = state.schema.tables.find((x) => x.name === e.target.value);
          setFk({ to: e.target.value, cols: (tgt?.primary_key ?? []).map((k) => (t.columns.some((c) => c.name === k) ? k : "")) });
        }}>
          <option value="">FK to table…</option>
          {state.schema.tables.filter((x) => x.primary_key.length && x.name !== t.name).map((x) => <option key={x.name}>{x.name}</option>)}
        </select>
        {target?.primary_key.map((k, i) => (
          <select key={k} value={fk.cols[i] ?? ""} onChange={(e) => { const cols = [...fk.cols]; cols[i] = e.target.value; setFk({ ...fk, cols }); }} title={`maps to ${target.name}.${k}`}>
            <option value="">{k} ←</option>
            {t.columns.map((c) => <option key={c.name}>{c.name}</option>)}
          </select>
        ))}
        <button disabled={!target || fk.cols.some((c) => !c)} onClick={() =>
          go([{ op: "add_relationship", from_table: t.name, from_columns: fk.cols, to_table: fk.to }], `relationship ${t.name} → ${fk.to}`).then((ok) => ok && setFk({ to: "", cols: [] }))}>Add FK</button>
      </div>

      <div className="danger">
        <button onClick={() => {
          const used = incoming.length + outgoing.length > 0;
          if (!window.confirm(used ? `Delete ${t.name} and its ${incoming.length + outgoing.length} relationship(s)?` : `Delete ${t.name}?`)) return;
          go([{ op: "delete_table", table: t.name, cascade: used }], `delete ${t.name}`).then((ok) => ok && select(null));
        }}>Delete table</button>
      </div>
    </div>
  );
}
