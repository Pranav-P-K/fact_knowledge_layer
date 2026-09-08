import { useState, useEffect, useCallback } from "react";
import { FileText, Brain, Link2, Plus, RefreshCw } from "lucide-react";
import UploadPanel from "../components/UploadPanel";
import FactsTable from "../components/FactsTable";
import FactDetail from "../components/FactDetail";
import KnowledgeGraph from "../components/KnowledgeGraph";
import RelationshipsPanel from "../components/RelationshipsPanel";
import { listDocuments, relationshipStats } from "../api";

export default function Dashboard() {
  const [tab, setTab] = useState("facts"); // "facts" | "graph" | "upload"
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ total: 0, SUPPORTS: 0, CONTRADICTS: 0, RECONCILES: 0 });
  const [selectedFactId, setSelectedFactId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(() => {
    listDocuments().then(setDocuments).catch(() => {});
    relationshipStats().then(setStats).catch(() => {});
    setRefreshKey((k) => k + 1);
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 8000); // auto-refresh every 8s while processing
    return () => clearInterval(interval);
  }, [refresh]);

  const totalFacts = documents.reduce((s, d) => s + (d.fact_count || 0), 0);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top nav */}
      <header style={{
        background: "var(--c-surface)",
        borderBottom: "1px solid var(--c-border)",
        padding: "0 24px",
        display: "flex",
        alignItems: "center",
        gap: 16,
        height: 58,
        position: "sticky",
        top: 0,
        zIndex: 30,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32,
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            borderRadius: 8,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Brain size={16} color="#fff" />
          </div>
          <span style={{ fontWeight: 800, fontSize: "1.05rem", letterSpacing: "-0.02em" }}>
            Fact Knowledge Layer
          </span>
        </div>

        <div className="tabs" style={{ marginLeft: "auto", flexWrap: "wrap" }}>
          <button className={`tab${tab === "facts" ? " active" : ""}`} onClick={() => setTab("facts")}>
            <FileText size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Facts
          </button>
          <button className={`tab${tab === "graph" ? " active" : ""}`} onClick={() => setTab("graph")}>
            <Link2 size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Graph
          </button>
          <button className={`tab${tab === "relationships" ? " active" : ""}`} onClick={() => setTab("relationships")}>
            <Link2 size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Relations
          </button>
          <button className={`tab${tab === "upload" ? " active" : ""}`} onClick={() => setTab("upload")}>
            <Plus size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Upload
          </button>
        </div>

        <button className="btn btn-ghost" style={{ padding: "6px 10px" }} onClick={refresh} data-tip="Refresh">
          <RefreshCw size={14} />
        </button>
      </header>

      {/* Stats bar */}
      <div style={{
        background: "var(--c-surface-2)",
        borderBottom: "1px solid var(--c-border)",
        padding: "12px 24px",
        display: "flex",
        gap: 12,
        flexWrap: "wrap",
      }}>
        <div className="stat-chip">
          <span className="value">{documents.length}</span>
          <span className="label">Documents</span>
        </div>
        <div className="stat-chip">
          <span className="value">{totalFacts}</span>
          <span className="label">Facts</span>
        </div>
        <div className="stat-chip">
          <span className="value" style={{ color: "var(--c-supports)" }}>{stats.SUPPORTS}</span>
          <span className="label">Corroborated</span>
        </div>
        <div className="stat-chip">
          <span className="value" style={{ color: "var(--c-contradicts)" }}>{stats.CONTRADICTS}</span>
          <span className="label">Contradicted</span>
        </div>
        <div className="stat-chip">
          <span className="value" style={{ color: "var(--c-reconciles)" }}>{stats.RECONCILES}</span>
          <span className="label">Reconciled</span>
        </div>

        {/* Processing badges */}
        {documents.filter((d) => d.status === "processing").map((d) => (
          <div key={d.id} style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 12px", background: "var(--c-accent-glow)", border: "1px solid var(--c-accent)", borderRadius: "var(--radius)", fontSize: "0.78rem" }}>
            <div className="pulse-dot" style={{ background: "var(--c-accent)" }} />
            Processing {d.filename}…
          </div>
        ))}
      </div>

      {/* Main content */}
      <main style={{ flex: 1, padding: "24px", maxWidth: 1300, margin: "0 auto", width: "100%" }}>
        {tab === "upload" && (
          <div style={{ maxWidth: 620, margin: "0 auto" }}>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Upload PDFs</h2>
            <UploadPanel onUploadComplete={() => { refresh(); setTab("facts"); }} />

            {/* Document list */}
            {documents.length > 0 && (
              <div style={{ marginTop: 24 }}>
                <h3 style={{ fontWeight: 600, marginBottom: 12, fontSize: "0.9rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Loaded Documents
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {documents.map((d) => (
                    <div key={d.id} className="glass" style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px" }}>
                      <FileText size={16} color="var(--c-accent)" />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.filename}</p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          {d.page_count} pages · {d.fact_count} facts
                        </p>
                      </div>
                      <span
                        className={`badge ${d.status === "done" ? "badge-SUPPORTS" : d.status === "failed" ? "badge-CONTRADICTS" : "badge-unknown"}`}
                        style={{ flexShrink: 0 }}
                      >
                        {d.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {tab === "facts" && (
          <div>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Extracted Facts</h2>
            <FactsTable
              documents={documents}
              onSelectFact={(f) => setSelectedFactId(f.id)}
              refreshKey={refreshKey}
            />
          </div>
        )}

        {tab === "relationships" && (
          <div>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Cross-Document Relationships</h2>
            <p style={{ color: "var(--c-text-muted)", marginBottom: 20, fontSize: "0.88rem" }}>
              Facts linked across documents — corroborated, contradicted, or reconciled by context.
            </p>
            <RelationshipsPanel onSelectFact={(id) => setSelectedFactId(id)} />
          </div>
        )}

        {tab === "graph" && (
          <div>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Knowledge Graph</h2>
            <KnowledgeGraph
              documents={documents}
              onSelectFact={(id) => setSelectedFactId(id)}
              refreshKey={refreshKey}
            />
          </div>
        )}
      </main>

      {/* Fact detail panel */}
      <FactDetail
        factId={selectedFactId}
        onClose={() => setSelectedFactId(null)}
        onSelectFact={(id) => setSelectedFactId(id)}
      />
    </div>
  );
}
