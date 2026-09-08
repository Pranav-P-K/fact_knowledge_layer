"""
main.py — FastAPI application entry point.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import io
import logging
import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding so Indian Rupee (₹) and unicode dashes don't crash
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

import database as db
from fact_extractor import get_api_key, set_api_key
from routers import documents, facts, relationships

# Initialise database on startup
db.init_db()

app = FastAPI(
    title="Fact Knowledge Layer",
    description="Extract, ground, and relate facts across PDFs.",
    version="1.0.0",
)

# Allow the Vite dev server (port 5173) and production build
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(facts.router)
app.include_router(relationships.router)


class KeyRequest(BaseModel):
    key: str


@app.get("/", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "Fact Knowledge Layer"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/config/status", tags=["config"])
def config_status() -> dict:
    key = get_api_key()
    return {
        "has_api_key": bool(key),
        "active_model": "gemini-2.0-flash",
    }


@app.post("/config/key", tags=["config"])
def update_key(req: KeyRequest) -> dict:
    new_key = req.key.strip()
    if not new_key:
        return {"status": "error", "message": "Key cannot be empty"}

    set_api_key(new_key)

    # Optionally persist to backend/.env
    try:
        env_path = Path(__file__).parent / ".env"
        env_path.write_text(f"GEMINI_API_KEY={new_key}\n", encoding="utf-8")
    except Exception:
        pass

    return {"status": "ok", "message": "API key updated successfully"}
