"""
fact_extractor.py — Extract structured facts from text chunks using Gemini and Multi-Key Pool.

Each fact has:
  - fact_text:      A concise, self-contained statement of the fact.
  - fact_type:      A free-form category inferred from the content.
  - attributes:     A flat key-value dict enriched with canonical metrics, normalized numbers,
                    and accounting standards (Ind AS vs Non-GAAP).
  - evidence_quote: The exact verbatim span from the source text that supports this fact.
  - page_number:    The page number supplied by the caller.

Graceful Multi-Key Rotation:
  - Automatically acquires an active key from KeyPoolManager.
  - If a key triggers HTTP 429, quarantines it and instantly falls back to the next key.
"""

from __future__ import annotations

import json
import logging
import textwrap
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from financial_normalizer import infer_accounting_standard, infer_canonical_metric, parse_normalized_number
from key_pool import key_pool

logger = logging.getLogger(__name__)

# Preferred model: Gemini 2.0 Flash / 2.5 Flash / 3.5 Flash Lite
_MODEL_NAME = "gemini-2.0-flash"


def get_api_key() -> Optional[str]:
    """Helper to check if any active key exists."""
    status = key_pool.get_status()
    return "active" if status["healthy_keys"] > 0 else None


def set_api_key(key: str) -> None:
    """Set or update keys in the pool."""
    key_pool.set_keys([key])


_SYSTEM_PROMPT = textwrap.dedent(
    """\
    You are a financial and business fact-extraction engine for Superjoin Finance.

    Given a passage from a document (e.g. annual report, prospectus, earnings deck, economic review),
    extract every meaningful, verifiable fact.
    Focus on:
    - Financial figures (Revenue, EBITDA, Net Income, Margins, Cash reserves, Debt)
    - Operational & market metrics (Shipment volumes, tonnage, pin codes, market share)
    - Macroeconomic indicators (GDP growth, CPI inflation, CAD, Fiscal Deficits)
    - Accounting classifications (Ind AS / GAAP reported vs Adjusted / Non-GAAP)
    - Personnel, governance, and infrastructure details

    For each fact, output a JSON object with exactly these fields:
    {
      "fact_text": "<concise, self-contained statement with exact numbers and periods>",
      "fact_type": "<inferred category, e.g. financial_metric | operational_metric | macro_metric | infrastructure | personnel>",
      "attributes": {
        "metric_name": "<raw metric name>",
        "period": "<fiscal period, e.g. FY21, FY24, Q4 FY24>",
        "reported_value": "<exact string value with units>",
        "accounting_standard": "<Ind AS | Statutory | Non-GAAP Adjusted | Unspecified>"
      },
      "evidence_quote": "<exact verbatim phrase from the passage that proves this fact>"
    }

    Return a JSON array of these objects. If no meaningful facts are present, return [].
    Do NOT invent facts not present in the passage.
    """
)


@dataclass
class ExtractedFact:
    fact_text: str
    fact_type: str
    attributes: Dict[str, Any]
    evidence_quote: str
    page_number: int


def extract_facts_from_chunk(chunk_text: str, page_number: int, max_retries: int = 3) -> List[ExtractedFact]:
    """Call Gemini across the multi-key pool with automatic 429 failover."""
    for attempt in range(max_retries):
        model, key_used = key_pool.acquire_client(model_name=_MODEL_NAME)
        if model is None:
            logger.warning(
                "No active Gemini API keys available in KeyPool. Skipping LLM extraction on page %d.",
                page_number,
            )
            return []

        prompt = f"PASSAGE (page {page_number}):\n\n{chunk_text}"
        try:
            response = model.generate_content([_SYSTEM_PROMPT, prompt])
            raw = response.text.strip()

            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw

            data = json.loads(raw)
            if not isinstance(data, list):
                logger.warning("Gemini returned non-list JSON on page %d", page_number)
                return []

            facts: List[ExtractedFact] = []
            for item in data:
                try:
                    f_text = str(item.get("fact_text", "")).strip()
                    if not f_text:
                        continue

                    raw_attrs = item.get("attributes", {}) if isinstance(item.get("attributes"), dict) else {}

                    # Financial canonicalization & normalization
                    c_metric = infer_canonical_metric(f_text)
                    norm_val, base_unit = parse_normalized_number(f_text)
                    acct_std = infer_accounting_standard(f_text, raw_attrs)

                    raw_attrs["canonical_metric"] = c_metric
                    raw_attrs["normalized_value"] = norm_val
                    raw_attrs["base_unit"] = base_unit
                    raw_attrs["accounting_basis"] = acct_std

                    facts.append(
                        ExtractedFact(
                            fact_text=f_text,
                            fact_type=str(item.get("fact_type", "general")).strip().lower(),
                            attributes=raw_attrs,
                            evidence_quote=str(item.get("evidence_quote", "")).strip(),
                            page_number=page_number,
                        )
                    )
                except Exception as e:
                    logger.warning("Skipping malformed fact item: %s — %s", item, e)

            return facts

        except Exception as e:
            err_msg = str(e).lower()
            if "resourceexhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
                logger.warning(
                    "429 Quota limit hit on key during page %d extraction. Quarantining key and rotating...",
                    page_number,
                )
                if key_used:
                    key_pool.report_429(key_used, cooldown_seconds=60.0)
                # Next attempt will automatically select the next healthy key in the pool!
                continue
            else:
                logger.error("Gemini API error on page %d: %s", page_number, e)
                if key_used:
                    key_pool.report_error(key_used)
                return []

    return []
