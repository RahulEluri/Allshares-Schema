import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { memo } from "react";
import type { DerivedView } from "../types";

export type ViewNodeData = { view: DerivedView; highlight: Set<string>; dimmed: boolean; selected: boolean };
export type ViewNodeType = Node<ViewNodeData, "view">;

/** A derived view: values calculated from its source table (dashed card, read-only). */
function ViewNodeImpl({ data }: NodeProps<ViewNodeType>) {
  const { view: v, highlight, dimmed, selected } = data;
  return (
    <div className={`tnode vnode${selected ? " sel" : ""}${dimmed ? " dim" : ""}${highlight.has(v.name) ? " hl" : ""}`}>
      <Handle type="target" position={Position.Left} id="src" className="h" isConnectable={false} />
      <div className="thead vhead">
        <span className="tname">{v.name}</span>
        <span className="tlayer">derived view</span>
      </div>
      <div className="tgrain" title={v.description}>from {v.source_table} · per {v.group_by.join(", ")}</div>
      <div className="tcols">
        {v.group_by.map((g) => (
          <div key={g} className="tcol"><span className="kicon" /><span className="cname">{g}</span><span className="ctype">key</span></div>
        ))}
        {v.columns.map((c) => (
          <div key={c.name} className={`tcol${highlight.has(`${v.name}.${c.name}`) ? " hl" : ""}`} title={`${c.description}\n= ${c.expression}`}>
            <span className="kicon">ƒ</span>
            <span className={`cname${c.field_id ? " linked" : ""}`}>{c.name}</span>
            <span className="ctype">{c.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export const ViewNode = memo(ViewNodeImpl);
