# 🎬 Superjoin Finance — 3-Minute Demo Video Script & Submission Guide

> **Target Duration**: 2 minutes 45 seconds (Under the 3-minute limit)  
> **Tool Recommended**: [Loom](https://www.loom.com) (free, records screen + cam bubble) or OBS Studio.  
> **Screen Resolution**: 1080p (1920×1080) or browser zoom at 100% / 110% for crisp readability.  
> **Preparation**: Have your deployed web app open with the **Delhivery Logistics** starter dataset selected. Also have Excel open or ready to open the downloaded `.xlsx` model.

---

## ⏱️ Video Timeline Breakdown

```
0:00 ─── 0:30   [Hook & Context] Why document fact extraction fails in Finance & Superjoin's mission
0:30 ─── 1:15   [The 4 Required Cases] Corroboration, Contradiction, Reconciliation, Extraction Anomaly
1:15 ─── 1:55   [Interactive Grounding & Knowledge Graph] Verbatim citations & Cytoscape visual network
1:55 ─── 2:30   [Superjoin Differentiator] Native Excel Audit Model (.xlsx) with dynamic formulas
2:30 ─── 2:45   [Production Engineering & Wrap-Up] Multi-Key 429 rotation, 12-factor env, and next steps
```

---

## 🎙️ Step-by-Step Script & Visual Actions

### Part 1: Hook & Core Problem (0:00 – 0:30)
* **Screen**: Deployed Dashboard, highlighting the header: *"Fact Knowledge Layer — Superjoin Finance"*.
* **Action**: Mouse hover over the KPI cards (Documents: 3, Extracted Facts: 22, Cross-Document Links: 9).
* **Say**:
  > *"Hi Superjoin team! In private equity, banking, and FP&A, financial analysts spend hundreds of hours manually cross-referencing numbers across IPO prospectuses, annual reports, and investor decks. But numbers alone are useless without verbatim grounding, formula audit trails, and reconciliation across disclosures.*
  >
  > *Today I've built the **Fact Knowledge Layer** — an end-to-end engine that extracts structured financial facts, computes exact mathematical variances across disclosures, maps inter-document relationships, and exports an audit-ready Excel financial model with dynamic formulas."*

---

### Part 2: The Four Required Evaluation Cases (0:30 – 1:15)
* **Screen**: Click on the **"Relations & Cases"** tab.
* **Action**: Scroll smoothly across the 4 highlighted case cards at the top of the tab.
* **Say**:
  > *"To demonstrate our analytical engine on the official Delhivery starter dataset, we've highlighted the four key evaluation cases right at the top:*
  >
  > 1. *First, **Corroboration**: FY24 Revenue of ₹8,142 Crores appears identically in both the Audited Annual Report on page 14 and the Q4 Earnings Deck on page 6. Our system detects an exact 0.00% variance.*
  > 2. *Second, **Genuine Contradiction**: The Annual Report reports statutory Ind AS EBITDA margin of 2.2%, while the Earnings Deck claims 4.1% Adjusted EBITDA. Our system catches this accounting divergence between statutory GAAP and non-GAAP metrics.*
  > 3. *Third, **Contextual Reconciliation**: The 2022 Prospectus shows ₹3,646 Cr revenue, while FY24 reports ₹8,142 Cr. Rather than flagging a contradiction, our engine reconciles this through a 3-year timeline: 123% organic growth combined with the Spoton Logistics acquisition.*
  > 4. *Fourth, **Extraction Anomaly**: We specifically identify edge cases like dense multi-column tables on slide 11 where numbers lack headers, automatically tagging them for human review."*

---

### Part 3: Evidence Grounding & Knowledge Graph (1:15 – 1:55)
* **Screen**: Click on the **"Facts Inventory"** tab, click on any fact card (e.g. FY24 Revenue), then switch to the **"Knowledge Graph"** tab.
* **Action**: 
  - Click on a fact in the table to open the slide-out **Evidence Grounding Inspector**.
  - Show the verbatim quote and page citation badge.
  - Switch to the **Knowledge Graph** tab and interactively drag a node or filter by "Contradiction".
* **Say**:
  > *"In financial workflows, an AI hallucination is fatal. That's why every single fact is strictly grounded. When I click any fact, our Grounding Inspector displays the exact verbatim evidence quote, the source document filename, the exact page number, and the surrounding contextual paragraph.*
  >
  > *On the **Knowledge Graph** tab, analysts can visualize the cross-document evidence network powered by Cytoscape.js. Green edges show corroborations, red edges show contradictions, and purple edges show temporal reconciliations. It lets analysts spot inconsistencies at a glance across hundreds of filing pages."*

---

### Part 4: Superjoin-Native Excel Audit Model (.xlsx) (1:55 – 2:30)
* **Screen**: Click the **"Download Superjoin Model (.xlsx)"** button in the header.
* **Action**: Open the downloaded Excel file on screen (or show pre-opened Excel window).
* **Say**:
  > *"Because Superjoin lives in spreadsheets, we don't just display results in a web browser. I built a native **Superjoin Excel Model Exporter** using openpyxl.*
  >
  > *With one click, it generates a formatted multi-tab financial model:*
  > - *Tab 1 is an **Executive Variance Matrix** with real, dynamic Excel formulas — like `=C5-B5` — complete with financial accounting formatting and conditional color coding.*
  > - *Tab 2 provides the **Fact Inventory** with canonical metric tags.*
  > - *Tab 3 is the **Reconciliation Audit Trail** providing side-by-side evidence quotes and analytical reasoning.*
  > *An investment associate can immediately hand this spreadsheet to an MD or client."*

---

### Part 5: Production Engineering & Wrap-Up (2:30 – 2:45)
* **Screen**: Click the **"Key Pool"** telemetry badge in the top-right corner to show the live Key Pool Telemetry modal. Also show the **India Macroeconomy** dataset toggle.
* **Action**: Click the India Macroeconomy button to show instant multi-corpus adaptation.
* **Say**:
  > *"Under the hood, we solved all four Brownie Points:*
  > - *Layout-aware block chunking handles 100-page filings without OOM issues.*
  > - *A Multi-Key Round-Robin Provider Pool rotates Gemini API keys with automatic 429 quarantine.*
  > - *And following 12-Factor App methodology, all keys are managed exclusively via environment variables with live hot-reloading.*
  >
  > *The system is live, responsive across all devices, and ready for you to test. Thank you!"*

---

## 🏆 Checklist Before Recording

- [ ] Ensure browser is in **Dark Mode** or standard zoom (100% or 110%).
- [ ] Test audio volume so your voice is crisp and clear.
- [ ] Have the downloaded Excel file ready in your taskbar so you can Alt-Tab into it smoothly without waiting.
- [ ] Keep your mouse movements deliberate and smooth (don't shake or rapidly wiggle the cursor).
- [ ] Keep the video strictly under 3 minutes (2m 30s – 2m 50s is the sweet spot).
- [ ] Upload to **Loom** or **YouTube (Unlisted)** and copy the shareable link.
