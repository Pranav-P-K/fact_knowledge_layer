/**
 * api.js — Centralised API client for the Fact Knowledge Layer backend.
 */

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

// ── Documents & Seeding ──────────────────────────────────────────────────────

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/documents/upload", { method: "POST", body: form });
}

export async function seedDataset(dataset = "delhivery") {
  return request("/documents/seed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset }),
  });
}

export async function resetAll() {
  return request("/documents/reset", { method: "DELETE" });
}

export async function listDocuments() {
  return request("/documents");
}

export async function getDocument(id) {
  return request(`/documents/${id}`);
}

// ── Facts ─────────────────────────────────────────────────────────────────────

export async function listFacts({ documentId, factType, hasRelationship, page = 1, pageSize = 50 } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (documentId != null) params.set("document_id", documentId);
  if (factType) params.set("fact_type", factType);
  if (hasRelationship != null) params.set("has_relationship", hasRelationship);
  return request(`/facts?${params}`);
}

export async function getFact(id) {
  return request(`/facts/${id}`);
}

export async function listFactTypes() {
  return request("/facts/types");
}

// ── Relationships ─────────────────────────────────────────────────────────────

export async function listRelationships({ type, docId } = {}) {
  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (docId != null) params.set("doc_id", docId);
  return request(`/relationships?${params}`);
}

export async function relationshipStats() {
  return request("/relationships/stats");
}

// ── Configuration ─────────────────────────────────────────────────────────────

export async function getConfigStatus() {
  return request("/config/status");
}

export async function saveApiKey(key) {
  return request("/config/key", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key }),
  });
}
