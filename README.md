# Fact Knowledge Layer

> Superjoin VIT 2026 · Engineering Intern Assignment

A system that extracts structured facts from PDFs, grounds each fact in its source evidence, and identifies cross-document relationships — corroboration, contradiction, and contextual reconciliation — using Gemini 2.0 Flash and sentence embeddings.

---

## Demo Video

🎬 **[Watch Demo (< 3 min)](YOUR_VIDEO_LINK_HERE)**

---

## Setup and Run Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free [Gemini API key](https://aistudio.google.com/)

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/fact_knowledge_layer.git
cd fact_knowledge_layer
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
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

The API will be live at **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

### 3. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Use it

1. Click **Upload** → drag in your PDFs
2. Processing runs in the background (watch the pulsing indicator)
3. Switch to **Facts** to browse extracted facts
4. Switch to **Relations** to see the four required cases with evidence
5. Switch to **Graph** for the interactive force-directed visualization

---

## Approach

### Architecture

```
PDF Upload
   │
   ▼
FastAPI Backend (Python)
   ├── pymupdf          → page-by-page text extraction
   ├── paragraph chunker → ≤1500 char chunks preserving page numbers  
   ├── Gemini 2.0 Flash → structured JSON fact extraction per chunk
   ├── all-MiniLM-L6-v2 → 384-dim normalized embeddings (local, free)
   ├── SQLite           → facts + documents + relationships
   └── Relationship detection (incremental):
         ├── cosine similarity ≥ 0.68 → candidate pairs
         └── Gemini → SUPPORTS / CONTRADICTS / RECONCILES / UNRELATED + explanation

React + Vite Frontend
   ├── Facts tab        → filterable, paginated table
   ├── Relations tab    → the four required cases with side-by-side evidence
   ├── Graph tab        → react-force-graph-2d, node colors per document
   └── FactDetail panel → slide-in with full evidence + all relationships
```

### Key Decisions

| Decision | Rationale |
|---|---|
| **Gemini JSON mode** | Reliable structured output; no manual parsing hacks |
| **Local embeddings (MiniLM)** | Zero cost, fast, 384-dim is enough for semantic similarity screening |
| **Two-stage relationship detection** | Cosine similarity screens candidates cheaply; LLM only runs on likely pairs — keeps API cost low |
| **Dynamic `fact_type`** | LLM infers the category; stored as free-form text + JSON `attributes` → schema evolves naturally with document variety |
| **Incremental processing** | New PDFs are compared against the existing corpus; no rebuild needed |
| **SQLite** | Zero-setup, portable, WAL mode for concurrent reads during background processing |
| **Background tasks** | Upload returns immediately; processing runs async so the UI stays responsive |

### The Four Required Cases

All four emerge automatically from the pipeline — no hardcoding:

| Case | Where to find it |
|---|---|
| **Corroboration** | Relations tab → 🟢 Corroborated section |
| **Genuine contradiction** | Relations tab → 🔴 Contradicted section |
| **Contextual reconciliation** | Relations tab → 🟡 Reconciled section (LLM explains the context) |
| **Extraction failure** | See *Limitations* below |

### AI Tools Used

- **Antigravity (Google DeepMind)** — used as the coding agent to scaffold and build the entire project
- **Gemini 2.0 Flash** — fact extraction and relationship classification at runtime

---

## Limitations and Next Steps

### Current Limitations

1. **Table extraction** — pymupdf often garbles numbers from PDF tables. Complex tables should use a dedicated table parser (camelot, pdfplumber). Currently the system logs the failure and skips the chunk.

2. **Similarity threshold tuning** — the 0.68 cosine threshold was chosen heuristically. Too low → false positive relationships; too high → missed corroborations. A calibration dataset would help.

3. **Large PDFs** — very large PDFs (200+ pages) can take several minutes. The chunking is fast but Gemini API calls add up. A batching + rate-limit strategy would help.

4. **Co-reference resolution** — if a person is called "the Director" in one doc and "Mr. Sharma" in another, semantic embeddings may not catch the link. A NER + entity resolution layer would fix this.

5. **No persistent graph** — the NetworkX graph is rebuilt in-memory for each relationship query. For very large corpora, a graph DB (Neo4j) or cached adjacency list would be faster.

### What I'd Build Next

- **Entity resolution layer** — cluster facts by entity (person, company, place) before relationship detection
- **Confidence thresholds UI** — let users tune the similarity and confidence thresholds interactively
- **PDF annotation viewer** — highlight the evidence quote directly in the PDF using PDF.js
- **Contradiction alerting** — notify when a newly uploaded document contradicts existing facts
- **Streaming extraction** — stream facts to the UI as they're extracted rather than waiting for the whole pipeline
- **Export** — download knowledge graph as JSON-LD or CSV

---

## Additional Notes

- **No credentials in this repo.** The `.env.example` file shows exactly what key is needed. All Gemini calls go through your own API key.
- The system was tested with company filings and regulatory PDFs where financial figures, personnel changes, and addresses provided natural corroboration/contradiction examples.
- The similarity threshold (0.68) and top-K (5) constants in `relationship_detector.py` are easy to tune without touching any other file.
