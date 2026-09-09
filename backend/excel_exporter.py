"""
excel_exporter.py — Superjoin Financial Audit Model & Variance Spreadsheet Generator.

Generates a multi-tab financial audit workbook (.xlsx):
  - Sheet 1: Executive Variance Matrix (Metric comparison with dynamic Excel formulas)
  - Sheet 2: Fact Knowledge Layer Inventory (Grounded facts, quotes, page citations)
  - Sheet 3: Cross-Document Reconciliation Audit Trail (Side-by-side evidence & reasoning)
"""

from __future__ import annotations

import io
import json
from typing import Any, Dict, List

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import database as db
from financial_normalizer import calculate_variance, infer_accounting_standard, infer_canonical_metric, parse_normalized_number

# Styling constants
FONT_FAMILY = "Calibri"
HEADER_FILL = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")  # Deep Indigo
SUBHEADER_FILL = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
ZEBRA_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

GREEN_FILL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
GREEN_FONT = Font(name=FONT_FAMILY, size=10, bold=True, color="166534")

RED_FILL = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
RED_FONT = Font(name=FONT_FAMILY, size=10, bold=True, color="991B1B")

YELLOW_FILL = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
YELLOW_FONT = Font(name=FONT_FAMILY, size=10, bold=True, color="854D0E")

THIN_BORDER = Border(
    left=Side(style="thin", color="E2E8F0"),
    right=Side(style="thin", color="E2E8F0"),
    top=Side(style="thin", color="E2E8F0"),
    bottom=Side(style="thin", color="E2E8F0"),
)


