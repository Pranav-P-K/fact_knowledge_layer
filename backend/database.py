"""
database.py — SQLite schema and connection helpers.

Three tables:
  documents   — one row per uploaded PDF
  facts       — extracted facts with dynamic schema via attributes JSON + embedding blob
  relationships — cross-document fact pairs: SUPPORTS | CONTRADICTS | RECONCILES
"""

import sqlite3
import json
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist yet."""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT    NOT NULL,
                upload_time TEXT    NOT NULL DEFAULT (datetime('now')),
                page_count  INTEGER NOT NULL DEFAULT 0,
                status      TEXT    NOT NULL DEFAULT 'processing'
            );

            CREATE TABLE IF NOT EXISTS facts (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id    INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                fact_text      TEXT    NOT NULL,
                fact_type      TEXT    NOT NULL,
                attributes     TEXT    NOT NULL DEFAULT '{}',
                evidence_quote TEXT    NOT NULL DEFAULT '',
                page_number    INTEGER NOT NULL DEFAULT 0,
                embedding      BLOB,
                created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_facts_document ON facts(document_id);
            CREATE INDEX IF NOT EXISTS idx_facts_type     ON facts(fact_type);

            CREATE TABLE IF NOT EXISTS relationships (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id_a        INTEGER NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
                fact_id_b        INTEGER NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
                relationship_type TEXT   NOT NULL CHECK(relationship_type IN ('SUPPORTS','CONTRADICTS','RECONCILES')),
                explanation      TEXT    NOT NULL DEFAULT '',
                confidence       REAL    NOT NULL DEFAULT 0.0,
                created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(fact_id_a, fact_id_b)
            );

            CREATE INDEX IF NOT EXISTS idx_rel_a ON relationships(fact_id_a);
            CREATE INDEX IF NOT EXISTS idx_rel_b ON relationships(fact_id_b);
            """
        )
        conn.commit()
    finally:
        conn.close()


# ── CRUD helpers ────────────────────────────────────────────────────────────

def insert_document(filename: str, page_count: int) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO documents(filename, page_count, status) VALUES(?,?,?)",
            (filename, page_count, "processing"),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_document_status(doc_id: int, status: str) -> None:
    conn = get_connection()
    try:
        conn.execute("UPDATE documents SET status=? WHERE id=?", (status, doc_id))
        conn.commit()
    finally:
        conn.close()


def insert_fact(
    document_id: int,
    fact_text: str,
    fact_type: str,
    attributes: dict,
    evidence_quote: str,
    page_number: int,
    embedding: bytes,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO facts(document_id, fact_text, fact_type, attributes,
                              evidence_quote, page_number, embedding)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                document_id,
                fact_text,
                fact_type,
                json.dumps(attributes),
                evidence_quote,
                page_number,
                embedding,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def insert_relationship(
    fact_id_a: int,
    fact_id_b: int,
    relationship_type: str,
    explanation: str,
    confidence: float,
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO relationships
                (fact_id_a, fact_id_b, relationship_type, explanation, confidence)
            VALUES(?,?,?,?,?)
            """,
            (fact_id_a, fact_id_b, relationship_type, explanation, confidence),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_facts_with_embeddings(exclude_document_id: int | None = None):
    """Return all facts (optionally excluding a specific document) including raw embedding bytes."""
    conn = get_connection()
    try:
        if exclude_document_id is not None:
            rows = conn.execute(
                "SELECT id, document_id, fact_text, embedding FROM facts WHERE document_id != ? AND embedding IS NOT NULL",
                (exclude_document_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, document_id, fact_text, embedding FROM facts WHERE embedding IS NOT NULL"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_facts_for_document(document_id: int):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, document_id, fact_text, embedding FROM facts WHERE document_id=? AND embedding IS NOT NULL",
            (document_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def clear_all_data() -> None:
    """Wipe all documents, facts, and relationships."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM relationships")
        conn.execute("DELETE FROM facts")
        conn.execute("DELETE FROM documents")
        conn.commit()
    finally:
        conn.close()

