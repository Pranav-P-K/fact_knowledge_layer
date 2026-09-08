"""
routers/documents.py — PDF upload and document listing endpoints.

POST /documents/upload
  Accepts a PDF file, runs the full extraction pipeline in the background,
  and immediately returns the document id so the UI can poll for status.

GET /documents
  Returns all documents with their status and fact count.

GET /documents/{doc_id}
  Returns a single document with metadata.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

import database as db
from embedder import embed_text
from fact_extractor import extract_facts_from_chunk
from pdf_processor import extract_chunks
from relationship_detector import detect_relationships_for_document

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


async def _process_pdf(doc_id: int, pdf_bytes: bytes) -> None:
    """Background task: extract facts, embed them, detect relationships."""
    try:
        # 1. Parse PDF into chunks
        chunks, page_count = extract_chunks(pdf_bytes)
        logger.info("Document %d: %d chunks from %d pages", doc_id, len(chunks), page_count)

        # 2. Extract facts per chunk
        all_facts = []
        for chunk in chunks:
            facts = extract_facts_from_chunk(chunk.text, chunk.page_number)
            all_facts.extend(facts)

        logger.info("Document %d: %d facts extracted", doc_id, len(all_facts))

        # 3. Embed and store each fact
        for fact in all_facts:
            embedding_blob = embed_text(fact.fact_text)
            db.insert_fact(
                document_id=doc_id,
                fact_text=fact.fact_text,
                fact_type=fact.fact_type,
                attributes=fact.attributes,
                evidence_quote=fact.evidence_quote,
                page_number=fact.page_number,
                embedding=embedding_blob,
            )

        # 4. Detect cross-document relationships (incremental)
        n_rels = detect_relationships_for_document(doc_id)
        logger.info("Document %d: %d new relationships found", doc_id, n_rels)

        db.update_document_status(doc_id, "done")

    except Exception as e:
        logger.exception("Pipeline failed for document %d: %s", doc_id, e)
        db.update_document_status(doc_id, "failed")


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Quick page count before full processing
    try:
        _, page_count = extract_chunks(pdf_bytes)
    except Exception:
        page_count = 0

    doc_id = db.insert_document(file.filename, page_count)
    background_tasks.add_task(_process_pdf, doc_id, pdf_bytes)

    return {"document_id": doc_id, "filename": file.filename, "status": "processing"}


@router.get("")
def list_documents() -> List[Dict[str, Any]]:
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """
            SELECT d.id, d.filename, d.upload_time, d.page_count, d.status,
                   COUNT(f.id) AS fact_count
            FROM documents d
            LEFT JOIN facts f ON f.document_id = d.id
            GROUP BY d.id
            ORDER BY d.id DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/{doc_id}")
def get_document(doc_id: int) -> Dict[str, Any]:
    conn = db.get_connection()
    try:
        row = conn.execute(
            """
            SELECT d.id, d.filename, d.upload_time, d.page_count, d.status,
                   COUNT(f.id) AS fact_count
            FROM documents d
            LEFT JOIN facts f ON f.document_id = d.id
            WHERE d.id = ?
            GROUP BY d.id
            """,
            (doc_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        return dict(row)
    finally:
        conn.close()
