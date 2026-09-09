import { useState, useEffect, useCallback } from "react";
import { Search, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import { listFacts, listFactTypes } from "../api";

const REL_COLORS = {
  SUPPORTS: "var(--c-supports)",
  CONTRADICTS: "var(--c-contradicts)",
  RECONCILES: "var(--c-reconciles)",
};

function truncate(str, n = 90) {
  return str && str.length > n ? str.slice(0, n) + "…" : str;
}

export default function FactsTable({ documents, onSelectFact, refreshKey }) {
  const [facts, setFacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [filterDoc, setFilterDoc] = useState("");
  const [filterType, setFilterType] = useState("");
  const [filterRel, setFilterRel] = useState("");
  const [factTypes, setFactTypes] = useState([]);

  useEffect(() => {
    listFactTypes().then(setFactTypes).catch(() => {});
  }, [refreshKey]);

  const fetchFacts = useCallback(async () => {
    setLoading(true);
    try {
      const hasRel =
        filterRel === "yes" ? true : filterRel === "no" ? false : undefined;
      const res = await listFacts({
        documentId: filterDoc ? Number(filterDoc) : undefined,
        factType: filterType || undefined,
        hasRelationship: hasRel,
        page,
        pageSize,
      });
      setFacts(res.items);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filterDoc, filterType, filterRel, page, pageSize, refreshKey]);

  useEffect(() => {
    fetchFacts();
  }, [fetchFacts]);

  // Client-side search filter
  const displayed = search
    ? facts.filter(
        (f) =>
          f.fact_text.toLowerCase().includes(search.toLowerCase()) ||
          f.fact_type.toLowerCase().includes(search.toLowerCase())
      )
    : facts;

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Filter bar */}
      <div className="facts-filter-bar" style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ position: "relative", flex: "1 1 200px" }}>
          <Search size={14} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--c-text-muted)" }} />
          <input
            className="field"
            style={{ paddingLeft: 32, width: "100%" }}
            placeholder="Search facts…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="field" style={{ flex: "1 1 120px" }} value={filterDoc} onChange={(e) => { setFilterDoc(e.target.value); setPage(1); }}>
          <option value="">All documents</option>
          {documents.map((d) => (
            <option key={d.id} value={d.id}>{d.filename}</option>
          ))}
        </select>
        <select className="field" style={{ flex: "1 1 100px" }} value={filterType} onChange={(e) => { setFilterType(e.target.value); setPage(1); }}>
          <option value="">All types</option>
          {factTypes.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <select className="field" style={{ flex: "1 1 100px" }} value={filterRel} onChange={(e) => { setFilterRel(e.target.value); setPage(1); }}>
          <option value="">All facts</option>
          <option value="yes">Has relationships</option>
          <option value="no">No relationships</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass" style={{ overflow: "hidden" }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Fact</th>
                <th>Type</th>
                <th>Document</th>
                <th>Page</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", padding: "32px", color: "var(--c-text-muted)" }}>
                    <div className="spinner" style={{ margin: "0 auto" }} />
                  </td>
                </tr>
              ) : displayed.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", padding: "32px", color: "var(--c-text-muted)" }}>
                    No facts found. Upload a PDF to get started.
                  </td>
                </tr>
              ) : (
                displayed.map((f) => (
                  <tr key={f.id} onClick={() => onSelectFact(f)} className="fade-in">
                    <td style={{ maxWidth: 340 }}>
                      <p style={{ fontWeight: 500, marginBottom: 2 }}>{truncate(f.fact_text)}</p>
                    </td>
                    <td>
                      <span className="badge badge-unknown">{f.fact_type}</span>
                    </td>
                    <td style={{ color: "var(--c-text-muted)", fontSize: "0.8rem" }}>
                      {f.filename}
                    </td>
                    <td style={{ color: "var(--c-text-muted)", fontSize: "0.8rem" }}>
                      p.{f.page_number}
                    </td>
                    <td style={{ maxWidth: 220 }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--c-text-muted)" }}>
                        {truncate(f.evidence_quote, 60)}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "10px 14px", borderTop: "1px solid var(--c-border)",
          }}>
            <span style={{ fontSize: "0.8rem", color: "var(--c-text-muted)" }}>
              {total} facts · page {page} of {totalPages}
            </span>
            <div style={{ display: "flex", gap: 6 }}>
              <button className="btn btn-ghost" style={{ padding: "4px 10px" }} disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                <ChevronLeft size={14} />
              </button>
              <button className="btn btn-ghost" style={{ padding: "4px 10px" }} disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
