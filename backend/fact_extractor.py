"""
fact_extractor.py — Extract structured facts from text chunks using Gemini.

Each fact has:
  - fact_text:      A concise, self-contained statement of the fact.
  - fact_type:      A free-form category inferred from the content
                    (e.g. 'financial_metric', 'personnel', 'address',
                     'legal_clause', 'product_specification', …).
  - attributes:     A flat key-value dict with domain-specific fields
                    (e.g. {"amount": "₹10 Cr", "period": "FY2023"}).
  - evidence_quote: The exact verbatim span from the source text that supports this fact.
  - page_number:    The page number supplied by the caller.

Graceful handling:
  - If GEMINI_API_KEY is missing or invalid, logs a warning and returns [] instead of crashing.
  - Retries on rate limits (ResourceExhausted / 429) with exponential backoff.
"""

from __future__ import annotations

import json
import logging
import os
import textwrap
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_MODEL_NAME = "gemini-2.0-flash"
_cached_key: Optional[str] = None
_model: Optional[genai.GenerativeModel] = None


def get_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from environment or memory."""
    global _cached_key
    if _cached_key:
        return _cached_key
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k and k not in ("placeholder", "your_gemini_api_key_here", "your_key_here"):
        _cached_key = k
        return k
    return None


def set_api_key(key: str) -> None:
    """Set or update the API key at runtime."""
    global _cached_key, _model
    _cached_key = key.strip()
    os.environ["GEMINI_API_KEY"] = _cached_key
    _model = None  # Force re-creation with new key


def get_model() -> Optional[genai.GenerativeModel]:
    """Lazily initialize the Gemini GenerativeModel if an API key is available."""
    global _model
    if _model is not None:
        return _model

    key = get_api_key()
    if not key:
        return None

    try:
        genai.configure(api_key=key)
        _model = genai.GenerativeModel(
            _MODEL_NAME,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        return _model
    except Exception as e:
        logger.error("Failed to initialize Gemini model: %s", e)
        return None


_SYSTEM_PROMPT = textwrap.dedent(
    """\
    You are a precise fact-extraction engine.

    Given a passage from a document, extract every meaningful, verifiable fact.
    Focus on:
    - Numerical values (financial figures, dates, quantities, percentages, addresses)
    - Personnel changes (appointments, resignations, roles)
    - Legal or regulatory statements (compliance, violations, rulings)
    - Product or service specifications
    - Locations, infrastructure, and operational details

    For each fact, output a JSON object with exactly these fields:
    {
      "fact_text": "<concise, self-contained statement>",
      "fact_type": "<inferred category, e.g. financial_metric | personnel | address | legal_clause | specification | infrastructure>",
      "attributes": { "<key>": "<value>", ... },
      "evidence_quote": "<exact verbatim phrase from the passage that proves this fact>"
    }

    Return a JSON array of these objects. If no meaningful facts are present, return [].
    Do NOT invent facts not present in the passage.
    Do NOT include trivial formatting or boilerplate as facts.
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
    """Call Gemini and parse the structured fact list. Retries with backoff on rate limits."""
    model = get_model()
    if model is None:
        logger.warning(
            "GEMINI_API_KEY is not configured. Skipping LLM fact extraction on page %d.",
            page_number,
        )
        return []

    prompt = f"PASSAGE (page {page_number}):\n\n{chunk_text}"
    backoff = 2.0

    for attempt in range(max_retries):
        try:
            response = model.generate_content([_SYSTEM_PROMPT, prompt])
            raw = response.text.strip()

            # Strip markdown code fencing if present
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
                    facts.append(
                        ExtractedFact(
                            fact_text=f_text,
                            fact_type=str(item.get("fact_type", "general")).strip().lower(),
                            attributes=item.get("attributes", {}) if isinstance(item.get("attributes"), dict) else {},
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
                if attempt < max_retries - 1:
                    logger.warning(
                        "Rate limit hit on page %d (attempt %d/%d). Backing off %.1fs...",
                        page_number, attempt + 1, max_retries, backoff,
                    )
                    time.sleep(backoff)
                    backoff *= 2
                    continue
            logger.error("Gemini API error on page %d: %s", page_number, e)
            return []

    return []
