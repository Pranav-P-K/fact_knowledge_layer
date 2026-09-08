import { useState, useEffect, useRef, useCallback } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { listRelationships } from "../api";

const TYPE_COLORS = {
  SUPPORTS: "#22c55e",
  CONTRADICTS: "#ef4444",
  RECONCILES: "#f59e0b",
};

// Assign a stable color per document
const DOC_PALETTE = [
  "#6366f1", "#06b6d4", "#ec4899", "#84cc16",
  "#f97316", "#a855f7", "#14b8a6", "#eab308",
];

export default function KnowledgeGraph({ documents, onSelectFact, refreshKey }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState("");
  const fgRef = useRef();

  const docColorMap = {};
  (documents || []).forEach((d, i) => {
    docColorMap[d.id] = DOC_PALETTE[i % DOC_PALETTE.length];
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const rels = await listRelationships({ type: filterType || undefined });

      const nodeMap = {};
      const links = [];

      for (const r of rels) {
        // Node A
        if (!nodeMap[r.fact_id_a]) {
          nodeMap[r.fact_id_a] = {
            id: r.fact_id_a,
            name: r.fact_a_text,
            doc: r.fact_a_doc_name,
            docId: r.fact_a_doc_id,
            type: r.fact_a_type,
            color: docColorMap[r.fact_a_doc_id] || "#6366f1",
          };
        }
        // Node B
        if (!nodeMap[r.fact_id_b]) {
          nodeMap[r.fact_id_b] = {
            id: r.fact_id_b,
            name: r.fact_b_text,
            doc: r.fact_b_doc_name,
            docId: r.fact_b_doc_id,
            type: r.fact_b_type,
            color: docColorMap[r.fact_b_doc_id] || "#6366f1",
          };
        }
        links.push({
          source: r.fact_id_a,
          target: r.fact_id_b,
          type: r.relationship_type,
          explanation: r.explanation,
          confidence: r.confidence,
          color: TYPE_COLORS[r.relationship_type] || "#888",
        });
      }

      setGraphData({ nodes: Object.values(nodeMap), links });
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filterType, refreshKey, JSON.stringify(documents)]);

  useEffect(() => { load(); }, [load]);

  const handleNodeClick = useCallback((node) => {
    onSelectFact?.(node.id);
  }, [onSelectFact]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Controls */}
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ display: "flex", gap: 6 }}>
          {["", "SUPPORTS", "CONTRADICTS", "RECONCILES"].map((t) => (
            <button
              key={t}
              className={`tab${filterType === t ? " active" : ""}`}
              onClick={() => setFilterType(t)}
            >
              {t || "All"}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div style={{ marginLeft: "auto", display: "flex", gap: 12, fontSize: "0.75rem", color: "var(--c-text-muted)", alignItems: "center" }}>
          {Object.entries(TYPE_COLORS).map(([t, c]) => (
            <span key={t} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ width: 20, height: 2, background: c, display: "inline-block" }} />
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Document legend */}
      {documents.length > 0 && (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {documents.map((d, i) => (
            <span key={d.id} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
              <span style={{ width: 10, height: 10, borderRadius: "50%", background: DOC_PALETTE[i % DOC_PALETTE.length], flexShrink: 0 }} />
              {d.filename}
            </span>
          ))}
        </div>
      )}

      {/* Graph */}
      <div className="glass" style={{ overflow: "hidden", borderRadius: "var(--radius-lg)", height: 560, position: "relative" }}>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}>
            <div className="spinner" />
          </div>
        ) : graphData.nodes.length === 0 ? (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%", color: "var(--c-text-muted)" }}>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: "2rem", marginBottom: 8 }}>🔗</p>
              <p>No relationships found yet.</p>
              <p style={{ fontSize: "0.8rem" }}>Upload multiple PDFs to see connections.</p>
            </div>
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            backgroundColor="#0d0f14"
            nodeColor={(n) => n.color}
            nodeRelSize={6}
            nodeLabel={(n) => `${n.name}\n📄 ${n.doc}`}
            linkColor={(l) => l.color}
            linkWidth={2}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.004}
            linkDirectionalParticleColor={(l) => l.color}
            onNodeClick={handleNodeClick}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.name.slice(0, 40) + (node.name.length > 40 ? "…" : "");
              const fontSize = Math.max(10, 14 / globalScale);
              ctx.beginPath();
              ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI);
              ctx.fillStyle = node.color;
              ctx.fill();
              if (globalScale >= 0.8) {
                ctx.font = `${fontSize}px Inter, sans-serif`;
                ctx.fillStyle = "rgba(226,232,240,0.85)";
                ctx.textAlign = "center";
                ctx.fillText(label, node.x, node.y + 12);
              }
            }}
          />
        )}
      </div>

      <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)", textAlign: "center" }}>
        {graphData.nodes.length} facts · {graphData.links.length} relationships · Click a node to inspect
      </p>
    </div>
  );
}
