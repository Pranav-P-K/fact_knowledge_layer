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

Failures (malformed JSON, empty extractions) are logged and return an empty list
so the pipeline continues uninterrupted.
"""

from __future__ import annotations

import json
import logging
import os
import textwrap
from dataclasses import dataclass
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv

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

_SYSTEM_PROMPT = textwrap.dedent(
    """\
    You are a precise fact-extraction engine.

    Given a passage from a document, extract every meaningful, verifiable fact.
    Focus on:
    - Numerical values (financial figures, dates, quantities, percentages, addresses)
    - Personnel changes (appointments, resignations, roles)
    - Legal or regulatory statements (compliance, violations, rulings)
    - Product or service specifications
    - Locations and operational details

    For each fact, output a JSON object with exactly these fields:
    {
      "fact_text": "<concise, self-contained statement>",
      "fact_type": "<inferred category, e.g. financial_metric | personnel | address | legal_clause | specification>",
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


def extract_facts_from_chunk(chunk_text: str, page_number: int) -> List[ExtractedFact]:
    """Call Gemini and parse the structured fact list. Returns [] on failure."""
    prompt = f"PASSAGE (page {page_number}):\n\n{chunk_text}"
    try:
        response = _model.generate_content([_SYSTEM_PROMPT, prompt])
        raw = response.text.strip()

        # Gemini sometimes wraps JSON in ```json ... ```
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
                facts.append(
                    ExtractedFact(
                        fact_text=str(item.get("fact_text", "")).strip(),
                        fact_type=str(item.get("fact_type", "unknown")).strip().lower(),
                        attributes=item.get("attributes", {}) if isinstance(item.get("attributes"), dict) else {},
                        evidence_quote=str(item.get("evidence_quote", "")).strip(),
                        page_number=page_number,
                    )
                )
            except Exception as e:
                logger.warning("Skipping malformed fact item: %s — %s", item, e)

        return [f for f in facts if f.fact_text]  # drop empty

    except json.JSONDecodeError as e:
        logger.error("JSON parse error on page %d: %s", page_number, e)
        return []
    except Exception as e:
        logger.error("Gemini API error on page %d: %s", page_number, e)
        return []
