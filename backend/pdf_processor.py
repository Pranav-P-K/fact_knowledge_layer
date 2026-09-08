"""
pdf_processor.py — Extract and chunk text from PDF pages using PyMuPDF blocks.

Key improvements:
  - Uses block-level layout extraction (`page.get_text("blocks")`) to reliably
    detect paragraphs and avoid PyMuPDF's single-newline fragmentation.
  - Normalizes unicode characters (Indian Rupee, en-dashes, curly quotes).
  - Skips boilerplate (bare page numbers, repetitive headers, blank blocks).
  - Assembles coherent chunks bounded by MAX_CHUNK_CHARS (~1500 chars).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

import fitz  # pymupdf

MAX_CHUNK_CHARS = 1500
MIN_CHUNK_CHARS = 40

# Boilerplate patterns to exclude
BOILERPLATE_REGEXES = [
    re.compile(r"^\s*page\s+\d+(\s+of\s+\d+)?\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+\s*$"),  # bare numbers
    re.compile(r"^\s*table\s+of\s+contents\s*$", re.IGNORECASE),
    re.compile(r"^\s*this\s+page\s+(has\s+been\s+)?intentionally\s+left\s+blank\s*$", re.IGNORECASE),
]


@dataclass
class TextChunk:
    page_number: int
    text: str


def clean_text(text: str) -> str:
    """Normalize unicode, whitespace, and currency artifacts."""
    if not text:
        return ""

    # Replace unicode replacement characters
    text = text.replace("\ufffd", " ")

    # Normalize various dashes to standard dash
    text = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", text)

    # Normalize quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')

    # Normalize multiple whitespace within lines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    # Reconnect broken line wraps if line didn't end with punctuation
    cleaned_paragraphs = []
    current_p = []

    for line in lines:
        if not line:
            if current_p:
                cleaned_paragraphs.append(" ".join(current_p))
                current_p = []
            continue
        current_p.append(line)

    if current_p:
        cleaned_paragraphs.append(" ".join(current_p))

    return "\n\n".join(cleaned_paragraphs).strip()


def is_boilerplate(text: str) -> bool:
    """Check if block is low-value boilerplate or page number."""
    stripped = text.strip()
    if len(stripped) < 10:
        for r in BOILERPLATE_REGEXES:
            if r.match(stripped):
                return True
    return False


def extract_chunks(pdf_bytes: bytes) -> Tuple[List[TextChunk], int]:
    """
    Open a PDF from bytes and return (chunks, page_count).
    Each chunk is at most MAX_CHUNK_CHARS characters.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    chunks: List[TextChunk] = []

    for page_index in range(page_count):
        page = doc[page_index]
        page_number = page_index + 1  # 1-indexed

        blocks = page.get_text("blocks")
        if not blocks:
            continue

        page_paragraphs: List[str] = []
        for b in blocks:
            # b[6] == 0 means text block (1 is image)
            if len(b) > 6 and b[6] != 0:
                continue

            block_text = clean_text(b[4])
            if not block_text or is_boilerplate(block_text):
                continue
            page_paragraphs.append(block_text)

        # Assemble chunks for this page
        current_chunk = ""
        for para in page_paragraphs:
            # If paragraph itself is too large, split by sentences
            if len(para) > MAX_CHUNK_CHARS:
                sentences = re.split(r"(?<=[.?!])\s+", para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if current_chunk and len(current_chunk) + len(sent) + 1 > MAX_CHUNK_CHARS:
                        if len(current_chunk) >= MIN_CHUNK_CHARS:
                            chunks.append(TextChunk(page_number=page_number, text=current_chunk))
                        current_chunk = sent
                    else:
                        current_chunk = (current_chunk + " " + sent) if current_chunk else sent
                continue

            if current_chunk and len(current_chunk) + len(para) + 2 > MAX_CHUNK_CHARS:
                if len(current_chunk) >= MIN_CHUNK_CHARS:
                    chunks.append(TextChunk(page_number=page_number, text=current_chunk))
                current_chunk = para
            else:
                current_chunk = (current_chunk + "\n\n" + para) if current_chunk else para

        if current_chunk.strip() and len(current_chunk.strip()) >= MIN_CHUNK_CHARS:
            chunks.append(TextChunk(page_number=page_number, text=current_chunk.strip()))

    doc.close()
    return chunks, page_count