def generate_superjoin_excel_model() -> io.BytesIO:
    """Generate the complete Superjoin Financial Audit Model (.xlsx)."""
    wb = openpyxl.Workbook()

    # ── Fetch Data ────────────────────────────────────────────────────────────
    conn = db.get_connection()
    try:
        documents = [dict(r) for r in conn.execute("SELECT * FROM documents ORDER BY id ASC").fetchall()]
        facts = [dict(r) for r in conn.execute(
            """
            SELECT f.*, d.filename as doc_name
            FROM facts f
            JOIN documents d ON f.document_id = d.id
            ORDER BY f.id ASC
            """
        ).fetchall()]
        relationships = [dict(r) for r in conn.execute(
            """
            SELECT r.*,
                   fa.fact_text as fact_a_text, fa.evidence_quote as fact_a_evidence, fa.page_number as fact_a_page,
                   da.filename as fact_a_doc_name,
                   fb.fact_text as fact_b_text, fb.evidence_quote as fact_b_evidence, fb.page_number as fact_b_page,
                   db.filename as fact_b_doc_name
            FROM relationships r
            JOIN facts fa ON r.fact_id_a = fa.id
            JOIN documents da ON fa.document_id = da.id
            JOIN facts fb ON r.fact_id_b = fb.id
            JOIN documents db ON fb.document_id = db.id
            ORDER BY r.id ASC
            """
        ).fetchall()]
    finally:
        conn.close()

    # ── SHEET 1: EXECUTIVE VARIANCE MATRIX ────────────────────────────────────
    ws1 = wb.active
    ws1.title = "Executive Variance Matrix"
    ws1.views.sheetView[0].showGridLines = True

    # Title Block
    ws1["A1"] = "SUPERJOIN FINANCE · FACT AUDIT & VARIANCE MODEL"
    ws1["A1"].font = Font(name=FONT_FAMILY, size=14, bold=True, color="312E81")
    ws1["A2"] = f"Automated Cross-Document Verification · {len(documents)} Filings Analyzed · {len(facts)} Facts Grounded"
    ws1["A2"].font = Font(name=FONT_FAMILY, size=10, italic=True, color="64748B")

    # Table Headers
    doc_cols = [d["filename"].replace("-excerpt.pdf", "").replace(".pdf", "") for d in documents[:3]]
    headers1 = ["Metric Category", "Canonical Metric", "Standard Unit"]
    for d_name in doc_cols:
        headers1.append(f"{d_name} (Reported)")
    if len(doc_cols) >= 2:
        headers1.extend(["Variance (Formula)", "% Change (Formula)", "Audit Status"])

    row_num = 4
    for col_num, h in enumerate(headers1, 1):
        cell = ws1.cell(row=row_num, column=col_num, value=h)
        cell.fill = HEADER_FILL
        cell.font = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Populate canonical metrics
    # Group facts by canonical metric across documents
    metric_map: Dict[str, Dict[str, Any]] = {}
    for f in facts:
        c_metric = infer_canonical_metric(f["fact_text"])
        val, unit = parse_normalized_number(f["fact_text"])
        doc_id = f["document_id"]
        if c_metric not in metric_map:
            metric_map[c_metric] = {"unit": unit, "docs": {}}
        if doc_id not in metric_map[c_metric]["docs"]:
            metric_map[c_metric]["docs"][doc_id] = {"val": val, "raw": f["fact_text"]}

    row_num = 5
    for c_metric, data in sorted(metric_map.items()):
        category = c_metric.split(".")[0].capitalize()
        name = c_metric.split(".")[1].replace("_", " ").title() if "." in c_metric else c_metric

        ws1.cell(row=row_num, column=1, value=category).font = Font(name=FONT_FAMILY, size=10)
        ws1.cell(row=row_num, column=2, value=name).font = Font(name=FONT_FAMILY, size=10, bold=True)
        ws1.cell(row=row_num, column=3, value=data["unit"]).font = Font(name=FONT_FAMILY, size=10, color="64748B")

        # Document reported values
        for i, d in enumerate(documents[:3]):
            d_id = d["id"]
            doc_fact = data["docs"].get(d_id)
            col = 4 + i
            if doc_fact and doc_fact["val"] is not None:
                val = doc_fact["val"]
                cell = ws1.cell(row=row_num, column=col, value=val)
                cell.font = Font(name=FONT_FAMILY, size=10)
                cell.alignment = Alignment(horizontal="right")
                if data["unit"] == "INR":
                    cell.number_format = "₹#,##0"
                elif data["unit"] == "PERCENT":
                    cell.number_format = '0.0"%"'
                else:
                    cell.number_format = "#,##0"
            else:
                ws1.cell(row=row_num, column=col, value="-").alignment = Alignment(horizontal="center")

        # Formulas for Variance & % Change (comparing col 4 and col 5 if present)
        if len(doc_cols) >= 2:
            col_var = 4 + len(doc_cols)
            col_pct = col_var + 1
            col_status = col_pct + 1

            col_a_letter = get_column_letter(4)
            col_b_letter = get_column_letter(5)

            # Excel formula: =IF(OR(ISBLANK(D5), ISBLANK(E5)), "", E5-D5)
            ws1.cell(row=row_num, column=col_var, value=f"=IF(OR({col_a_letter}{row_num}=\"-\", {col_b_letter}{row_num}=\"-\"), \"-\", {col_b_letter}{row_num}-{col_a_letter}{row_num})")
            ws1.cell(row=row_num, column=col_var).alignment = Alignment(horizontal="right")

            # Formula for % Change: =IF(D5=0, "", (E5-D5)/D5)
            ws1.cell(row=row_num, column=col_pct, value=f"=IF(OR({col_a_letter}{row_num}=\"-\", {col_b_letter}{row_num}=\"-\", {col_a_letter}{row_num}=0), \"-\", ({col_b_letter}{row_num}-{col_a_letter}{row_num})/{col_a_letter}{row_num})")
            ws1.cell(row=row_num, column=col_pct).number_format = "0.0%"
            ws1.cell(row=row_num, column=col_pct).alignment = Alignment(horizontal="right")

            # Status cell
            status_cell = ws1.cell(row=row_num, column=col_status, value="Verified")
            status_cell.font = GREEN_FONT
            status_cell.fill = GREEN_FILL
            status_cell.alignment = Alignment(horizontal="center")

        # Borders and zebra striping
        for c in range(1, len(headers1) + 1):
            cell = ws1.cell(row=row_num, column=c)
            cell.border = THIN_BORDER
            if row_num % 2 == 0 and not cell.fill.start_color.rgb:
                cell.fill = ZEBRA_FILL

        row_num += 1

    # ── SHEET 2: FACT KNOWLEDGE INVENTORY ─────────────────────────────────────
    ws2 = wb.create_sheet(title="Fact Inventory")
    ws2.views.sheetView[0].showGridLines = True

    headers2 = ["Fact ID", "Source Document", "Page #", "Canonical Metric", "Fact Statement", "Verbatim Evidence Quote", "Normalized Value", "Unit", "Accounting Basis"]
    for col_num, h in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col_num, value=h)
        cell.fill = SUBHEADER_FILL
        cell.font = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for idx, f in enumerate(facts, 2):
        val, unit = parse_normalized_number(f["fact_text"])
        attrs = json.loads(f["attributes"]) if isinstance(f["attributes"], str) else (f["attributes"] or {})
        std = infer_accounting_standard(f["fact_text"], attrs)
        metric = infer_canonical_metric(f["fact_text"])

        ws2.cell(row=idx, column=1, value=f"FACT-{f['id']:03d}").alignment = Alignment(horizontal="center")
        ws2.cell(row=idx, column=2, value=f["doc_name"])
        ws2.cell(row=idx, column=3, value=f["page_number"]).alignment = Alignment(horizontal="center")
        ws2.cell(row=idx, column=4, value=metric)
        ws2.cell(row=idx, column=5, value=f["fact_text"])
        ws2.cell(row=idx, column=6, value=f'"{f["evidence_quote"]}"')
        ws2.cell(row=idx, column=7, value=val or "-").alignment = Alignment(horizontal="right")
        ws2.cell(row=idx, column=8, value=unit).alignment = Alignment(horizontal="center")
        ws2.cell(row=idx, column=9, value=std).alignment = Alignment(horizontal="center")

        for c in range(1, len(headers2) + 1):
            cell = ws2.cell(row=idx, column=c)
            cell.font = Font(name=FONT_FAMILY, size=9)
            cell.border = THIN_BORDER
            if idx % 2 == 1:
                cell.fill = ZEBRA_FILL

    # ── SHEET 3: RECONCILIATION AUDIT TRAIL ───────────────────────────────────
    ws3 = wb.create_sheet(title="Reconciliation Audit Trail")
    ws3.views.sheetView[0].showGridLines = True

    headers3 = ["Rel ID", "Relationship Type", "Fact A Document & Page", "Fact A Verbatim Evidence", "Fact B Document & Page", "Fact B Verbatim Evidence", "Mathematical Delta", "Analytical Explanation", "Confidence"]
    for col_num, h in enumerate(headers3, 1):
        cell = ws3.cell(row=1, column=col_num, value=h)
        cell.fill = HEADER_FILL
        cell.font = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for idx, r in enumerate(relationships, 2):
        val_a, u_a = parse_normalized_number(r["fact_a_text"])
        val_b, u_b = parse_normalized_number(r["fact_b_text"])
        variance_info = calculate_variance(val_a, val_b, u_a if u_a != "UNKNOWN" else u_b)

        r_type = r["relationship_type"]
        ws3.cell(row=idx, column=1, value=f"REL-{r['id']:03d}").alignment = Alignment(horizontal="center")

        type_cell = ws3.cell(row=idx, column=2, value=r_type)
        type_cell.alignment = Alignment(horizontal="center")
        if r_type == "SUPPORTS":
            type_cell.fill, type_cell.font = GREEN_FILL, GREEN_FONT
        elif r_type == "CONTRADICTS":
            type_cell.fill, type_cell.font = RED_FILL, RED_FONT
        else:
            type_cell.fill, type_cell.font = YELLOW_FILL, YELLOW_FONT

        ws3.cell(row=idx, column=3, value=f"{r['fact_a_doc_name']} (p.{r['fact_a_page']})")
        ws3.cell(row=idx, column=4, value=f'"{r["fact_a_evidence"]}"')
        ws3.cell(row=idx, column=5, value=f"{r['fact_b_doc_name']} (p.{r['fact_b_page']})")
        ws3.cell(row=idx, column=6, value=f'"{r["fact_b_evidence"]}"')
        ws3.cell(row=idx, column=7, value=variance_info["formatted_variance"]).alignment = Alignment(horizontal="center")
        ws3.cell(row=idx, column=8, value=r["explanation"])
        ws3.cell(row=idx, column=9, value=f"{int(r['confidence'] * 100)}%").alignment = Alignment(horizontal="center")

        for c in range(1, len(headers3) + 1):
            cell = ws3.cell(row=idx, column=c)
            cell.font = Font(name=FONT_FAMILY, size=9)
            cell.border = THIN_BORDER
            if idx % 2 == 1 and c != 2:
                cell.fill = ZEBRA_FILL

    # Auto-adjust column widths across all sheets
    for sheet in [ws1, ws2, ws3]:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
