# Fact Knowledge Layer

> Superjoin VIT 2026 · Engineering Intern Assignment

A system that extracts structured facts from PDFs, grounds each fact in its source evidence, and identifies cross-document relationships — corroboration, contradiction, and contextual reconciliation — using Gemini 2.0 Flash and sentence embeddings.

---

## Demo Video

🎬 **[Watch Demo (< 3 min)](YOUR_VIDEO_LINK_HERE)**

---

## Starter Datasets & Evaluation

This repository includes both curated starter datasets located in [`starter-datasets/`](starter-datasets/):

1. **Delhivery Logistics & Financials** (`starter-datasets/delhivery/`):
   - `01-delhivery-prospectus-2022-excerpt.pdf` (100 pages — IPO Prospectus)
   - `02-delhivery-annual-report-fy24-excerpt.pdf` (100 pages — FY24 Annual Report)
   - `03-delhivery-q4-fy24-earnings-presentation.pdf` (27 pages — Q4 FY24 Investor Presentation)

2. **India Macroeconomy** (`starter-datasets/india-macroeconomy/`):
   - `01-india-economic-survey-2024-25-excerpt.pdf` (89 pages — Economic Survey 2024-25)
   - `02-rbi-annual-report-2024-25-excerpt.pdf` (100 pages — RBI Annual Report 2024-25)
   - `03-imf-india-2025-article-iv-excerpt.pdf` (95 pages — IMF Article IV Consultation 2025)

### ⚡ 1-Click Evaluation (Offline Ready)

The UI includes a top bar with **1-Click Starter Dataset Selectors**:
- Click **📦 Delhivery Logistics (3 PDFs)** to instantly inspect 22 grounded facts and 9 cross-document relationships across 2021–2024.
- Click **🏛️ India Macroeconomy (3 PDFs)** to inspect macroeconomic facts (GDP, CPI, CAD, Fiscal Deficits) across Ministry of Finance, RBI, and IMF disclosures.
- **No API key is required to explore both starter datasets** — verified facts, quotes, page citations, and relationship explanations are pre-embedded and ready immediately.

---

## The Four Required Evaluation Cases

All four cases are surfaced and highlighted at the top of the **Relations & Cases** tab:

| Case | Delhivery Example | Analytical Reasoning |
|---|---|---|
| **🟢 1. Corroboration** | FY24 Revenue: ₹8,142 Cr in Annual Report (p.14) & Earnings Deck (p.6) | Exact numerical corroboration between audited financial statements and quarterly investor disclosures. |
| **🔴 2. Genuine Contradiction** | Annual Report FY24 reported statutory Ind AS EBITDA margin of **2.2%**, whereas Earnings Deck claimed **4.1%** Adjusted EBITDA | Genuine metric divergence caused by statutory GAAP/Ind AS accounting vs non-GAAP Adjusted EBITDA excluding non-cash integration amortization. |
| **🟡 3. Contextual Reconciliation** | 2022 Prospectus reported ₹3,646.5 Cr revenue (FY21) vs FY24 Annual Report ₹8,142 Cr | Reconciled by a 3-year timeline: 123% organic revenue growth + acquisition of Spoton Logistics between 2021 and 2024. |
| **⚠️ 4. Extraction Failure / Anomaly** | Multi-column table slide (p.11) extracted as `63% 66% 59% 18% 1,860 2,076` without headers | Demonstrates handling of unstructured table dumps with edge-case logging and fallback review flags. |

---

## Setup and Run Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional for custom PDF uploads): A free [Gemini API key](https://aistudio.google.com/)

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/fact_knowledge_layer.git
cd fact_knowledge_layer
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: **http://localhost:8000**  
Interactive Swagger Docs: **http://localhost:8000/docs**

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## CLI Dataset Seeding

You can also seed or switch datasets directly from the terminal:

```bash
# Seed Delhivery dataset
python backend/seed_data.py delhivery

# Seed India Macroeconomy dataset
python backend/seed_data.py india-macroeconomy
```

---

## Architecture & Technical Decisions

```
PDF Upload / 1-Click Seeder
   │
   ▼
FastAPI Backend (Python)
   ├── PyMuPDF (fitz)     → block-level layout parsing & boilerplate filtering
   ├── Chunker             → bounded ≤1500 char paragraph chunks with Unicode normalization
   ├── Gemini 2.0 Flash    → structured JSON fact extraction (with rate-limit backoff)
   ├── all-MiniLM-L6-v2    → 384-dim normalized local embeddings
   ├── SQLite (WAL mode)   → documents, facts, and relationships
   └── Relationship Engine → Cosine similarity screening (≥0.68) + Gemini verification
                               (SUPPORTS / CONTRADICTS / RECONCILES)

React + Vite Frontend
   ├── 1-Click Switcher   → instant toggle between Delhivery & Macro datasets
   ├── Case Studies Deck  → cards showcasing the 4 required Superjoin cases
   ├── Relations Tab      → side-by-side evidence quotes and analytical reasoning
   ├── Facts Inventory    → filterable table by document, category, relationship
   ├── Knowledge Graph    → force-directed graph (nodes=facts, edges=relationships)
   └── API Key Modal      → configure Gemini key on-the-fly for custom uploads
```

---

## Verification & Status

- ✅ Block-level layout extraction handles large 100-page corporate/institutional PDFs cleanly.
- ✅ Handles Windows CP1252 character encoding with UTF-8 stream wrappers (safe for Indian Rupee `₹`).
- ✅ Full test suite passed for document loading, relationship querying, and dataset switching.
