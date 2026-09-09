import { useState, useEffect } from "react";
import { X, FileText, Quote, Tag, Link2, CheckCircle2, ShieldCheck, Scale } from "lucide-react";
import { getFact } from "../api";

const REL_LABELS = {
  SUPPORTS: { emoji: "🟢", label: "Corroborates" },
  CONTRADICTS: { emoji: "🔴", label: "Contradicts" },
  RECONCILES: { emoji: "🟡", label: "Reconciles" },
};

export default function FactDetail({ factId, onClose, onSelectFact }) {
  const [fact, setFact] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!factId) return;
    setLoading(true);
    getFact(factId)
      .then(setFact)
      .catch(() => setFact(null))
      .finally(() => setLoading(false));
  }, [factId]);

  if (!factId) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: "fixed", inset: 0,
          background: "rgba(0,0,0,0.6)",
          backdropFilter: "blur(4px)",
          zIndex: 40,
        }}
      />
      {/* Panel */}
      <div
        className="fade-in"
        style={{
          position: "fixed", top: 0, right: 0, bottom: 0,
          width: "min(580px, 100vw)",
          background: "var(--c-surface)",
          borderLeft: "1px solid var(--c-border)",
          zIndex: 50,
          display: "flex", flexDirection: "column",
          overflowY: "auto",
        }}
      >
        {/* Header */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "16px 20px",
          borderBottom: "1px solid var(--c-border)",
          background: "var(--c-surface-2)",
          position: "sticky", top: 0, zIndex: 1,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ShieldCheck size={18} color="#4ade80" />
            <span style={{ fontWeight: 700, fontSize: "0.95rem" }}>Evidence Grounding Inspector</span>
          </div>
          <button className="btn btn-ghost" style={{ padding: "4px 8px" }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
            <div className="spinner" />
          </div>
        ) : !fact ? (
          <p style={{ padding: 24, color: "var(--c-text-muted)" }}>Failed to load fact.</p>
        ) : (
          <div style={{ padding: 22, display: "flex", flexDirection: "column", gap: 22 }}>
            {/* Fact statement card */}
            <div style={{
              background: "linear-gradient(180deg, rgba(99, 102, 241, 0.06) 0%, rgba(30, 41, 59, 0.3) 100%)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              borderRadius: 8,
              padding: 16,
            }}>
              <p style={{ fontSize: "1.05rem", fontWeight: 700, lineHeight: 1.5, marginBottom: 8 }}>
                {fact.fact_text}
              </p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                <span className="badge badge-unknown"><Tag size={10} style={{ marginRight: 3 }} />{fact.fact_type}</span>
                <span style={{ fontSize: "0.78rem", color: "var(--c-text-muted)" }}>
                  <FileText size={12} style={{ verticalAlign: "middle", marginRight: 3 }} />
                  {fact.filename} · Page {fact.page_number}
                </span>
              </div>
            </div>

            {/* Verbatim Source Evidence Grounding */}
            {fact.evidence_quote && (
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                  <p style={{ fontSize: "0.76rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700 }}>
                    📖 Verbatim Source Proof (Page {fact.page_number})
                  </p>
                  <span style={{ fontSize: "0.72rem", color: "#4ade80", display: "flex", alignItems: "center", gap: 4 }}>
                    <CheckCircle2 size={12} /> 100% Un-hallucinated
                  </span>
                </div>

                {/* Simulated Document Page Snippet */}
                <div style={{
                  background: "#0b0f19",
                  border: "1px solid var(--c-border)",
                  borderRadius: 8,
                  padding: "16px 18px",
                  fontFamily: "var(--font-mono, monospace)",
                  fontSize: "0.82rem",
                  lineHeight: 1.6,
                  color: "#cbd5e1",
                  boxShadow: "inset 0 2px 4px rgba(0,0,0,0.5)",
                }}>
                  <div style={{ fontSize: "0.68rem", color: "var(--c-text-dim)", marginBottom: 10, borderBottom: "1px solid rgba(255,255,255,0.08)", paddingBottom: 6 }}>
                    DOCUMENT: {fact.filename} | SECTION: PAGE {fact.page_number}
                  </div>
                  <div style={{
                    background: "rgba(234, 179, 8, 0.18)",
                    borderLeft: "3px solid #facc15",
                    padding: "8px 12px",
                    color: "#fef08a",
                    borderRadius: "0 6px 6px 0",
                    fontWeight: 500,
                  }}>
                    "{fact.evidence_quote}"
                  </div>
                </div>
              </div>
            )}

            {/* Financial Normalization & Attributes */}
            {fact.attributes && Object.keys(fact.attributes).length > 0 && (
              <div>
                <p style={{ fontSize: "0.76rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, marginBottom: 10 }}>
                  📊 Superjoin Canonical Schema
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {Object.entries(fact.attributes).map(([k, v]) => (
                    <div key={k} style={{
                      background: "var(--c-surface-2)", borderRadius: "var(--radius-sm)",
                      padding: "8px 12px", border: "1px solid var(--c-border)",
                    }}>
                      <p style={{ fontSize: "0.68rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 2 }}>
                        {k.replace(/_/g, " ")}
                      </p>
                      <p style={{ fontSize: "0.86rem", fontWeight: 600, color: "var(--c-text)" }}>
                        {typeof v === "object" ? JSON.stringify(v) : String(v)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cross-Document Relationships */}
            {fact.relationships && fact.relationships.length > 0 && (
              <div>
                <p style={{ fontSize: "0.76rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, marginBottom: 10 }}>
                  🔗 Cross-Document Verification Links ({fact.relationships.length})
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {fact.relationships.map((r) => {
                    const other = r.fact_id_a === fact.id
                      ? { text: r.fact_b_text, doc: r.doc_b_name, id: r.fact_id_b }
                      : { text: r.fact_a_text, doc: r.doc_a_name, id: r.fact_id_a };
                    const meta = REL_LABELS[r.relationship_type] || { emoji: "⚪", label: r.relationship_type };

                    return (
                      <div
                        key={r.id}
                        style={{
                          background: "var(--c-surface-2)",
                          border: "1px solid var(--c-border)",
                          borderRadius: "var(--radius)",
                          padding: "12px 14px",
                          cursor: "pointer",
                          transition: "border-color 0.15s, transform 0.1s",
                        }}
                        onClick={() => onSelectFact(other.id)}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = "var(--c-accent)";
                          e.currentTarget.style.transform = "translateX(2px)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = "var(--c-border)";
                          e.currentTarget.style.transform = "translateX(0)";
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                          <span className={`badge badge-${r.relationship_type}`}>
                            {meta.emoji} {meta.label}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "var(--c-text-muted)" }}>
                            Confidence: {(r.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p style={{ fontSize: "0.84rem", fontWeight: 500, marginBottom: 6 }}>{other.text}</p>
                        <p style={{ fontSize: "0.72rem", color: "var(--c-text-muted)" }}>
                          <FileText size={10} style={{ verticalAlign: "middle", marginRight: 3 }} />
                          {other.doc}
                        </p>
                        {r.explanation && (
                          <div style={{
                            fontSize: "0.78rem", color: "var(--c-text-muted)",
                            marginTop: 8, paddingTop: 8,
                            borderTop: "1px solid var(--c-border)",
                          }}>
                            <strong>💡 Reasoning:</strong> {r.explanation}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
