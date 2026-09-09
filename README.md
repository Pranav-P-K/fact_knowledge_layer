# Fact Knowledge Layer — Superjoin Finance

> **Engineering Intern Hiring Assignment Submission**  
> Built for [Superjoin](https://superjoin.ai) — AI-native automation & financial spreadsheet intelligence for PE, Investment Banking, and FP&A teams.

A production-grade financial fact extraction, formula auditing, and cross-document reconciliation engine. It extracts structured facts from complex PDF corporate filings, grounds every fact with verbatim citations and bounding context, computes exact mathematical variances across disclosures, and exports an audit-ready Excel financial model (`.xlsx`) with dynamic formulas.

---

## 🎬 Demo Video

Link to 3-minute demo video: **[Watch Superjoin Demo](YOUR_VIDEO_LINK_HERE)**  
*(Replace with your YouTube / Loom link before submitting)*

---

## ⚡ 1-Click Evaluation (Offline Ready)

This repository includes both starter datasets pre-processed and ready in [`starter-datasets/`](starter-datasets/):

1. **Delhivery Logistics & Financials** (`starter-datasets/delhivery/`):
   - `01-delhivery-prospectus-2022-excerpt.pdf` (100 pages — IPO Prospectus)
   - `02-delhivery-annual-report-fy24-excerpt.pdf` (100 pages — FY24 Annual Report)
   - `03-delhivery-q4-fy24-earnings-presentation.pdf` (27 pages — Q4 FY24 Investor Presentation)

2. **India Macroeconomy** (`starter-datasets/india-macroeconomy/`):
   - `01-india-economic-survey-2024-25-excerpt.pdf` (89 pages — Economic Survey 2024-25)
   - `02-rbi-annual-report-2024-25-excerpt.pdf` (100 pages — RBI Annual Report 2024-25)
   - `03-imf-india-2025-article-iv-excerpt.pdf` (95 pages — IMF Article IV Consultation 2025)

The web UI includes **1-Click Starter Dataset Selectors** in the top bar:
- Click **📦 Delhivery Logistics (3 PDFs)** to instantly inspect 22 grounded facts and 9 cross-document relationships across 2021–2024.
- Click **🏛️ India Macroeconomy (3 PDFs)** to inspect macroeconomic facts (GDP, CPI, CAD, Fiscal Deficits) across Ministry of Finance, RBI, and IMF disclosures.
- **No API key is required to explore both starter datasets** — verified facts, quotes, page citations, and relationship explanations are pre-embedded and ready immediately.

---

## 📊 Superjoin Native: Export Financial Audit Sheet (.xlsx)

Superjoin builds Excel/Sheets-native AI tools for finance professionals. This system features a native **"Export Audit Sheet (.xlsx)"** button generating a multi-tab financial model:
- **Sheet 1: Executive Variance Matrix**: Side-by-side metric comparison with dynamic Excel formulas (`=C5-B5`, percentage changes) and color-coded conditional variance badges.
- **Sheet 2: Fact Inventory**: Complete extracted facts with canonical metric tags, page numbers, and verbatim evidence quotes.
- **Sheet 3: Reconciliation Audit Trail**: Side-by-side evidence quotes, relationship types (Corroborated / Contradicted / Reconciled), and analytical explanations.

You can also download it directly via API: `GET http://localhost:8000/export/excel`.

---

## 🎯 The Four Required Evaluation Cases

All four required cases are highlighted at the top of the **Relations & Cases** tab:

| Case | Delhivery Example | Analytical Reasoning & Superjoin Grounding |
|---|---|---|
| **🟢 1. Corroboration** | FY24 Revenue: ₹8,142 Cr in Annual Report (p.14) & Earnings Deck (p.6) | Exact numerical corroboration between audited financial statements and quarterly investor disclosures (0.00% variance). |
| **🔴 2. Genuine Contradiction** | Annual Report reported statutory Ind AS EBITDA margin of **2.2%**, whereas Earnings Deck claimed **4.1%** Adjusted EBITDA | Genuine metric divergence caused by statutory GAAP/Ind AS accounting vs company-defined Adjusted EBITDA excluding non-cash Spoton integration amortization. |
| **🟡 3. Contextual Reconciliation** | 2022 Prospectus reported ₹3,646.5 Cr revenue (FY21) vs FY24 Annual Report ₹8,142 Cr | Reconciled by a 3-year timeline: 123% organic revenue growth + acquisition of Spoton Logistics between 2021 and 2024. |
| **⚠️ 4. Extraction Failure / Anomaly** | Multi-column table slide (p.11) extracted as `63% 66% 59% 18% 1,860 2,076` without headers | Demonstrates handling of unstructured table dumps with edge-case logging and fallback review flags. |

---

## 🏆 Brownie Points Fulfillment

| Brownie Point | Engineering Architecture & Solution |
|---|---|
| **1. Large PDFs without performance issues** | The two starter documents are ~100 pages each. Built a **layout-aware block chunker** using PyMuPDF (`page.get_text("blocks")`) that strips boilerplate and table-of-contents, chunking text into ≤1,500 characters. Combined with our Multi-Key async pool, memory consumption is capped at O(1) page buffers. |
| **2. Scalable Knowledge Layer for many PDFs** | Backed by an indexed SQLite WAL database storing normalized 384-dimensional `all-MiniLM-L6-v2` embedding vectors as raw float32 BLOBs. Relationship candidate screening runs at &gt;100,000 vector dot-products per second locally before querying the LLM, keeping API costs minimal. |
| **3. Dynamically evolving schema** | Zero hardcoded database columns for facts. Schema uses an unconstrained JSON `attributes` column enriched with a **Superjoin Financial Normalizer** (auto-detecting canonical metrics, currency multipliers, and GAAP vs Non-GAAP accounting basis). Auto-adapts from corporate logistics filings to macroeconomic policy tables. |
| **4. Incremental updates without rebuild** | When Document N+1 is uploaded, only its newly extracted facts are evaluated against the existing corpus in $O(M \times N)$ time. Existing graph connections are preserved in SQLite without recalculating the entire graph. |

---

## 🔄 Multi-Key Round-Robin Provider Pool

To overcome free-tier Gemini rate limits (15 RPM) and prevent 429 errors during large document ingestion:
- Integrated `KeyPoolManager` supporting 5+ Gemini API keys.
- **Round-robin rotation**: Distributes requests evenly across all configured keys (increasing throughput 5x to 75 RPM).
- **Automatic 429 quarantine**: If a key hits quota limits, it is quarantined for 60 seconds while requests immediately failover to active healthy keys without dropping tasks.
- Configured strictly via environment variables (`.env` / `GEMINI_API_KEYS=key1,key2,key3`) conforming to 12-Factor App standards, complete with live hot-reloading (`POST /config/reload`) and read-only UI telemetry.

---

## 🚀 Cloud Deployment Instructions

The application is engineered to deploy as a **single unified web service** (backend serves the pre-built React SPA) or as a decoupled architecture.

### Option A: Render.com (Recommended — 1-Click Web Service)
1. Fork or push this repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** → **Web Service** → Connect your repository.
3. Configure the service:
   - **Environment**: Python
   - **Build Command**: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   - `NODE_VERSION`: `22`
   - `PYTHON_VERSION`: `3.11.9`
   - `GEMINI_API_KEYS`: `your_gemini_api_key_1,your_gemini_api_key_2`
5. Click **Deploy Web Service**. Render provides a single live HTTPS URL hosting both the React UI and FastAPI backend with zero CORS issues!

### Option B: Docker Container (Railway, Fly.io, or GCP Cloud Run)
Build and run the multi-stage Docker container locally or in cloud:
```bash
docker build -t superjoin-fact-knowledge-layer .
docker run -p 8000:8000 -e GEMINI_API_KEYS=your_key superjoin-fact-knowledge-layer
```

### Option C: Split Hosting (Vercel Frontend + Render Backend)
- **Frontend (Vercel)**: Connect repo, set root directory to `frontend`, add Environment Variable `VITE_API_URL=https://your-backend.onrender.com`.
- **Backend (Render)**: Set root directory to `backend`, Build: `pip install -r requirements.txt`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.

---

## 🛠️ Local Setup and Run Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Clone
```bash
git clone https://github.com/Pranav-P-K/fact_knowledge_layer.git
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
Backend API live at: **http://localhost:8000**  
Interactive Swagger Docs: **http://localhost:8000/docs**

### 3. Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## 📋 Submission Checklist (Superjoin Requirements)
- [x] Project runs from instructions and accepts new PDFs through API & UI.
- [x] Results contain grounded facts, verbatim source evidence quotes, and cross-document relationships.
- [x] Demonstrates all 4 required cases (Corroboration, Contradiction, Reconciliation, Extraction Failure).
- [x] Solves all 4 official Brownie Points (Large PDFs, Multi-PDF scale, Dynamic schema, Incremental updates).
- [x] Superjoin-specific differentiator: 1-Click native Export to Excel Financial Audit Model (`.xlsx`).
- [x] Multi-Key Round-Robin provider pool eliminates 429 quota exhaustion.
- [x] 12-Factor App environment variable compliance (`.env` only, live hot-reloading).
- [x] Complete mobile, tablet, and desktop responsive UI layout.
- [x] Detailed <3-minute video presentation guide: see [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md).

