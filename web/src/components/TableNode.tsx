import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { memo, useState } from "react";
import { LAYER_COLOR } from "../ctx";
import type { Table } from "../types";

export type TableNodeData = {
  table: Table;
  fkCols: Set<string>;
  highlight: Set<string>;
  dimmed: boolean;
  selected: boolean;
  issues: number;
  onDropField: (table: string, field: string) => void;
  onSelect: (table: string) => void;
};

export type TableNodeType = Node<TableNodeData, "table">;

function TableNodeImpl({ data }: NodeProps<TableNodeType>) {
  const { table: t, fkCols, highlight, dimmed, selected, issues } = data;
  const [over, setOver] = useState(false);
  const color = LAYER_COLOR[t.layer];
  const pk = new Set(t.primary_key);
  const hl = highlight.has(t.name);
  return (
    <div
      className={`tnode${selected ? " sel" : ""}${dimmed ? " dim" : ""}${hl ? " hl" : ""}${over ? " over" : ""}`}
      style={{ borderColor: selected ? color : undefined }}
      onDragOver={(e) => { if (e.dataTransfer.types.includes("text/x-field")) { e.preventDefault(); setOver(true); } }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { setOver(false); const f = e.dataTransfer.getData("text/x-field"); if (f) { e.preventDefault(); data.onDropField(t.name, f); } }}
      onDoubleClick={() => data.onSelect(t.name)}
    >
      <div className="thead" style={{ background: color }}>
        <span className="tname">{t.name}</span>
        <span className="tlayer">{t.layer}{t.layer === "ref" ? ` · ${t.rows.length}` : ""}</span>
        {issues > 0 && <span className="tissue" title={`${issues} validation error(s)`}>!</span>}
      </div>
      {t.grain && <div className="tgrain" title={t.description}>{t.grain}</div>}
      <div className="tcols">
        {t.columns.map((c) => {
          const key = `${t.name}.${c.name}`;
          return (
            <div key={c.name} className={`tcol${highlight.has(key) ? " hl" : ""}${c.needs_confirmation ? " confirm" : ""}`} title={c.description}>
              <Handle type="target" position={Position.Left} id={`${c.name}-t`} className="h" />
              <span className="kicon">{pk.has(c.name) ? "🔑" : fkCols.has(c.name) ? "↗" : ""}</span>
              <span className={`cname${c.field_id ? " linked" : ""}`}>{c.name}{c.needs_confirmation ? " †" : ""}</span>
              <span className="ctype">{c.type}{c.mode === "REQUIRED" ? "!" : c.mode === "REPEATED" ? "[]" : ""}</span>
              <Handle type="source" position={Position.Right} id={`${c.name}-s`} className="h" />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export const TableNode = memo(TableNodeImpl);
