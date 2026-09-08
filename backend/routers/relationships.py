"""
routers/relationships.py — Relationship listing for the knowledge graph.

GET /relationships
  Query params:
    type      (str) — SUPPORTS | CONTRADICTS | RECONCILES
    doc_id    (int) — only relationships involving a specific document

GET /relationships/stats
  Returns counts by type.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

import database as db

router = APIRouter(prefix="/relationships", tags=["relationships"])


@router.get("")
def list_relationships(
    type: Optional[str] = None,
    doc_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    conn = db.get_connection()
    try:
        where_clauses = ["1=1"]
        params: list = []

        if type is not None:
            where_clauses.append("r.relationship_type = ?")
            params.append(type.upper())

        if doc_id is not None:
            where_clauses.append("(fa.document_id = ? OR fb.document_id = ?)")
            params.extend([doc_id, doc_id])

        where_sql = " AND ".join(where_clauses)

        rows = conn.execute(
            f"""
            SELECT
                r.id, r.relationship_type, r.explanation, r.confidence,
                r.fact_id_a, r.fact_id_b,
                fa.fact_text  AS fact_a_text,
                fa.fact_type  AS fact_a_type,
                fa.page_number AS fact_a_page,
                fa.evidence_quote AS fact_a_evidence,
                fa.document_id AS fact_a_doc_id,
                da.filename   AS fact_a_doc_name,
                fb.fact_text  AS fact_b_text,
                fb.fact_type  AS fact_b_type,
                fb.page_number AS fact_b_page,
                fb.evidence_quote AS fact_b_evidence,
                fb.document_id AS fact_b_doc_id,
                db2.filename  AS fact_b_doc_name
            FROM relationships r
            JOIN facts fa ON fa.id = r.fact_id_a
            JOIN facts fb ON fb.id = r.fact_id_b
            JOIN documents da ON da.id = fa.document_id
            JOIN documents db2 ON db2.id = fb.document_id
            WHERE {where_sql}
            ORDER BY r.confidence DESC
            """,
            params,
        ).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/stats")
def relationship_stats() -> Dict[str, Any]:
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """
            SELECT relationship_type, COUNT(*) AS count
            FROM relationships
            GROUP BY relationship_type
            """
        ).fetchall()
        counts = {r["relationship_type"]: r["count"] for r in rows}
        total = sum(counts.values())
        return {
            "total": total,
            "SUPPORTS": counts.get("SUPPORTS", 0),
            "CONTRADICTS": counts.get("CONTRADICTS", 0),
            "RECONCILES": counts.get("RECONCILES", 0),
        }
    finally:
        conn.close()
