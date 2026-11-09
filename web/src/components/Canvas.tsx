import {
  Background, Controls, MiniMap, ReactFlow, ConnectionMode, applyNodeChanges, useReactFlow,
  type Connection, type Edge, type NodeChange,
} from "@xyflow/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { LAYER_COLOR, useApp } from "../ctx";
import type { DerivedView, Layer, Table } from "../types";
import { TableNode, type TableNodeType } from "./TableNode";
import { ViewNode, type ViewNodeType } from "./ViewNode";

const nodeTypes = { table: TableNode, view: ViewNode };
const COL_X: Record<Layer, number> = { ref: 0, catalogue: 1, dim: 2, provenance: 3, fact: 4, child: 5, bridge: 5 };
type AnyNode = TableNodeType | ViewNodeType;

function autoLayout(tables: Table[], views: DerivedView[]): Record<string, { x: number; y: number }> {
  const pos: Record<string, { x: number; y: number }> = {};
  const colY: Record<number, number> = {};
  const refs = tables.filter((t) => t.layer === "ref");
  refs.forEach((t, i) => { pos[t.name] = { x: (i % 2) * 250, y: Math.floor(i / 2) * 175 }; });
  for (const t of tables) {
    if (t.layer === "ref") continue;
    const col = COL_X[t.layer] + 1;
    const y = colY[col] ?? 0;
    pos[t.name] = { x: 520 + (col - 1) * 300, y };
    colY[col] = y + 60 + t.columns.length * 19 + 40;
  }
  for (const v of views) {
    const src = pos[v.source_table] ?? { x: 0, y: 0 };
    pos[v.name] = { x: src.x + 290, y: src.y };
  }
  return pos;
}

