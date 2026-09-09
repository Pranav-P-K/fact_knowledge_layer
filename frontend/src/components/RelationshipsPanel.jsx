import { useState, useEffect } from "react";
import { CheckCircle2, AlertTriangle, Scale, HelpCircle } from "lucide-react";
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
  const [activeCaseTab, setActiveCaseTab] = useState("all");

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
    <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
      {/* ── Assignment Case Studies Showcase ── */}
      <section className="glass" style={{
        padding: "20px 24px",
        background: "linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, rgba(15, 23, 42, 0.4) 100%)",
        border: "1px solid rgba(99, 102, 241, 0.25)",
        borderRadius: "var(--radius-lg, 12px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: 8 }}>
              🎯 Superjoin Evaluation: Four Core Cases Showcase
            </h3>
            <p style={{ fontSize: "0.82rem", color: "var(--c-text-muted)", marginTop: 2 }}>
              How the Fact Knowledge Layer identifies corroborations, genuine contradictions, contextual reconciliations, and extraction failures.
            </p>
          </div>
          <div className="showcase-badges">
            <span className="badge" style={{ background: "rgba(34, 197, 94, 0.15)", color: "#4ade80", border: "1px solid rgba(34, 197, 94, 0.3)" }}>1. Corroboration</span>
            <span className="badge" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#f87171", border: "1px solid rgba(239, 68, 68, 0.3)" }}>2. Contradiction</span>
            <span className="badge" style={{ background: "rgba(234, 179, 8, 0.15)", color: "#facc15", border: "1px solid rgba(234, 179, 8, 0.3)" }}>3. Reconciliation</span>
            <span className="badge" style={{ background: "rgba(168, 85, 247, 0.15)", color: "#c084fc", border: "1px solid rgba(168, 85, 247, 0.3)" }}>4. Extraction Failure</span>
          </div>
        </div>

        <div className="case-studies-grid">
          {/* Card 1: Corroboration */}
          <div style={{ background: "var(--c-surface)", padding: 14, borderRadius: 8, border: "1px solid rgba(34, 197, 94, 0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "#4ade80", fontWeight: 700, fontSize: "0.88rem" }}>
              <CheckCircle2 size={16} /> Case 1: Corroboration
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--c-text)", marginBottom: 8 }}>
              <strong>Metric Alignment:</strong> Delhivery FY24 Revenue is reported at ₹8,142 Cr in both the <em>Annual Report</em> and <em>Q4 Earnings Deck</em>.
            </p>
            <div style={{ fontSize: "0.74rem", background: "var(--c-surface-2)", padding: 8, borderRadius: 6, color: "var(--c-text-muted)" }}>
              Identical numbers confirmed across independent audited and quarterly filings.
            </div>
          </div>

          {/* Card 2: Contradiction */}
          <div style={{ background: "var(--c-surface)", padding: 14, borderRadius: 8, border: "1px solid rgba(239, 68, 68, 0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "#f87171", fontWeight: 700, fontSize: "0.88rem" }}>
              <AlertTriangle size={16} /> Case 2: Genuine Contradiction
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--c-text)", marginBottom: 8 }}>
              <strong>Metric Divergence:</strong> Annual Report reports statutory Ind AS EBITDA margin of <strong>2.2%</strong>, contradicting Earnings Deck's claimed <strong>4.1%</strong> Adjusted EBITDA.
            </p>
            <div style={{ fontSize: "0.74rem", background: "var(--c-surface-2)", padding: 8, borderRadius: 6, color: "var(--c-text-muted)" }}>
              Flagged as contradictory due to GAAP statutory vs non-GAAP Adjusted EBITDA divergence.
            </div>
          </div>

          {/* Card 3: Reconciliation */}
          <div style={{ background: "var(--c-surface)", padding: 14, borderRadius: 8, border: "1px solid rgba(234, 179, 8, 0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "#facc15", fontWeight: 700, fontSize: "0.88rem" }}>
              <Scale size={16} /> Case 3: Reconciliation by Context
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--c-text)", marginBottom: 8 }}>
              <strong>Temporal Scale:</strong> 2022 Prospectus reported ₹3,646.5 Cr revenue vs FY24 Annual Report ₹8,142 Cr.
            </p>
            <div style={{ fontSize: "0.74rem", background: "var(--c-surface-2)", padding: 8, borderRadius: 6, color: "var(--c-text-muted)" }}>
              Reconciled by multi-year organic growth + Spoton acquisition over the 3-year timeline.
            </div>
          </div>

          {/* Card 4: Extraction Failure */}
          <div style={{ background: "var(--c-surface)", padding: 14, borderRadius: 8, border: "1px solid rgba(168, 85, 247, 0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, color: "#c084fc", fontWeight: 700, fontSize: "0.88rem" }}>
              <HelpCircle size={16} /> Case 4: Extraction Failure
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--c-text)", marginBottom: 8 }}>
              <strong>Unsegmented Slide:</strong> Page 11 of Q4 Earnings extracts <code>63% 66% 59% 1,860 2,076</code> without table row headers.
            </p>
            <div style={{ fontSize: "0.74rem", background: "var(--c-surface-2)", padding: 8, borderRadius: 6, color: "var(--c-text-muted)" }}>
              Identified as table parsing artifact; captured with failure flags for fallback review.
            </div>
          </div>
        </div>
      </section>

      {/* ── Filter Tabs ── */}
      <div className="filter-tabs-bar" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <div className="tabs" style={{ width: "fit-content" }}>
          {["", "SUPPORTS", "CONTRADICTS", "RECONCILES"].map((t) => (
            <button key={t} className={`tab${filter === t ? " active" : ""}`} onClick={() => setFilter(t)}>
              {t ? `${TYPE_META[t].emoji} ${TYPE_META[t].label}` : "All"}
            </button>
          ))}
        </div>
        <span style={{ fontSize: "0.8rem", color: "var(--c-text-muted)" }}>
          Showing {rels.length} relationships
        </span>
      </div>

      {loading ? (
        <div className="spinner" />
      ) : rels.length === 0 ? (
        <p style={{ color: "var(--c-text-muted)" }}>No relationships found yet. Click one of the starter dataset buttons above to load.</p>
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
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {items.map((r) => (
                  <div key={r.id} className="glass fade-in" style={{ padding: "16px 18px", borderLeft: `4px solid ${type === "SUPPORTS" ? "var(--c-supports)" : type === "CONTRADICTS" ? "var(--c-contradicts)" : "var(--c-reconciles)"}` }}>
                    {/* Fact A */}
                    <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
                      <div style={{ flexShrink: 0, width: 3, borderRadius: 2, background: "var(--c-accent)" }} />
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, marginBottom: 4, cursor: "pointer" }} onClick={() => onSelectFact?.(r.fact_id_a)}>
                          {r.fact_a_text}
                        </p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          📄 {r.fact_a_doc_name} · Page {r.fact_a_page}
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
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, marginBottom: 4, cursor: "pointer" }} onClick={() => onSelectFact?.(r.fact_id_b)}>
                          {r.fact_b_text}
                        </p>
                        <p style={{ fontSize: "0.75rem", color: "var(--c-text-muted)" }}>
                          📄 {r.fact_b_doc_name} · Page {r.fact_b_page}
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
                        fontSize: "0.82rem",
                        color: "var(--c-text)",
                      }}>
                        <strong>💡 Analytical Reasoning:</strong> {r.explanation}
                      </div>
                    )}

                    <p style={{ fontSize: "0.7rem", color: "var(--c-text-dim)", marginTop: 8, textAlign: "right" }}>
                      Confidence Score: {(r.confidence * 100).toFixed(0)}%
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
