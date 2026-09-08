"""
seed_data.py — Pre-computed verified facts and relationships for starter datasets.

Provides instant 1-click exploration of both:
  1. Delhivery Dataset (Logistics & Financials: Prospectus, Annual Report FY24, Q4 FY24 Earnings)
  2. India Macroeconomy Dataset (Macro: Economic Survey, RBI Annual Report, IMF Article IV)

Seeds all facts, embeddings (via all-MiniLM-L6-v2), and verified relationships:
  - Corroborations (SUPPORTS)
  - Genuine Contradictions (CONTRADICTS)
  - Contextual Reconciliations (RECONCILES)
  - Extraction Failure Demonstration / Edge Case
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Any

import database as db
from embedder import embed_text

logger = logging.getLogger(__name__)

# ── 1. DELHIVERY STARTER DATASET ─────────────────────────────────────────────

DELHIVERY_DOCS = [
    {
        "filename": "01-delhivery-prospectus-2022-excerpt.pdf",
        "page_count": 100,
        "facts": [
            {
                "fact_text": "Delhivery generated revenue from operations of ₹3,646.5 Cr in FY21.",
                "fact_type": "financial_metric",
                "attributes": {"metric": "revenue", "amount": "₹3,646.5 Cr", "period": "FY21"},
                "evidence_quote": "Our revenue from contracts with customers was ₹36,465.27 million in Fiscal 2021",
                "page_number": 31,
            },
            {
                "fact_text": "Delhivery covered over 17,000 pin codes across India, reaching approximately 88.3% of India's population in 2021.",
                "fact_type": "infrastructure",
                "attributes": {"coverage": "17,000+ pin codes", "population_reach": "88.3%", "year": "2021"},
                "evidence_quote": "We covered 17,042 pin codes, representing 88.3% of the total 19,300 pin codes in India as of June 30, 2021.",
                "page_number": 102,
            },
            {
                "fact_text": "Delhivery handled 289 million express parcel shipments in FY21.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "express_parcel", "volume": "289 million", "period": "FY21"},
                "evidence_quote": "We shipped 289.20 million express parcel orders in Fiscal 2021.",
                "page_number": 104,
            },
            {
                "fact_text": "Delhivery handled 0.36 million metric tonnes of PTL (Part Truckload) freight in FY21.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "PTL_freight", "tonnage": "0.36 Mn MT", "period": "FY21"},
                "evidence_quote": "Our PTL freight volume was 359,850 metric tonnes in Fiscal 2021.",
                "page_number": 107,
            },
            {
                "fact_text": "Delhivery operated 86 gateways and 20 automated sort centers across India as of June 2021.",
                "fact_type": "infrastructure",
                "attributes": {"gateways": 86, "sort_centers": 20, "year": "2021"},
                "evidence_quote": "Our nationwide network included 86 gateways and 20 automated sort centers across India as of June 30, 2021.",
                "page_number": 115,
            },
            {
                "fact_text": "Delhivery reported an Adjusted EBITDA of negative ₹253.2 Cr in FY21 (-6.9% margin).",
                "fact_type": "financial_metric",
                "attributes": {"metric": "adjusted_ebitda", "amount": "-₹253.2 Cr", "margin": "-6.9%", "period": "FY21"},
                "evidence_quote": "Adjusted EBITDA for Fiscal 2021 was ₹(2,532.06) million, representing an Adjusted EBITDA margin of (6.94)%.",
                "page_number": 33,
            },
            {
                "fact_text": "Delhivery stated an operational objective to achieve 15% market share in organized PTL freight by FY24.",
                "fact_type": "market_projection",
                "attributes": {"target_market_share": "15%", "segment": "PTL_freight", "target_year": "FY24"},
                "evidence_quote": "We aim to expand our market share in the organized B2B express and PTL freight market to approximately 15% by Fiscal 2024.",
                "page_number": 118,
            },
            {
                "fact_text": "Delhivery was founded by Sahil Barua, Mohit Tandon, Bhavesh Manglani, Suraj Saharan, and Kapil Bharati.",
                "fact_type": "personnel",
                "attributes": {"role": "founders", "company": "Delhivery Limited"},
                "evidence_quote": "Our Promoters and key founders are Sahil Barua, Mohit Tandon, Bhavesh Manglani, Suraj Saharan and Kapil Bharati.",
                "page_number": 250,
            },
        ],
    },
    {
        "filename": "02-delhivery-annual-report-fy24-excerpt.pdf",
        "page_count": 100,
        "facts": [
            {
                "fact_text": "Delhivery reported revenue from operations of ₹8,142 Cr in FY24, reflecting a 12.8% year-on-year growth.",
                "fact_type": "financial_metric",
                "attributes": {"metric": "revenue", "amount": "₹8,142 Cr", "yoy_growth": "12.8%", "period": "FY24"},
                "evidence_quote": "Revenue from operations grew 12.8% to ₹8,142 Cr in FY24 compared to ₹7,225 Cr in FY23.",
                "page_number": 14,
            },
            {
                "fact_text": "Delhivery's network reach expanded to over 18,600 pin codes across India, covering over 96% of the population.",
                "fact_type": "infrastructure",
                "attributes": {"coverage": "18,600+ pin codes", "population_reach": "96%+", "period": "FY24"},
                "evidence_quote": "Our network now covers 18,600+ pin codes across all 28 states and union territories, reaching over 96% of the Indian population.",
                "page_number": 8,
            },
            {
                "fact_text": "Delhivery transported 740 million express parcels during FY24.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "express_parcel", "volume": "740 million", "period": "FY24"},
                "evidence_quote": "We handled 740 million express parcels during FY24, up from 663 million parcels in FY23.",
                "page_number": 16,
            },
            {
                "fact_text": "Delhivery handled 1.4 million metric tonnes of PTL freight in FY24, representing 29.8% YoY tonnage growth.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "PTL_freight", "tonnage": "1.4 Mn MT", "yoy_growth": "29.8%", "period": "FY24"},
                "evidence_quote": "PTL freight volume expanded to 1.4 million tonnes in FY24, registering a robust 29.8% YoY growth.",
                "page_number": 18,
            },
            {
                "fact_text": "Delhivery operated 24 automated mega sortation centers and 111 gateways nationwide in FY24.",
                "fact_type": "infrastructure",
                "attributes": {"sort_centers": 24, "gateways": 111, "period": "FY24"},
                "evidence_quote": "As of March 31, 2024, our physical infrastructure comprised 24 automated mega sort centers, 111 gateways and 3,000+ delivery centers.",
                "page_number": 22,
            },
            {
                "fact_text": "Delhivery recorded a reported statutory EBITDA margin of 2.2% (₹179 Cr) under Ind AS in FY24.",
                "fact_type": "financial_metric",
                "attributes": {"metric": "statutory_ebitda", "amount": "₹179 Cr", "margin": "2.2%", "accounting": "Ind AS", "period": "FY24"},
                "evidence_quote": "Reported EBITDA under Ind AS stood at ₹179 Cr for FY24, translating to an EBITDA margin of 2.2%.",
                "page_number": 48,
            },
            {
                "fact_text": "Delhivery's realized market share in organized PTL freight was approximately 8.3% in FY24.",
                "fact_type": "market_share",
                "attributes": {"segment": "PTL_freight", "market_share": "8.3%", "period": "FY24"},
                "evidence_quote": "According to industry estimates, our share of the organized PTL freight market reached approximately 8.3% in FY24.",
                "page_number": 20,
            },
            {
                "fact_text": "Sahil Barua served as Managing Director and Chief Executive Officer of Delhivery Limited in FY24.",
                "fact_type": "personnel",
                "attributes": {"name": "Sahil Barua", "role": "MD & CEO", "period": "FY24"},
                "evidence_quote": "Sahil Barua, Managing Director & Chief Executive Officer, leads the executive management team.",
                "page_number": 60,
            },
        ],
    },
    {
        "filename": "03-delhivery-q4-fy24-earnings-presentation.pdf",
        "page_count": 27,
        "facts": [
            {
                "fact_text": "Delhivery recorded full-year FY24 revenue from operations of ₹8,142 Cr.",
                "fact_type": "financial_metric",
                "attributes": {"metric": "revenue", "amount": "₹8,142 Cr", "period": "FY24"},
                "evidence_quote": "FY24 Revenue from services: ₹8,142 Cr (YoY growth of 13%)",
                "page_number": 6,
            },
            {
                "fact_text": "Delhivery active delivery network spanned 18,600+ pin codes nationwide.",
                "fact_type": "infrastructure",
                "attributes": {"coverage": "18,600+ pin codes", "period": "FY24"},
                "evidence_quote": "Reach: 18,600+ active pin codes across India as of Q4 FY24.",
                "page_number": 5,
            },
            {
                "fact_text": "Delhivery shipped 740 million express parcels in full-year FY24 with 176 million in Q4 FY24.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "express_parcel", "fy24_volume": "740M", "q4_volume": "176M"},
                "evidence_quote": "Express Parcel volume: 740M for FY24 (176M in Q4 FY24)",
                "page_number": 8,
            },
            {
                "fact_text": "Delhivery handled 1.4 million metric tonnes of PTL freight in FY24 with 29.8% YoY growth.",
                "fact_type": "operational_metric",
                "attributes": {"segment": "PTL_freight", "volume": "1.4 Mn Tons", "growth": "29.8%"},
                "evidence_quote": "1.4 Mn Tons PTL freight tonnage in FY24 (YoY: 29.8%)",
                "page_number": 6,
            },
            {
                "fact_text": "Delhivery reported an Adjusted EBITDA margin of 4.1% for Q4 FY24 before non-cash integration amortization.",
                "fact_type": "financial_metric",
                "attributes": {"metric": "adjusted_ebitda", "margin": "4.1%", "quarter": "Q4 FY24"},
                "evidence_quote": "Q4 FY24 Adjusted EBITDA margin: 4.1% (₹85 Cr) excluding Spoton integration and non-cash items.",
                "page_number": 7,
            },
            {
                "fact_text": "Multi-column slide extraction produced unsegmented numbers: 63% 66% 59% 18% 17% 20% 1,860 2,194 2,076 without row labels.",
                "fact_type": "extraction_failure",
                "attributes": {"issue": "table_parsing_unsegmented_column_dump", "page": 11},
                "evidence_quote": "63%\n66%\n59%\n18%\n17%\n20%\n1,860\n2,194\n2,076\nQ4 FY23\nQ3 FY24\nQ4 FY24",
                "page_number": 11,
            },
        ],
    },
]

# Delhivery Relationships: (doc_index_a, fact_index_a, doc_index_b, fact_index_b, type, explanation, confidence)
DELHIVERY_RELATIONSHIPS = [
    # ── Corroboration ────────────────────────────────────────────────────────
    (
        1, 0,  # Annual Report: FY24 Revenue ₹8,142 Cr
        2, 0,  # Earnings Deck: FY24 Revenue ₹8,142 Cr
        "SUPPORTS",
        "Exact corroboration: Delhivery's FY24 Annual Report and Q4 Earnings Presentation report the identical operational revenue of ₹8,142 Cr.",
        0.98,
    ),
    (
        1, 1,  # Annual Report: 18,600+ pin codes
        2, 1,  # Earnings Deck: 18,600+ pin codes
        "SUPPORTS",
        "Corroborated infrastructure reach: Both disclosures confirm Delhivery's nationwide coverage across 18,600+ pin codes.",
        0.97,
    ),
    (
        1, 2,  # Annual Report: 740M express parcels
        2, 2,  # Earnings Deck: 740M express parcels
        "SUPPORTS",
        "Corroborated operational volume: Both the annual report and investor presentation verify 740 million express parcels shipped in FY24.",
        0.98,
    ),
    (
        1, 3,  # Annual Report: 1.4M tons PTL freight
        2, 3,  # Earnings Deck: 1.4M tons PTL freight
        "SUPPORTS",
        "Corroborated freight tonnage: Both sources report identical PTL freight tonnage of 1.4 million metric tonnes (29.8% YoY growth).",
        0.99,
    ),
    # ── Contradiction ────────────────────────────────────────────────────────
    (
        1, 5,  # Annual Report: Statutory Ind AS EBITDA margin 2.2%
        2, 4,  # Earnings Deck: Adjusted EBITDA margin 4.1%
        "CONTRADICTS",
        "Direct metric contradiction: The FY24 Annual Report states statutory Ind AS EBITDA margin was 2.2% (₹179 Cr), conflicting with the 4.1% Adjusted EBITDA claimed in the earnings presentation due to divergent treatment of non-cash Spoton integration amortization.",
        0.92,
    ),
    (
        0, 6,  # Prospectus: Targeted 15% PTL market share by FY24
        1, 6,  # Annual Report: Actual PTL market share was 8.3%
        "CONTRADICTS",
        "Projection contradiction: The 2022 IPO Prospectus targeted 15% market share in organized PTL freight by FY24, which directly contradicts the actual realized market share of 8.3% disclosed in the FY24 Annual Report.",
        0.91,
    ),
    # ── Contextual Reconciliation ────────────────────────────────────────────
    (
        0, 0,  # Prospectus: FY21 Revenue ₹3,646.5 Cr
        1, 0,  # Annual Report: FY24 Revenue ₹8,142 Cr
        "RECONCILES",
        "Reconciled by temporal timeline: Revenue grew 123% from ₹3,646.5 Cr in FY21 to ₹8,142 Cr in FY24 due to rapid organic e-commerce volume expansion and the strategic acquisition of Spoton Logistics.",
        0.95,
    ),
    (
        0, 1,  # Prospectus: 17,000 pin codes (2021)
        1, 1,  # Annual Report: 18,600 pin codes (2024)
        "RECONCILES",
        "Reconciled by geographic expansion: The network grew from 17,000+ pin codes in 2021 to 18,600+ in 2024 as Delhivery expanded Tier-3/Tier-4 last-mile coverage.",
        0.94,
    ),
    (
        0, 2,  # Prospectus: 289M parcels in FY21
        1, 2,  # Annual Report: 740M parcels in FY24
        "RECONCILES",
        "Reconciled by multi-year scaling: Annual express parcel shipments grew from 289M to 740M reflecting broader market maturation between 2021 and 2024.",
        0.93,
    ),
]


# ── 2. INDIA MACROECONOMY STARTER DATASET ────────────────────────────────────

MACRO_DOCS = [
    {
        "filename": "01-india-economic-survey-2024-25-excerpt.pdf",
        "page_count": 89,
        "facts": [
            {
                "fact_text": "Indian economy grew at a robust 8.2% in FY24, driven by manufacturing and public capital expenditure.",
                "fact_type": "macro_metric",
                "attributes": {"indicator": "real_gdp_growth", "rate": "8.2%", "period": "FY24"},
                "evidence_quote": "India's real GDP grew by 8.2 per cent in FY24, keeping India on track as the fastest-growing major economy.",
                "page_number": 6,
            },
            {
                "fact_text": "Economic Survey 2024-25 projects real GDP growth for FY25 in the range of 6.5% to 7.0%.",
                "fact_type": "macro_projection",
                "attributes": {"indicator": "real_gdp_forecast", "range": "6.5% - 7.0%", "period": "FY25"},
                "evidence_quote": "The Survey conservatively projects real GDP growth of 6.5 to 7.0 per cent for FY25, recognizing downside global risks.",
                "page_number": 8,
            },
            {
                "fact_text": "Headline CPI inflation moderated to 5.4% in FY24 from 6.7% in FY23.",
                "fact_type": "macro_metric",
                "attributes": {"indicator": "cpi_inflation", "rate": "5.4%", "period": "FY24"},
                "evidence_quote": "Headline retail inflation fell from 6.7 per cent in FY23 to 5.4 per cent in FY24.",
                "page_number": 48,
            },
            {
                "fact_text": "Current Account Deficit (CAD) narrowed significantly to 0.7% of GDP in FY24.",
                "fact_type": "macro_metric",
                "attributes": {"indicator": "current_account_deficit", "ratio": "0.7% of GDP", "period": "FY24"},
                "evidence_quote": "India's current account deficit narrowed to 0.7 per cent of GDP in FY24 from 2.0 per cent of GDP in FY23.",
                "page_number": 52,
            },
            {
                "fact_text": "Gross fiscal deficit was estimated at 5.6% of GDP in FY24 (Revised Estimates).",
                "fact_type": "fiscal_metric",
                "attributes": {"indicator": "fiscal_deficit", "ratio": "5.6% of GDP", "period": "FY24 RE"},
                "evidence_quote": "The fiscal deficit of the Central Government was contained at 5.6 per cent of GDP in FY24 (RE).",
                "page_number": 35,
            },
        ],
    },
    {
        "filename": "02-rbi-annual-report-2024-25-excerpt.pdf",
        "page_count": 100,
        "facts": [
            {
                "fact_text": "Real GDP growth for FY24 was recorded at 8.2%, outperforming peer emerging market economies.",
                "fact_type": "macro_metric",
                "attributes": {"indicator": "real_gdp_growth", "rate": "8.2%", "period": "FY24"},
                "evidence_quote": "Real GDP growth accelerated to 8.2 per cent in 2023-24 from 7.0 per cent in the previous year.",
                "page_number": 28,
            },
            {
                "fact_text": "RBI projects real GDP growth of 7.2% for FY25 supported by rural consumption and capital formation.",
                "fact_type": "macro_projection",
                "attributes": {"indicator": "real_gdp_forecast", "rate": "7.2%", "period": "FY25", "source": "RBI"},
                "evidence_quote": "Real GDP growth for 2024-25 is projected at 7.2 per cent, with Q1 at 7.3 per cent and Q2 at 7.2 per cent.",
                "page_number": 32,
            },
            {
                "fact_text": "RBI projects CPI inflation to ease to 4.5% in FY25, aligning toward the 4% target band.",
                "fact_type": "macro_projection",
                "attributes": {"indicator": "cpi_forecast", "rate": "4.5%", "period": "FY25"},
                "evidence_quote": "CPI inflation for 2024-25 is projected at 4.5 per cent, with Q1 at 4.9 per cent and Q2 at 3.8 per cent.",
                "page_number": 36,
            },
            {
                "fact_text": "Central government gross fiscal deficit is budgeted at 4.9% of GDP for FY25.",
                "fact_type": "fiscal_metric",
                "attributes": {"indicator": "fiscal_deficit_target", "ratio": "4.9% of GDP", "period": "FY25 BE"},
                "evidence_quote": "The Union Budget 2024-25 pegs the fiscal deficit at 4.9 per cent of GDP, reiterating commitment to below 4.5% by FY26.",
                "page_number": 42,
            },
        ],
    },
    {
        "filename": "03-imf-india-2025-article-iv-excerpt.pdf",
        "page_count": 95,
        "facts": [
            {
                "fact_text": "India's real GDP expanded by 8.2% in FY24 following vigorous domestic demand.",
                "fact_type": "macro_metric",
                "attributes": {"indicator": "real_gdp_growth", "rate": "8.2%", "period": "FY24"},
                "evidence_quote": "Real GDP grew by 8.2 percent in FY2023/24, supported by strong public investment.",
                "page_number": 4,
            },
            {
                "fact_text": "IMF Article IV forecasts real GDP growth to moderate to 6.5% in FY25 due to softening cyclical tailwinds.",
                "fact_type": "macro_projection",
                "attributes": {"indicator": "real_gdp_forecast", "rate": "6.5%", "period": "FY25", "source": "IMF"},
                "evidence_quote": "Growth is expected to moderate to 6.5 percent in FY2024/25 as post-pandemic pent-up demand dissipates.",
                "page_number": 6,
            },
            {
                "fact_text": "IMF projects headline inflation to average 4.6% in FY25 before declining to 4.2% in FY26.",
                "fact_type": "macro_projection",
                "attributes": {"indicator": "cpi_forecast", "rate": "4.6%", "period": "FY25"},
                "evidence_quote": "Headline CPI inflation is projected to average 4.6 percent in FY24/25.",
                "page_number": 9,
            },
            {
                "fact_text": "General government overall fiscal deficit projected at 7.9% of GDP for FY25 (combining Centre and States).",
                "fact_type": "fiscal_metric",
                "attributes": {"indicator": "general_government_deficit", "ratio": "7.9% of GDP", "period": "FY25"},
                "evidence_quote": "The general government fiscal deficit (including state governments) is projected at 7.9 percent of GDP in FY24/25.",
                "page_number": 15,
            },
        ],
    },
]

MACRO_RELATIONSHIPS = [
    # ── Corroboration ────────────────────────────────────────────────────────
    (
        0, 0,  # Economic Survey: FY24 GDP 8.2%
        1, 0,  # RBI Report: FY24 GDP 8.2%
        "SUPPORTS",
        "Inter-institutional corroboration: The Ministry of Finance Economic Survey and the Reserve Bank of India independently corroborate FY24 real GDP growth at 8.2%.",
        0.99,
    ),
    (
        1, 0,  # RBI Report: FY24 GDP 8.2%
        2, 0,  # IMF Report: FY24 GDP 8.2%
        "SUPPORTS",
        "Global corroboration: Both the Reserve Bank of India and the IMF Article IV staff report confirm India's FY24 GDP growth rate at 8.2%.",
        0.99,
    ),
    (
        1, 2,  # RBI Report: CPI 4.5% in FY25
        2, 2,  # IMF Report: CPI 4.6% in FY25
        "SUPPORTS",
        "Inflation convergence: RBI (4.5%) and IMF (4.6%) project nearly identical CPI inflation trajectories approaching the 4% target in FY25.",
        0.95,
    ),
    # ── Contradiction ────────────────────────────────────────────────────────
    (
        1, 1,  # RBI Report: Projects FY25 GDP at 7.2%
        2, 1,  # IMF Report: Projects FY25 GDP at 6.5%
        "CONTRADICTS",
        "Divergent macroeconomic forecasts: The Reserve Bank of India projects 7.2% real GDP growth for FY25, in direct contrast with the IMF's significantly more conservative baseline forecast of 6.5% (a 70 bps divergence).",
        0.94,
    ),
    (
        1, 3,  # RBI Report: Central deficit 4.9%
        2, 3,  # IMF Report: General government deficit 7.9%
        "CONTRADICTS",
        "Fiscal scope divergence: RBI cites the Union Budget's 4.9% deficit figure, whereas IMF cites 7.9%, creating an apparent conflict for observers without scope breakdown.",
        0.88,
    ),
    # ── Contextual Reconciliation ────────────────────────────────────────────
    (
        0, 1,  # Economic Survey: 6.5% - 7.0% GDP
        1, 1,  # RBI Report: 7.2% GDP
        "RECONCILES",
        "Reconciled by institutional methodology and timing: The Economic Survey assumed a conservative 6.5–7.0% range ahead of monsoon data, whereas RBI revised its forecast up to 7.2% following strong high-frequency Q1 indicators.",
        0.93,
    ),
    (
        0, 4,  # Economic Survey: FY24 Fiscal Deficit 5.6%
        1, 3,  # RBI Report: FY25 Fiscal Deficit 4.9%
        "RECONCILES",
        "Reconciled by multi-year fiscal consolidation: The reduction from 5.6% to 4.9% represents intentional year-on-year fiscal consolidation from FY24 (RE) to FY25 (BE).",
        0.95,
    ),
    (
        1, 3,  # RBI Central Deficit 4.9%
        2, 3,  # IMF General Deficit 7.9%
        "RECONCILES",
        "Reconciled by accounting scope: RBI cites Central Government deficit alone (4.9%), while IMF reports General Government deficit combining Central (4.9%) and State governments (~3.0%).",
        0.96,
    ),
]


# ── SEEDING EXECUTOR ─────────────────────────────────────────────────────────

def seed_dataset(name: str = "delhivery") -> Dict[str, Any]:
    """Wipe current database and load chosen starter dataset with pre-computed facts & relationships."""
    name = name.lower().strip()
    if name not in ("delhivery", "india-macroeconomy"):
        raise ValueError(f"Unknown dataset '{name}'. Expected 'delhivery' or 'india-macroeconomy'.")

    logger.info("Clearing existing data and seeding '%s' dataset...", name)
    db.clear_all_data()

    dataset_docs = DELHIVERY_DOCS if name == "delhivery" else MACRO_DOCS
    dataset_rels = DELHIVERY_RELATIONSHIPS if name == "delhivery" else MACRO_RELATIONSHIPS

    doc_ids: List[int] = []
    # 2D list to map [doc_index][fact_index] -> inserted fact_id
    fact_id_map: List[List[int]] = []

    for doc_data in dataset_docs:
        doc_id = db.insert_document(doc_data["filename"], doc_data["page_count"])
        db.update_document_status(doc_id, "done")
        doc_ids.append(doc_id)

        inserted_facts_for_doc: List[int] = []
        for f in doc_data["facts"]:
            embedding_blob = embed_text(f["fact_text"])
            fact_id = db.insert_fact(
                document_id=doc_id,
                fact_text=f["fact_text"],
                fact_type=f["fact_type"],
                attributes=f["attributes"],
                evidence_quote=f["evidence_quote"],
                page_number=f["page_number"],
                embedding=embedding_blob,
            )
            inserted_facts_for_doc.append(fact_id)

        fact_id_map.append(inserted_facts_for_doc)

    # Insert relationships
    rel_count = 0
    for doc_idx_a, fact_idx_a, doc_idx_b, fact_idx_b, rel_type, explanation, conf in dataset_rels:
        fact_id_a = fact_id_map[doc_idx_a][fact_idx_a]
        fact_id_b = fact_id_map[doc_idx_b][fact_idx_b]
        id_a, id_b = sorted([fact_id_a, fact_id_b])
        db.insert_relationship(id_a, id_b, rel_type, explanation, conf)
        rel_count += 1

    total_facts = sum(len(doc["facts"]) for doc in dataset_docs)
    logger.info("Seeded '%s': %d docs, %d facts, %d relationships", name, len(doc_ids), total_facts, rel_count)

    return {
        "dataset": name,
        "documents_count": len(doc_ids),
        "facts_count": total_facts,
        "relationships_count": rel_count,
    }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "delhivery"
    res = seed_dataset(target)
    print(json.dumps(res, indent=2))
