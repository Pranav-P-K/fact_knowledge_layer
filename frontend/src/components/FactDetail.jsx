import { useState, useEffect } from "react";
import { X, FileText, Quote, Tag, Link2 } from "lucide-react";
import { getFact } from "../api";

const REL_LABELS = {
  SUPPORTS: { emoji: "🟢", label: "Supports" },
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
          background: "rgba(0,0,0,0.5)",
          backdropFilter: "blur(4px)",
          zIndex: 40,
        }}
      />
      {/* Panel */}
      <div
        className="fade-in"
        style={{
          position: "fixed", top: 0, right: 0, bottom: 0,
          width: "min(540px, 100vw)",
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
          <span style={{ fontWeight: 700, fontSize: "1rem" }}>Fact Detail</span>
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
          <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Fact text */}
            <div>
              <p style={{ fontSize: "1.05rem", fontWeight: 600, lineHeight: 1.5 }}>{fact.fact_text}</p>
              <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap", alignItems: "center" }}>
                <span className="badge badge-unknown"><Tag size={10} />{fact.fact_type}</span>
                <span style={{ fontSize: "0.78rem", color: "var(--c-text-muted)" }}>
                  <FileText size={10} style={{ verticalAlign: "middle", marginRight: 3 }} />
                  {fact.filename} · p.{fact.page_number}
                </span>
              </div>
            </div>

            {/* Evidence quote */}
            {fact.evidence_quote && (
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>
                  Source Evidence
                </p>
                <div className="evidence-quote">"{fact.evidence_quote}"</div>
              </div>
            )}

            {/* Attributes */}
            {fact.attributes && Object.keys(fact.attributes).length > 0 && (
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
                  Attributes
                </p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                  {Object.entries(fact.attributes).map(([k, v]) => (
                    <div key={k} style={{
                      background: "var(--c-surface-2)", borderRadius: "var(--radius-sm)",
                      padding: "6px 10px", border: "1px solid var(--c-border)",
                    }}>
                      <p style={{ fontSize: "0.65rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{k}</p>
                      <p style={{ fontSize: "0.85rem", fontWeight: 600 }}>{String(v)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relationships */}
            {fact.relationships && fact.relationships.length > 0 && (
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
                  Relationships ({fact.relationships.length})
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
                          transition: "border-color 0.15s",
                        }}
                        onClick={() => onSelectFact(other.id)}
                        onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--c-accent)"}
                        onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--c-border)"}
                      >
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                          <span className={`badge badge-${r.relationship_type}`}>
                            {meta.emoji} {meta.label}
                          </span>
                          <span style={{ fontSize: "0.72rem", color: "var(--c-text-muted)" }}>
                            conf. {(r.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p style={{ fontSize: "0.83rem", marginBottom: 6 }}>{other.text}</p>
                        <p style={{ fontSize: "0.72rem", color: "var(--c-text-muted)" }}>
                          <FileText size={10} style={{ verticalAlign: "middle", marginRight: 3 }} />
                          {other.doc}
                        </p>
                        {r.explanation && (
                          <p style={{
                            fontSize: "0.78rem", color: "var(--c-text-muted)",
                            marginTop: 8, paddingTop: 8,
                            borderTop: "1px solid var(--c-border)",
                            fontStyle: "italic",
                          }}>
                            💡 {r.explanation}
                          </p>
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
