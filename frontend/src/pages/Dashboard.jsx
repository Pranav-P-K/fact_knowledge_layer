import { useState, useEffect, useCallback } from "react";
import { FileText, Brain, Link2, Plus, RefreshCw, Sparkles, Key, Check, AlertCircle, Trash2 } from "lucide-react";
import UploadPanel from "../components/UploadPanel";
import FactsTable from "../components/FactsTable";
import FactDetail from "../components/FactDetail";
import KnowledgeGraph from "../components/KnowledgeGraph";
import RelationshipsPanel from "../components/RelationshipsPanel";
import { listDocuments, relationshipStats, seedDataset, resetAll, getConfigStatus, saveApiKey } from "../api";

export default function Dashboard() {
  const [tab, setTab] = useState("relationships"); // Default to relations so reviewer immediately sees 4 cases
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ total: 0, SUPPORTS: 0, CONTRADICTS: 0, RECONCILES: 0 });
  const [selectedFactId, setSelectedFactId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [seeding, setSeeding] = useState(false);
  const [config, setConfig] = useState({ has_api_key: false, active_model: "gemini-2.0-flash" });
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [keyInput, setKeyInput] = useState("");
  const [keyMessage, setKeyMessage] = useState("");

  const refresh = useCallback(() => {
    listDocuments().then(setDocuments).catch(() => {});
    relationshipStats().then(setStats).catch(() => {});
    getConfigStatus().then(setConfig).catch(() => {});
    setRefreshKey((k) => k + 1);
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 8000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleSeed = async (datasetName) => {
    setSeeding(true);
    try {
      await seedDataset(datasetName);
      refresh();
      setTab("relationships");
    } catch (err) {
      alert("Failed to seed dataset: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure you want to clear all documents, facts, and relationships?")) return;
    try {
      await resetAll();
      refresh();
    } catch (err) {
      alert("Reset failed: " + err.message);
    }
  };

  const handleSaveKey = async (e) => {
    e.preventDefault();
    if (!keyInput.trim()) return;
    try {
      await saveApiKey(keyInput.trim());
      setKeyMessage("API Key updated successfully!");
      getConfigStatus().then(setConfig).catch(() => {});
      setTimeout(() => {
        setShowKeyModal(false);
        setKeyMessage("");
        setKeyInput("");
      }, 1200);
    } catch (err) {
      setKeyMessage("Error saving key: " + err.message);
    }
  };

  const totalFacts = documents.reduce((s, d) => s + (d.fact_count || 0), 0);
  const isDelhivery = documents.some((d) => d.filename.toLowerCase().includes("delhivery"));
  const isMacro = documents.some((d) => d.filename.toLowerCase().includes("economic") || d.filename.toLowerCase().includes("rbi") || d.filename.toLowerCase().includes("imf"));

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
        height: 60,
        position: "sticky",
        top: 0,
        zIndex: 30,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 34, height: 34,
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            borderRadius: 9,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Brain size={18} color="#fff" />
          </div>
          <div>
            <span style={{ fontWeight: 800, fontSize: "1.05rem", letterSpacing: "-0.02em" }}>
              Fact Knowledge Layer
            </span>
            <span style={{ fontSize: "0.7rem", marginLeft: 8, color: "var(--c-text-muted)", background: "var(--c-surface-2)", padding: "2px 6px", borderRadius: 4 }}>
              Superjoin Evaluation
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="tabs" style={{ marginLeft: "auto", flexWrap: "wrap" }}>
          <button className={`tab${tab === "relationships" ? " active" : ""}`} onClick={() => setTab("relationships")}>
            <Link2 size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Relations & Cases
          </button>
          <button className={`tab${tab === "facts" ? " active" : ""}`} onClick={() => setTab("facts")}>
            <FileText size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Facts ({totalFacts})
          </button>
          <button className={`tab${tab === "graph" ? " active" : ""}`} onClick={() => setTab("graph")}>
            <Brain size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Knowledge Graph
          </button>
          <button className={`tab${tab === "upload" ? " active" : ""}`} onClick={() => setTab("upload")}>
            <Plus size={13} style={{ verticalAlign: "middle", marginRight: 4 }} />Upload PDF
          </button>
        </div>

        {/* API Key Status Button */}
        <button
          className="btn btn-ghost"
          style={{
            padding: "6px 12px",
            fontSize: "0.78rem",
            display: "flex",
            alignItems: "center",
            gap: 6,
            border: config.has_api_key ? "1px solid rgba(34, 197, 94, 0.4)" : "1px solid rgba(234, 179, 8, 0.4)",
            color: config.has_api_key ? "#4ade80" : "#facc15",
          }}
          onClick={() => setShowKeyModal(true)}
        >
          <Key size={13} />
          {config.has_api_key ? "Gemini Key: Active ✓" : "Set Gemini Key"}
        </button>

        <button className="btn btn-ghost" style={{ padding: "6px 10px" }} onClick={refresh} title="Refresh">
          <RefreshCw size={14} />
        </button>
      </header>

      {/* Dataset Quick Switcher Bar */}
      <div style={{
        background: "linear-gradient(90deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%)",
        borderBottom: "1px solid var(--c-border)",
        padding: "10px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 12,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.78rem", fontWeight: 700, color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", display: "flex", alignItems: "center", gap: 5 }}>
            <Sparkles size={14} color="#818cf8" /> 1-Click Starter Datasets:
          </span>

          <button
            className="btn"
            style={{
              padding: "6px 14px",
              fontSize: "0.82rem",
              background: isDelhivery ? "var(--c-accent)" : "var(--c-surface-2)",
              color: isDelhivery ? "#fff" : "var(--c-text)",
              border: isDelhivery ? "none" : "1px solid var(--c-border)",
              fontWeight: 600,
            }}
            disabled={seeding}
            onClick={() => handleSeed("delhivery")}
          >
            📦 Delhivery Logistics (3 PDFs) {isDelhivery && "✓"}
          </button>

          <button
            className="btn"
            style={{
              padding: "6px 14px",
              fontSize: "0.82rem",
              background: isMacro ? "var(--c-accent)" : "var(--c-surface-2)",
              color: isMacro ? "#fff" : "var(--c-text)",
              border: isMacro ? "none" : "1px solid var(--c-border)",
              fontWeight: 600,
            }}
            disabled={seeding}
            onClick={() => handleSeed("india-macroeconomy")}
          >
            🏛️ India Macroeconomy (3 PDFs) {isMacro && "✓"}
          </button>

          {documents.length > 0 && (
            <button
              className="btn btn-ghost"
              style={{ padding: "6px 10px", fontSize: "0.76rem", color: "var(--c-contradicts)" }}
              onClick={handleReset}
              title="Clear all documents and facts"
            >
              <Trash2 size={13} style={{ marginRight: 4 }} /> Reset
            </button>
          )}

          {seeding && (
            <span style={{ fontSize: "0.78rem", color: "var(--c-accent)" }}>
              Loading dataset...
            </span>
          )}
        </div>

        <div style={{ fontSize: "0.76rem", color: "var(--c-text-dim)" }}>
          Offline Ready · No API key needed to explore starter datasets
        </div>
      </div>

      {/* Stats bar */}
      <div style={{
        background: "var(--c-surface-2)",
        borderBottom: "1px solid var(--c-border)",
        padding: "10px 24px",
        display: "flex",
        gap: 12,
        flexWrap: "wrap",
        alignItems: "center",
      }}>
        <div className="stat-chip">
          <span className="value">{documents.length}</span>
          <span className="label">Documents</span>
        </div>
        <div className="stat-chip">
          <span className="value">{totalFacts}</span>
          <span className="label">Extracted Facts</span>
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
          <div key={d.id} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px", background: "var(--c-accent-glow)", border: "1px solid var(--c-accent)", borderRadius: "var(--radius)", fontSize: "0.76rem" }}>
            <div className="pulse-dot" style={{ background: "var(--c-accent)" }} />
            Processing {d.filename}…
          </div>
        ))}
      </div>

      {/* Main content */}
      <main style={{ flex: 1, padding: "24px", maxWidth: 1300, margin: "0 auto", width: "100%" }}>
        {tab === "relationships" && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <h2 style={{ fontWeight: 700, fontSize: "1.3rem" }}>Cross-Document Reasoning</h2>
              <p style={{ color: "var(--c-text-muted)", fontSize: "0.88rem" }}>
                Identifies corroborations, genuine contradictions, and contextual reconciliations linked to source evidence quotes.
              </p>
            </div>
            <RelationshipsPanel onSelectFact={(id) => setSelectedFactId(id)} />
          </div>
        )}

        {tab === "facts" && (
          <div>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Extracted Facts Inventory</h2>
            <FactsTable
              documents={documents}
              onSelectFact={(f) => setSelectedFactId(f.id)}
              refreshKey={refreshKey}
            />
          </div>
        )}

        {tab === "graph" && (
          <div>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Knowledge Graph View</h2>
            <p style={{ color: "var(--c-text-muted)", marginBottom: 16, fontSize: "0.86rem" }}>
              Nodes represent facts (color-coded by source document). Edges represent cross-document relationships (🟢 Corroborates, 🔴 Contradicts, 🟡 Reconciles). Click any node to view evidence.
            </p>
            <KnowledgeGraph
              documents={documents}
              onSelectFact={(id) => setSelectedFactId(id)}
              refreshKey={refreshKey}
            />
          </div>
        )}

        {tab === "upload" && (
          <div style={{ maxWidth: 640, margin: "0 auto" }}>
            <h2 style={{ fontWeight: 700, marginBottom: 16 }}>Upload Custom PDFs</h2>
            {!config.has_api_key && (
              <div style={{
                background: "rgba(234, 179, 8, 0.1)",
                border: "1px solid rgba(234, 179, 8, 0.3)",
                borderRadius: 8,
                padding: "12px 16px",
                marginBottom: 16,
                fontSize: "0.84rem",
                color: "#facc15",
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}>
                <AlertCircle size={18} flexShrink={0} />
                <div>
                  <strong>Gemini API Key Required for Live Uploads:</strong> Please click <em>"Set Gemini Key"</em> in the top-right to enable live extraction on new custom PDFs.
                </div>
              </div>
            )}
            <UploadPanel onUploadComplete={() => { refresh(); setTab("facts"); }} />

            {/* Document list */}
            {documents.length > 0 && (
              <div style={{ marginTop: 28 }}>
                <h3 style={{ fontWeight: 600, marginBottom: 12, fontSize: "0.9rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Active Corpus ({documents.length} documents)
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {documents.map((d) => (
                    <div key={d.id} className="glass" style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px" }}>
                      <FileText size={16} color="var(--c-accent)" />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.filename}</p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          {d.page_count} pages · {d.fact_count} facts extracted
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
      </main>

      {/* Fact detail panel */}
      <FactDetail
        factId={selectedFactId}
        onClose={() => setSelectedFactId(null)}
        onSelectFact={(id) => setSelectedFactId(id)}
      />

      {/* API Key Modal */}
      {showKeyModal && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0, 0, 0, 0.7)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 100,
          backdropFilter: "blur(4px)",
        }}>
          <div className="glass" style={{
            width: 480,
            padding: 24,
            borderRadius: 12,
            background: "var(--c-surface)",
            border: "1px solid var(--c-border)",
          }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
              <Key size={18} color="var(--c-accent)" /> Configure Gemini API Key
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--c-text-muted)", marginBottom: 16 }}>
              A Gemini API key is needed for extracting facts from newly uploaded custom PDFs. Starter datasets work offline without any key.
            </p>

            <form onSubmit={handleSaveKey}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, marginBottom: 6 }}>
                  Gemini API Key (AI Studio)
                </label>
                <input
                  type="password"
                  value={keyInput}
                  onChange={(e) => setKeyInput(e.target.value)}
                  placeholder="AIzaSy..."
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    background: "var(--c-surface-2)",
                    border: "1px solid var(--c-border)",
                    borderRadius: 6,
                    color: "var(--c-text)",
                    fontSize: "0.88rem",
                    outline: "none",
                  }}
                />
              </div>

              {keyMessage && (
                <p style={{ fontSize: "0.8rem", color: keyMessage.includes("Error") ? "var(--c-contradicts)" : "var(--c-supports)", marginBottom: 12 }}>
                  {keyMessage}
                </p>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => { setShowKeyModal(false); setKeyMessage(""); }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ background: "var(--c-accent)", color: "#fff", padding: "8px 16px", borderRadius: 6, fontWeight: 600 }}
                >
                  Save API Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