export function Canvas({ visible, search }: { visible: Set<Layer>; search: string }) {
  const { state, apply, selected, select, highlight, toast } = useApp();
  const { tables, relationships } = state.schema;
  const views = useMemo(() => state.schema.views ?? [], [state.schema.views]);
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const saveTimer = useRef<number | undefined>(undefined);
  const rf = useReactFlow();
  useEffect(() => {
    const id = window.setTimeout(() => rf.fitView({ padding: 0.05, duration: 200 }), 60);
    return () => window.clearTimeout(id);
  }, [visible, rf]);

  useEffect(() => {
    const auto = autoLayout(tables, views);
    setPositions((cur) => ({ ...auto, ...state.layout.positions, ...cur }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.version]);

  const onDropField = useCallback((table: string, field: string) => {
    apply([{ op: "add_column", table, name: field, field_id: field }], `UI: place field ${field} in ${table}`);
  }, [apply]);

  const errorsByTable = useMemo(() => {
    const m: Record<string, number> = {};
    for (const i of state.issues) if (i.severity === "error" && i.table) m[i.table] = (m[i.table] ?? 0) + 1;
    return m;
  }, [state.issues]);

  const q = search.trim().toLowerCase();
  const searchHl = useMemo(() => {
    const s = new Set<string>();
    if (!q) return s;
    for (const t of tables) {
      if (t.name.includes(q)) s.add(t.name);
      for (const c of t.columns) {
        if ([c.name, c.cdp_alias, c.protocol_id, c.field_id, c.description].some((v) => v && v.toLowerCase().includes(q))) {
          s.add(t.name); s.add(`${t.name}.${c.name}`);
        }
      }
    }
    return s;
  }, [q, tables]);
  const hl = q ? searchHl : highlight;

  const layerOf = useCallback((name: string) => tables.find((t) => t.name === name)?.layer as Layer, [tables]);
  const shownViews = useMemo(() => views.filter((v) => visible.has(layerOf(v.source_table))), [views, visible, layerOf]);

  const nodes: AnyNode[] = useMemo(() => [
    ...tables.filter((t) => visible.has(t.layer)).map((t): TableNodeType => ({
      id: t.name, type: "table", position: positions[t.name] ?? { x: 0, y: 0 }, dragHandle: ".thead",
      data: {
        table: t, highlight: hl, selected: selected === t.name, issues: errorsByTable[t.name] ?? 0,
        dimmed: hl.size > 0 && !hl.has(t.name),
        fkCols: new Set(relationships.filter((r) => r.from_table === t.name).flatMap((r) => r.from_columns)),
        onDropField, onSelect: select,
      },
    })),
    ...shownViews.map((v): ViewNodeType => ({
      id: v.name, type: "view", position: positions[v.name] ?? { x: 0, y: 0 }, dragHandle: ".thead",
      data: { view: v, highlight: hl, selected: selected === v.name, dimmed: hl.size > 0 && !hl.has(v.name) },
    })),
  ], [tables, shownViews, visible, positions, hl, selected, relationships, errorsByTable, onDropField, select]);

  const edges: Edge[] = useMemo(() => [
    ...relationships
      .filter((r) => visible.has(layerOf(r.from_table)) && visible.has(layerOf(r.to_table)))
      .map((r) => ({
        id: r.name, source: r.from_table, target: r.to_table,
        sourceHandle: `${r.from_columns[0]}-s`, targetHandle: `${r.to_columns[0]}-t`,
        type: "smoothstep", markerStart: r.cardinality === "one_to_one" ? "one" : "many", markerEnd: "one",
        label: r.from_columns.length > 1 ? `(${r.from_columns.join(", ")})` : undefined,
        className: selected && (r.from_table === selected || r.to_table === selected) ? "edge-sel" : "",
        data: { name: r.name },
      })),
    ...shownViews.map((v) => ({
      id: `view:${v.name}`, source: v.source_table, target: v.name,
      sourceHandle: `${v.group_by[0]}-s`, targetHandle: "src", type: "smoothstep",
      className: "edge-derive", label: "derives", deletable: false, data: { view: true },
    })),
  ], [relationships, shownViews, visible, selected, layerOf]);

  const onNodesChange = useCallback((changes: NodeChange<AnyNode>[]) => {
    const moved = changes.filter((c) => c.type === "position" && c.position);
    if (!moved.length) return;
    setPositions((cur) => {
      const next = { ...cur };
      const nodesNow = applyNodeChanges(moved, nodes);
      for (const n of nodesNow) next[n.id] = n.position;
      window.clearTimeout(saveTimer.current);
      saveTimer.current = window.setTimeout(() => api.layout(next), 600);
      return next;
    });
  }, [nodes]);

  const onConnect = useCallback((c: Connection) => {
    const src = tables.find((t) => t.name === c.source);
    const dst = tables.find((t) => t.name === c.target);
    if (!src || !dst || !c.sourceHandle || !c.targetHandle) return;
    let fromT = src, toT = dst;
    let fromCol = c.sourceHandle.replace(/-[st]$/, ""), toCol = c.targetHandle.replace(/-[st]$/, "");
    if (!toT.primary_key.includes(toCol) && fromT.primary_key.includes(fromCol)) {
      [fromT, toT, fromCol, toCol] = [toT, fromT, toCol, fromCol];
    }
    if (!toT.primary_key.includes(toCol)) {
      toast("error", `Drag from a foreign-key column to a primary-key column (${toT.name}.${toCol} is not in its key).`);
      return;
    }
    let fromCols: string[];
    if (toT.primary_key.length === 1) fromCols = [fromCol];
    else {
      // Composite key: map the other key columns by name in the source table.
      fromCols = toT.primary_key.map((k) => (k === toCol ? fromCol : fromT.columns.find((x) => x.name === k)?.name ?? ""));
      if (fromCols.some((x) => !x)) {
        toast("error", `${toT.name} has a composite key (${toT.primary_key.join(", ")}); ${fromT.name} needs columns with those names. Use the side panel to map them.`);
        return;
      }
    }
    apply([{ op: "add_relationship", from_table: fromT.name, from_columns: fromCols, to_table: toT.name }],
      `UI: relationship ${fromT.name} → ${toT.name}`);
  }, [tables, apply, toast]);

  return (
    <div className="canvas">
      <svg style={{ position: "absolute", width: 0, height: 0 }}>
        <defs>
          <marker id="many" viewBox="0 0 12 12" refX="1" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse">
            <path d="M11 6 L1 1 M11 6 L1 6 M11 6 L1 11" stroke="#64748b" strokeWidth="1.2" fill="none" />
          </marker>
          <marker id="one" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto">
            <path d="M8 1 L8 11" stroke="#64748b" strokeWidth="1.4" />
          </marker>
        </defs>
      </svg>
      <ReactFlow
        nodes={nodes} edges={edges} nodeTypes={nodeTypes}
        onNodesChange={onNodesChange} onConnect={onConnect} connectionMode={ConnectionMode.Loose}
        onNodeClick={(_, n) => select(n.id)} onPaneClick={() => select(null)}
        onEdgeDoubleClick={(_, e) => {
          if (e.data?.view) return;
          if (window.confirm(`Delete relationship ${e.id}?`)) apply([{ op: "delete_relationship", name: e.id }], `UI: delete relationship ${e.id}`);
        }}
        minZoom={0.1} maxZoom={2} fitView fitViewOptions={{ padding: 0.05 }} proOptions={{ hideAttribution: true }}
        nodesConnectable elementsSelectable
      >
        <Background gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable nodeColor={(n) => (n.type === "view" ? "#a16207" : LAYER_COLOR[(n.data as { table: Table }).table.layer])} />
      </ReactFlow>
    </div>
  );
}
