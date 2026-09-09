"""
financial_normalizer.py — Financial Metric Canonicalization & Mathematical Variance Engine.

Tailored for Superjoin Finance:
  - Canonicalizes heterogeneous metric names across filings (e.g. "revenue from operations", "sales", "turnover" -> "revenue.operations")
  - Normalizes currencies and scale multipliers (Crores, Millions, Billions, Lakhs, Tonnes) to base standard numbers
  - Tracks accounting standards: Ind AS / US GAAP vs Non-GAAP Adjusted EBITDA
  - Computes exact mathematical variances and basis-point deltas between compared facts
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

# Scale multiplier factors
MULTIPLIERS = {
    "cr": 10_000_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "mn": 1_000_000,
    "million": 1_000_000,
    "millions": 1_000_000,
    "bn": 1_000_000_000,
    "billion": 1_000_000_000,
    "billions": 1_000_000_000,
    "k": 1_000,
    "thousand": 1_000,
}

# Regex to detect currency and scale
NUMERIC_SCALE_PATTERN = re.compile(
    r"(?:[₹$€£]|INR|USD)?\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|mn|million|millions|bn|billion|billions|k|thousand|tons|tonnes|metric tonnes)?",
    re.IGNORECASE,
)

PERCENT_PATTERN = re.compile(r"(-?\d+(?:\.\d+)?)\s*%", re.IGNORECASE)


def parse_normalized_number(text: str) -> Tuple[Optional[float], str]:
    """
    Extract a normalized base number and unit from text.
    Examples:
      '₹3,646.5 Cr' -> (36465000000.0, 'INR')
      '740 million' -> (740000000.0, 'COUNT')
      '8.2%' -> (8.2, 'PERCENT')
    """
    if not text:
        return None, "UNKNOWN"

    # 1. Check percentage
    pct_match = PERCENT_PATTERN.search(text)
    if pct_match:
        try:
            return float(pct_match.group(1)), "PERCENT"
        except ValueError:
            pass

    # 2. Check currency & scale
    match = NUMERIC_SCALE_PATTERN.search(text)
    if match:
        raw_num_str = match.group(1).replace(",", "")
        scale_str = (match.group(2) or "").lower()

        try:
            val = float(raw_num_str)
            mult = MULTIPLIERS.get(scale_str, 1)
            normalized_val = val * mult

            unit = "COUNT"
            if "₹" in text or "INR" in text.upper() or "crore" in text.lower() or "cr" in text.lower():
                unit = "INR"
            elif "$" in text or "USD" in text.upper():
                unit = "USD"
            elif "ton" in text.lower():
                unit = "TONS"

            return normalized_val, unit
        except ValueError:
            pass

    return None, "UNKNOWN"


def infer_canonical_metric(text: str) -> str:
    """Infer the canonical financial/operational metric category."""
    lower = text.lower()
    if "revenue" in lower or "turnover" in lower or "sales" in lower:
        return "financial.revenue"
    if "ebitda" in lower:
        return "financial.ebitda"
    if "parcel" in lower or "shipment" in lower or "orders" in lower:
        return "operational.express_parcels"
    if "ptl" in lower or "freight" in lower or "tonnage" in lower:
        return "operational.ptl_freight"
    if "pin code" in lower or "pincode" in lower or "coverage" in lower:
        return "infrastructure.pincodes"
    if "gdp" in lower:
        return "macro.gdp_growth"
    if "inflation" in lower or "cpi" in lower:
        return "macro.cpi_inflation"
    if "deficit" in lower:
        return "fiscal.deficit"
    if "market share" in lower:
        return "market.share"
    return "general.metric"


def infer_accounting_standard(text: str, attributes: Dict[str, Any]) -> str:
    """Determine whether a statement is Ind AS / Statutory GAAP or Non-GAAP Adjusted."""
    combined = f"{text} {attributes}".lower()
    if "adjusted" in combined or "non-gaap" in combined or "excluding" in combined:
        return "Non-GAAP (Adjusted)"
    if "ind as" in combined or "statutory" in combined or "reported" in combined:
        return "Ind AS / Statutory"
    return "Standard Reporting"


def calculate_variance(val_a: Optional[float], val_b: Optional[float], unit: str = "") -> Dict[str, Any]:
    """
    Compute absolute and percentage variance between two numerical values.
    Returns structured metrics suitable for financial modeling and Excel sheets.
    """
    if val_a is None or val_b is None:
        return {
            "has_variance": False,
            "absolute_delta": None,
            "percentage_delta": None,
            "formatted_variance": "N/A (Non-numerical)",
        }

    abs_delta = abs(val_a - val_b)
    base = max(abs(val_a), 1e-9)
    pct_delta = (abs_delta / base) * 100.0

    if unit == "PERCENT":
        # For percentage values (e.g. 7.2% vs 6.5%), express difference in basis points
        bps = round(abs_delta * 100)
        if bps == 0:
            formatted = "0 bps (Exact Match)"
        else:
            formatted = f"{bps} bps divergence"
    elif pct_delta < 0.01:
        formatted = "0.00% (Exact Match)"
    elif pct_delta > 100:
        formatted = f"+{pct_delta:.1f}% (Multi-Year Growth)"
    else:
        formatted = f"{pct_delta:.2f}% Variance"

    return {
        "has_variance": True,
        "val_a": val_a,
        "val_b": val_b,
        "unit": unit,
        "absolute_delta": round(abs_delta, 2),
        "percentage_delta": round(pct_delta, 2),
        "formatted_variance": formatted,
    }
