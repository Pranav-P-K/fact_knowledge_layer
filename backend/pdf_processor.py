"""
pdf_processor.py — Extract text from PDF pages using pymupdf.

Returns a list of chunks, each containing:
  - page_number (1-indexed)
  - text (raw extracted text for that page)

Large pages are further split at paragraph boundaries to keep chunks
under ~1500 characters, which fits comfortably in a single LLM prompt call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

import fitz  # pymupdf


MAX_CHUNK_CHARS = 1500


@dataclass
class TextChunk:
    page_number: int
    text: str


def extract_chunks(pdf_bytes: bytes) -> tuple[List[TextChunk], int]:
    """
    Open a PDF from bytes and return (chunks, page_count).
    Each chunk is at most MAX_CHUNK_CHARS characters.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    chunks: List[TextChunk] = []

    for page_index in range(page_count):
        page = doc[page_index]
        raw_text = page.get_text("text").strip()
        if not raw_text:
            continue

        page_number = page_index + 1  # 1-indexed

        # Split at double-newlines (paragraph boundaries)
        paragraphs = re.split(r"\n{2,}", raw_text)

        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph would exceed the limit, flush
            if current_chunk and len(current_chunk) + len(para) + 2 > MAX_CHUNK_CHARS:
                chunks.append(TextChunk(page_number=page_number, text=current_chunk.strip()))
                current_chunk = para
            else:
                current_chunk = (current_chunk + "\n\n" + para) if current_chunk else para

        if current_chunk.strip():
            chunks.append(TextChunk(page_number=page_number, text=current_chunk.strip()))

    doc.close()
    return chunks, page_count
