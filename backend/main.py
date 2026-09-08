"""
main.py — FastAPI application entry point.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

import database as db
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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(facts.router)
app.include_router(relationships.router)


@app.get("/", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "Fact Knowledge Layer"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
