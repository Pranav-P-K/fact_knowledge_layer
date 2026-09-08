import { useState, useCallback } from "react";
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from "lucide-react";
import { uploadDocument } from "../api";

const STATUS_COLORS = { done: "#22c55e", failed: "#ef4444", processing: "#6366f1" };

export default function UploadPanel({ onUploadComplete }) {
  const [dragging, setDragging] = useState(false);
  const [uploads, setUploads] = useState([]); // [{file, status, docId, error}]

  const processFile = useCallback(async (file) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Only PDF files are supported.");
      return;
    }

    const entry = { id: Date.now(), name: file.name, status: "uploading", docId: null, error: null };
    setUploads((u) => [entry, ...u]);

    try {
      const res = await uploadDocument(file);
      setUploads((u) =>
        u.map((x) => x.id === entry.id ? { ...x, status: "processing", docId: res.document_id } : x)
      );

      // Poll for completion
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const doc = await fetch(`http://localhost:8000/documents/${res.document_id}`).then((r) => r.json());
          if (doc.status === "done" || doc.status === "failed" || attempts > 120) {
            clearInterval(poll);
            setUploads((u) =>
              u.map((x) => x.id === entry.id ? { ...x, status: doc.status, docId: res.document_id } : x)
            );
            if (doc.status === "done") onUploadComplete?.();
          }
        } catch (_) {}
      }, 3000);
    } catch (err) {
      setUploads((u) =>
        u.map((x) => x.id === entry.id ? { ...x, status: "failed", error: err.message } : x)
      );
    }
  }, [onUploadComplete]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    Array.from(e.dataTransfer.files).forEach(processFile);
  }, [processFile]);

  const onFileInput = (e) => {
    Array.from(e.target.files).forEach(processFile);
    e.target.value = "";
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Drop zone */}
      <label
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 12,
          padding: "40px 24px",
          border: `2px dashed ${dragging ? "var(--c-accent)" : "var(--c-border)"}`,
          borderRadius: "var(--radius-lg)",
          background: dragging ? "var(--c-accent-glow)" : "var(--c-surface-2)",
          cursor: "pointer",
          transition: "all 0.2s",
        }}
      >
        <input type="file" accept=".pdf" multiple hidden onChange={onFileInput} />
        <div style={{
          width: 56, height: 56,
          background: "var(--c-accent-glow)",
          border: "1px solid var(--c-accent)",
          borderRadius: "50%",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <Upload size={24} color="var(--c-accent)" />
        </div>
        <div style={{ textAlign: "center" }}>
          <p style={{ fontWeight: 600, marginBottom: 4 }}>Drop PDFs here or click to browse</p>
          <p style={{ fontSize: "0.8rem", color: "var(--c-text-muted)" }}>
            Multiple files supported · Processed incrementally
          </p>
        </div>
      </label>

      {/* Upload history */}
      {uploads.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {uploads.map((u) => (
            <div key={u.id} className="glass fade-in" style={{
              display: "flex", alignItems: "center", gap: 12, padding: "12px 16px",
            }}>
              <FileText size={18} color="var(--c-text-muted)" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {u.name}
                </p>
                {u.error && (
                  <p style={{ fontSize: "0.75rem", color: "var(--c-contradicts)" }}>{u.error}</p>
                )}
              </div>
              {u.status === "uploading" && <div className="spinner" />}
              {u.status === "processing" && (
                <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--c-accent)", fontSize: "0.8rem" }}>
                  <div className="pulse-dot" style={{ background: "var(--c-accent)" }} />
                  Extracting facts…
                </div>
              )}
              {u.status === "done" && <CheckCircle size={18} color="var(--c-supports)" />}
              {u.status === "failed" && <AlertCircle size={18} color="var(--c-contradicts)" />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
