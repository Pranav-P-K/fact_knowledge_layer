"""
routers/facts.py — Fact listing and detail endpoints.

GET /facts
  Query params:
    document_id   (int)   — filter by document
    fact_type     (str)   — filter by type
    has_relationship (bool) — only facts that appear in at least one relationship
    page          (int)   — pagination (default 1)
    page_size     (int)   — items per page (default 50, max 200)

GET /facts/{fact_id}
  Returns a single fact with all its relationships and the related facts.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

import database as db

router = APIRouter(prefix="/facts", tags=["facts"])


@router.get("")
def list_facts(
    document_id: Optional[int] = None,
    fact_type: Optional[str] = None,
    has_relationship: Optional[bool] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> Dict[str, Any]:
    conn = db.get_connection()
    try:
        where_clauses = ["1=1"]
        params: list = []

        if document_id is not None:
            where_clauses.append("f.document_id = ?")
            params.append(document_id)

        if fact_type is not None:
            where_clauses.append("f.fact_type = ?")
            params.append(fact_type.lower())

        if has_relationship is True:
            where_clauses.append(
                "(EXISTS (SELECT 1 FROM relationships r WHERE r.fact_id_a = f.id OR r.fact_id_b = f.id))"
            )
        elif has_relationship is False:
            where_clauses.append(
                "(NOT EXISTS (SELECT 1 FROM relationships r WHERE r.fact_id_a = f.id OR r.fact_id_b = f.id))"
            )

        where_sql = " AND ".join(where_clauses)
        offset = (page - 1) * page_size

        total = conn.execute(
            f"SELECT COUNT(*) FROM facts f WHERE {where_sql}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"""
            SELECT f.id, f.document_id, d.filename, f.fact_text, f.fact_type,
                   f.attributes, f.evidence_quote, f.page_number, f.created_at
            FROM facts f
            JOIN documents d ON d.id = f.document_id
            WHERE {where_sql}
            ORDER BY f.id DESC
            LIMIT ? OFFSET ?
            """,
            params + [page_size, offset],
        ).fetchall()

        items = []
        for r in rows:
            item = dict(r)
            item["attributes"] = json.loads(item["attributes"] or "{}")
            items.append(item)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }
    finally:
        conn.close()


@router.get("/types")
def list_fact_types() -> List[str]:
    """Return distinct fact types present in the database (for filter dropdowns)."""
    conn = db.get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT fact_type FROM facts ORDER BY fact_type"
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


@router.get("/{fact_id}")
def get_fact(fact_id: int) -> Dict[str, Any]:
    conn = db.get_connection()
    try:
        row = conn.execute(
            """
            SELECT f.id, f.document_id, d.filename, f.fact_text, f.fact_type,
                   f.attributes, f.evidence_quote, f.page_number, f.created_at
            FROM facts f
            JOIN documents d ON d.id = f.document_id
            WHERE f.id = ?
            """,
            (fact_id,),
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Fact not found")

        fact = dict(row)
        fact["attributes"] = json.loads(fact["attributes"] or "{}")

        # Fetch relationships where this fact appears
        rel_rows = conn.execute(
            """
            SELECT r.id, r.fact_id_a, r.fact_id_b, r.relationship_type,
                   r.explanation, r.confidence,
                   fa.fact_text AS fact_a_text, fa.document_id AS fact_a_doc,
                   fb.fact_text AS fact_b_text, fb.document_id AS fact_b_doc,
                   da.filename AS doc_a_name, db2.filename AS doc_b_name
            FROM relationships r
            JOIN facts fa ON fa.id = r.fact_id_a
            JOIN facts fb ON fb.id = r.fact_id_b
            JOIN documents da ON da.id = fa.document_id
            JOIN documents db2 ON db2.id = fb.document_id
            WHERE r.fact_id_a = ? OR r.fact_id_b = ?
            ORDER BY r.confidence DESC
            """,
            (fact_id, fact_id),
        ).fetchall()

        fact["relationships"] = [dict(r) for r in rel_rows]
        return fact
    finally:
        conn.close()
