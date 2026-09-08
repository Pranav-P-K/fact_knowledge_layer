"""
embedder.py — Sentence embedding using all-MiniLM-L6-v2.

The model is loaded once at module import time (lazy singleton) to avoid
repeated disk I/O. Embeddings are 384-dimensional float32 vectors stored
as raw bytes in SQLite.
"""

from __future__ import annotations

import struct
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None
_EMBEDDING_DIM = 384


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> bytes:
    """Return a 384-dim float32 embedding as raw bytes for SQLite BLOB storage."""
    model = _get_model()
    vec: np.ndarray = model.encode(text, normalize_embeddings=True)
    return vec.astype(np.float32).tobytes()


def decode_embedding(blob: bytes) -> np.ndarray:
    """Deserialize a BLOB back to a numpy float32 array."""
    return np.frombuffer(blob, dtype=np.float32)


def cosine_similarity(a: bytes, b: bytes) -> float:
    """Cosine similarity between two stored embedding blobs.
    Because embeddings are L2-normalised, this is just the dot product.
    """
    va = decode_embedding(a)
    vb = decode_embedding(b)
    return float(np.dot(va, vb))
