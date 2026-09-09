"""
relationship_detector.py — Identify and classify cross-document fact relationships.

Pipeline (incremental — only runs on newly inserted facts):
  1. Load all existing facts from other documents (with embeddings).
  2. For each new fact, compute cosine similarity against every existing fact.
  3. Pairs above SIMILARITY_THRESHOLD are sent to Gemini for classification:
       SUPPORTS | CONTRADICTS | RECONCILES | UNRELATED
  4. Mathematical variance is computed and combined with the LLM reasoning.
  5. Non-UNRELATED pairs are stored in the relationships table.

Features:
  - Multi-Key provider pool with 429 quarantine failover.
  - Contextual financial reasoning.
"""

from __future__ import annotations

import json
import logging
import textwrap
from typing import Any, Dict, List, Optional

from database import (
    get_all_facts_with_embeddings,
    get_facts_for_document,
    insert_relationship,
)
from embedder import cosine_similarity
from financial_normalizer import calculate_variance, parse_normalized_number
from key_pool import key_pool

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.68  # tuned: lower → more candidates, higher → fewer but more precise
TOP_K = 5                    # max candidates per new fact sent to LLM

_CLASSIFY_SYSTEM = textwrap.dedent(
    """\
    You are an expert financial and analytical fact-comparison engine for Superjoin Finance.
    You will receive two facts extracted from different documents, along with their source evidence quotes.

    Classify the relationship as exactly one of:
      SUPPORTS    — both facts state the same metric or claim (even if expressed with different scale/wording)
      CONTRADICTS — the facts make incompatible or opposite claims for the same scope/period without reconciliation
      RECONCILES  — they appear to conflict numerically or semantically, but are reconciled by context
                    (e.g. different fiscal years/periods, organic multi-year growth, different accounting standards like GAAP vs Adjusted EBITDA, or different geographic scopes)
      UNRELATED   — the facts are about different subjects and have no meaningful cross-document connection

    Return a JSON object with:
    {
      "relationship": "SUPPORTS | CONTRADICTS | RECONCILES | UNRELATED",
      "explanation": "<1–3 sentence reasoning, explicitly mentioning period, accounting basis, or scope context>",
      "confidence": <float 0.0–1.0>
    }
    """
)


def _classify_pair(fact_a: Dict[str, Any], fact_b: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Call Gemini across the multi-key pool to classify the relationship."""
    for attempt in range(max_retries):
        model, key_used = key_pool.acquire_client()
        if model is None:
            return None

        prompt = (
            f"FACT A (id={fact_a['id']}):\n{fact_a['fact_text']}\n"
            f"Evidence: \"{fact_a.get('evidence_quote', '')}\"\n\n"
            f"FACT B (id={fact_b['id']}):\n{fact_b['fact_text']}\n"
            f"Evidence: \"{fact_b.get('evidence_quote', '')}\""
        )

        try:
            response = model.generate_content([_CLASSIFY_SYSTEM, prompt])
            raw = response.text.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw
            return json.loads(raw)
        except Exception as e:
            err_msg = str(e).lower()
            if "resourceexhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
                logger.warning(
                    "Rate limit on key during relationship classification (%d, %d). Quarantining and rotating...",
                    fact_a["id"], fact_b["id"],
                )
                if key_used:
                    key_pool.report_429(key_used, cooldown_seconds=60.0)
                continue
            else:
                logger.error("Classification failed for facts (%s, %s): %s", fact_a["id"], fact_b["id"], e)
                if key_used:
                    key_pool.report_error(key_used)
                return None

    return None


def detect_relationships_for_document(document_id: int) -> int:
    """
    Run relationship detection for all newly inserted facts of `document_id`
    against all facts from other documents.

    Returns the number of new relationships stored.
    """
    status = key_pool.get_status()
    if status["healthy_keys"] == 0:
        logger.warning("No active Gemini API keys in pool. Skipping live relationship detection.")
        return 0

    new_facts = get_facts_for_document(document_id)
    if not new_facts:
        return 0

    existing_facts = get_all_facts_with_embeddings(exclude_document_id=document_id)
    if not existing_facts:
        return 0

    stored = 0

    for new_fact in new_facts:
        if not new_fact["embedding"]:
            continue

        scored = []
        for ex_fact in existing_facts:
            if not ex_fact["embedding"]:
                continue
            sim = cosine_similarity(new_fact["embedding"], ex_fact["embedding"])
            if sim >= SIMILARITY_THRESHOLD:
                scored.append((sim, ex_fact))

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

            # Enrich explanation with mathematical variance if numbers are present
            val_a, u_a = parse_normalized_number(new_fact["fact_text"])
            val_b, u_b = parse_normalized_number(ex_fact["fact_text"])
            var_info = calculate_variance(val_a, val_b, u_a if u_a != "UNKNOWN" else u_b)
            if var_info["has_variance"] and var_info["formatted_variance"]:
                explanation = f"[{var_info['formatted_variance']}] {explanation}"

            id_a, id_b = sorted([new_fact["id"], ex_fact["id"]])
            insert_relationship(id_a, id_b, rel_type, explanation, confidence)
            stored += 1
            logger.info(
                "Relationship %s (%.2f) between fact %d and fact %d",
                rel_type, confidence, id_a, id_b,
            )

    return stored
