import { useState, useEffect } from "react";
import { listRelationships } from "../api";

const TYPE_META = {
  SUPPORTS:    { emoji: "🟢", label: "Corroborated", desc: "Both documents agree on this fact" },
  CONTRADICTS: { emoji: "🔴", label: "Contradicted",  desc: "Documents make incompatible claims" },
  RECONCILES:  { emoji: "🟡", label: "Reconciled",   desc: "Apparent conflict explained by context" },
};

export default function RelationshipsPanel({ onSelectFact }) {
  const [rels, setRels] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    listRelationships({ type: filter || undefined })
      .then(setRels)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filter]);

  const groups = {
    SUPPORTS:    rels.filter((r) => r.relationship_type === "SUPPORTS"),
    CONTRADICTS: rels.filter((r) => r.relationship_type === "CONTRADICTS"),
    RECONCILES:  rels.filter((r) => r.relationship_type === "RECONCILES"),
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Filter tabs */}
      <div className="tabs" style={{ width: "fit-content" }}>
        {["", "SUPPORTS", "CONTRADICTS", "RECONCILES"].map((t) => (
          <button key={t} className={`tab${filter === t ? " active" : ""}`} onClick={() => setFilter(t)}>
            {t ? `${TYPE_META[t].emoji} ${TYPE_META[t].label}` : "All"}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="spinner" />
      ) : rels.length === 0 ? (
        <p style={{ color: "var(--c-text-muted)" }}>No relationships found yet. Upload multiple PDFs.</p>
      ) : (
        Object.entries(groups)
          .filter(([, items]) => items.length > 0 && (filter === "" || filter === items[0]?.relationship_type))
          .map(([type, items]) => (
            <section key={type}>
              <h3 style={{ fontWeight: 700, marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                {TYPE_META[type].emoji} {TYPE_META[type].label}
                <span style={{ fontSize: "0.75rem", color: "var(--c-text-muted)", fontWeight: 400 }}>
                  — {TYPE_META[type].desc}
                </span>
                <span className={`badge badge-${type}`} style={{ marginLeft: "auto" }}>{items.length}</span>
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {items.map((r) => (
                  <div key={r.id} className="glass fade-in" style={{ padding: "16px 18px" }}>
                    {/* Fact A */}
                    <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
                      <div style={{ flexShrink: 0, width: 3, borderRadius: 2, background: "var(--c-accent)" }} />
                      <div>
                        <p style={{ fontWeight: 600, marginBottom: 4, cursor: "pointer" }} onClick={() => onSelectFact?.(r.fact_id_a)}>
                          {r.fact_a_text}
                        </p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          📄 {r.fact_a_doc_name} · p.{r.fact_a_page}
                        </p>
                        {r.fact_a_evidence && (
                          <div className="evidence-quote" style={{ marginTop: 6 }}>"{r.fact_a_evidence}"</div>
                        )}
                      </div>
                    </div>

                    {/* Connector */}
                    <div style={{ display: "flex", alignItems: "center", gap: 8, margin: "8px 0 8px 15px" }}>
                      <div style={{ height: 1, flex: 1, background: "var(--c-border)" }} />
                      <span className={`badge badge-${type}`}>{TYPE_META[type].emoji} {type}</span>
                      <div style={{ height: 1, flex: 1, background: "var(--c-border)" }} />
                    </div>

                    {/* Fact B */}
                    <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
                      <div style={{ flexShrink: 0, width: 3, borderRadius: 2, background: "#06b6d4" }} />
                      <div>
                        <p style={{ fontWeight: 600, marginBottom: 4, cursor: "pointer" }} onClick={() => onSelectFact?.(r.fact_id_b)}>
                          {r.fact_b_text}
                        </p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          📄 {r.fact_b_doc_name} · p.{r.fact_b_page}
                        </p>
                        {r.fact_b_evidence && (
                          <div className="evidence-quote" style={{ marginTop: 6 }}>"{r.fact_b_evidence}"</div>
                        )}
                      </div>
                    </div>

                    {/* Explanation */}
                    {r.explanation && (
                      <div style={{
                        marginTop: 10, padding: "10px 14px",
                        background: "var(--c-surface-2)",
                        borderRadius: "var(--radius-sm)",
                        borderLeft: `3px solid ${type === "SUPPORTS" ? "var(--c-supports)" : type === "CONTRADICTS" ? "var(--c-contradicts)" : "var(--c-reconciles)"}`,
                        fontSize: "0.82rem",
                        color: "var(--c-text-muted)",
                        fontStyle: "italic",
                      }}>
                        💡 {r.explanation}
                      </div>
                    )}

                    <p style={{ fontSize: "0.7rem", color: "var(--c-text-dim)", marginTop: 8, textAlign: "right" }}>
                      Confidence: {(r.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                ))}
              </div>
            </section>
          ))
      )}
    </div>
  );
}
