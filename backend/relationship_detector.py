"""
relationship_detector.py — Identify and classify cross-document fact relationships.

Pipeline (incremental — only runs on newly inserted facts):
  1. Load all existing facts from other documents (with embeddings).
  2. For each new fact, compute cosine similarity against every existing fact.
  3. Pairs above SIMILARITY_THRESHOLD are sent to Gemini for classification:
       SUPPORTS | CONTRADICTS | RECONCILES | UNRELATED
  4. Non-UNRELATED pairs are stored in the relationships table.

Design notes:
  - We only compare facts from *different* documents to avoid trivial self-matches.
  - TOP_K limits how many candidates per new fact are sent to the LLM.
  - The LLM receives both fact texts + their evidence quotes for context-aware reasoning.
"""

from __future__ import annotations

import json
import logging
import os
import textwrap
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv

from database import (
    get_all_facts_with_embeddings,
    get_facts_for_document,
    insert_relationship,
)
from embedder import cosine_similarity

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

_MODEL_NAME = "gemini-2.0-flash"
_model = genai.GenerativeModel(
    _MODEL_NAME,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.1,
    ),
)

SIMILARITY_THRESHOLD = 0.68  # tuned: lower → more candidates, higher → fewer but more precise
TOP_K = 5                    # max candidates per new fact sent to LLM

_CLASSIFY_SYSTEM = textwrap.dedent(
    """\
    You are a fact-comparison engine. You will receive two facts extracted from different
    documents, along with their source evidence quotes.

    Classify the relationship as exactly one of:
      SUPPORTS    — both facts say essentially the same thing (even if worded differently)
      CONTRADICTS — the facts make incompatible or opposite claims with no obvious reconciliation
      RECONCILES  — they appear to contradict but can be explained by context
                    (e.g. different time periods, different scopes, different units, partial data)
      UNRELATED   — the facts are about different subjects and have no meaningful relationship

    Return a JSON object with:
    {
      "relationship": "SUPPORTS | CONTRADICTS | RECONCILES | UNRELATED",
      "explanation": "<1–3 sentence reasoning, including what context resolves an apparent conflict>",
      "confidence": <float 0.0–1.0>
    }
    """
)


def _classify_pair(fact_a: Dict[str, Any], fact_b: Dict[str, Any]) -> Dict[str, Any] | None:
    """Call Gemini to classify the relationship between two facts."""
    prompt = (
        f"FACT A (id={fact_a['id']}):\n{fact_a['fact_text']}\n"
        f"Evidence: \"{fact_a.get('evidence_quote', '')}\"\n\n"
        f"FACT B (id={fact_b['id']}):\n{fact_b['fact_text']}\n"
        f"Evidence: \"{fact_b.get('evidence_quote', '')}\""
    )
    try:
        response = _model.generate_content([_CLASSIFY_SYSTEM, prompt])
        raw = response.text.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw
        return json.loads(raw)
    except Exception as e:
        logger.error("Classification failed for facts (%s, %s): %s", fact_a["id"], fact_b["id"], e)
        return None


def detect_relationships_for_document(document_id: int) -> int:
    """
    Run relationship detection for all newly inserted facts of `document_id`
    against all facts from other documents.

    Returns the number of new relationships stored.
    """
    # Facts from the new document (need embeddings)
    new_facts = get_facts_for_document(document_id)
    if not new_facts:
        return 0

    # All facts from other documents
    existing_facts = get_all_facts_with_embeddings(exclude_document_id=document_id)
    if not existing_facts:
        return 0

    stored = 0

    for new_fact in new_facts:
        if not new_fact["embedding"]:
            continue

        # Compute similarity to all existing facts
        scored = []
        for ex_fact in existing_facts:
            if not ex_fact["embedding"]:
                continue
            sim = cosine_similarity(new_fact["embedding"], ex_fact["embedding"])
            if sim >= SIMILARITY_THRESHOLD:
                scored.append((sim, ex_fact))

        # Sort descending and take top-K
        scored.sort(key=lambda x: x[0], reverse=True)
        candidates = scored[:TOP_K]

        for sim, ex_fact in candidates:
            result = _classify_pair(new_fact, ex_fact)
            if result is None:
                continue

            rel_type = result.get("relationship", "UNRELATED").upper()
            if rel_type not in ("SUPPORTS", "CONTRADICTS", "RECONCILES"):
                continue

            explanation = result.get("explanation", "")
            confidence = float(result.get("confidence", 0.0))

            # Always store with lower id first to avoid duplicates
            id_a, id_b = sorted([new_fact["id"], ex_fact["id"]])
            insert_relationship(id_a, id_b, rel_type, explanation, confidence)
            stored += 1
            logger.info(
                "Relationship %s (%.2f) between fact %d and fact %d",
                rel_type, confidence, id_a, id_b,
            )

    return stored
