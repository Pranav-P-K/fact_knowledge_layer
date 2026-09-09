"""
main.py — FastAPI application entry point with Superjoin Excel Exporter and Multi-Key Pool.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import io
import logging
import os
import sys
from pathlib import Path
from typing import List

# Fix Windows console UTF-8 encoding safely
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

import database as db
from excel_exporter import generate_superjoin_excel_model
from fact_extractor import get_api_key, set_api_key
from key_pool import key_pool
from routers import documents, facts, relationships

# Initialise database on startup
db.init_db()

app = FastAPI(
    title="Fact Knowledge Layer — Superjoin Finance",
    description="Extract, ground, and relate facts across PDFs with Excel model export.",
    version="1.2.0",
)

# Allow Vite dev server and any local client
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


class MultiKeyRequest(BaseModel):
    keys: List[str]


@app.get("/", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "Fact Knowledge Layer for Superjoin Finance"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/export/excel", tags=["export"])
def export_excel_model():
    """Generate and download the Superjoin Financial Audit Model (.xlsx)."""
    excel_buf = generate_superjoin_excel_model()
    return Response(
        content=excel_buf.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=superjoin_fact_audit_model.xlsx"
        },
    )


@app.get("/config/status", tags=["config"])
def config_status() -> dict:
    status = key_pool.get_status()
    return {
        "has_api_key": status["healthy_keys"] > 0,
        "total_keys": status["total_keys"],
        "healthy_keys": status["healthy_keys"],
        "active_model": status["active_model"],
    }


@app.get("/config/keys", tags=["config"])
def get_key_pool_status() -> dict:
    """Inspect detailed key health, request counts, and quarantine status."""
    return key_pool.get_status()


@app.post("/config/reload", tags=["config"])
def reload_keys_from_env() -> dict:
    """Hot reload key pool directly from backend/.env without restarting server."""
    return key_pool.reload_from_env()

