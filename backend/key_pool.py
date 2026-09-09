"""
key_pool.py — Resilient Multi-Key Round-Robin & Quota Quarantine Provider Pool.

Manages multiple Gemini API keys:
  - Round-robin key rotation across requests
  - Automatic quarantine on HTTP 429 / ResourceExhausted (60-second cooldown)
  - Automatic fallback to next active key
  - Dynamic key pool inspection & runtime updates
  - Zero downtime across multiple free-tier keys
"""

from __future__ import annotations

import logging
import os
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-3.5-flash-lite"


@dataclass
class KeyEntry:
    key: str
    quarantined_until: float = 0.0
    requests_count: int = 0
    errors_count: int = 0
    last_used: float = 0.0

    @property
    def is_quarantined(self) -> bool:
        return time.time() < self.quarantined_until

    @property
    def masked_key(self) -> str:
        if len(self.key) <= 8:
            return "****"
        return f"{self.key[:4]}...{self.key[-4:]}"


class KeyPoolManager:
    """Thread-safe multi-key rotation and rate-limit quarantine manager."""

    def __init__(self):
        self._lock = threading.Lock()
        self._keys: List[KeyEntry] = []
        self._current_index = 0
        self._models_cache: Dict[str, genai.GenerativeModel] = {}
        self._load_keys_from_env()

    def _load_keys_from_env(self) -> None:
        """Load keys exclusively from environment variables / backend/.env."""
        # Force reload .env from disk to capture any updates
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        else:
            load_dotenv(override=True)

        key_list: List[str] = []

        # 1. Comma/newline-separated list
        raw_keys = os.environ.get("GEMINI_API_KEYS", "").strip()
        if raw_keys:
            for k in re.split(r"[,;\n]+", raw_keys):
                cleaned = k.strip().strip("'\"")
                if cleaned and cleaned not in key_list:
                    key_list.append(cleaned)

        # 2. Numbered variables: GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...
        for i in range(1, 11):
            var_key = os.environ.get(f"GEMINI_API_KEY_{i}", "").strip().strip("'\"")
            if var_key and var_key not in key_list:
                key_list.append(var_key)

        # 3. Single variable: GEMINI_API_KEY
        single_key = os.environ.get("GEMINI_API_KEY", "").strip().strip("'\"")
        if single_key and single_key not in key_list:
            key_list.append(single_key)

        # Filter out placeholders
        valid_keys = [
            k for k in key_list
            if k and k.lower() not in ("placeholder", "your_gemini_api_key_here", "your_key_here", "none")
        ]

        with self._lock:
            self._keys = [KeyEntry(key=k) for k in valid_keys]
            self._current_index = 0
            self._models_cache.clear()

        logger.info("KeyPoolManager loaded %d active key(s) from .env.", len(self._keys))

    def reload_from_env(self) -> Dict[str, Any]:
        """Hot-reload key pool from .env without restarting server."""
        self._load_keys_from_env()
        return self.get_status()


    def get_status(self) -> Dict[str, Any]:
        """Return pool status and per-key health metrics."""
        now = time.time()
        with self._lock:
            key_metrics = []
            active_count = 0
            for i, entry in enumerate(self._keys):
                is_quar = entry.is_quarantined
                if not is_quar:
                    active_count += 1
                key_metrics.append({
                    "index": i + 1,
                    "masked_key": entry.masked_key,
                    "is_active": not is_quar,
                    "quarantined_seconds_left": max(0, int(entry.quarantined_until - now)) if is_quar else 0,
                    "requests_count": entry.requests_count,
                    "errors_count": entry.errors_count,
                })

            return {
                "total_keys": len(self._keys),
                "healthy_keys": active_count,
                "active_model": DEFAULT_MODEL,
                "keys": key_metrics,
            }

    def set_keys(self, new_keys: List[str]) -> None:
        """Replace the key pool with a new list of keys and persist to .env."""
        cleaned = [
            k.strip() for k in new_keys
            if k.strip() and k.strip().lower() not in ("placeholder", "your_gemini_api_key_here")
        ]

        with self._lock:
            self._keys = [KeyEntry(key=k) for k in cleaned]
            self._current_index = 0
            self._models_cache.clear()

        # Persist to .env
        try:
            env_path = Path(__file__).parent / ".env"
            keys_str = ",".join(cleaned)
            env_path.write_text(f"GEMINI_API_KEYS={keys_str}\nGEMINI_API_KEY={cleaned[0] if cleaned else ''}\n", encoding="utf-8")
        except Exception as e:
            logger.warning("Could not persist keys to .env: %s", e)

        logger.info("KeyPoolManager updated: %d active key(s).", len(cleaned))

    def acquire_client(self, model_name: str = DEFAULT_MODEL) -> Tuple[Optional[genai.GenerativeModel], Optional[str]]:
        """
        Get the next available GenerativeModel and its associated key.
        Returns (model, key_string) or (None, None) if no keys are available.
        """
        with self._lock:
            if not self._keys:
                return None, None

            now = time.time()
            n = len(self._keys)

            # Round-robin search for a non-quarantined key
            for _ in range(n):
                idx = self._current_index % n
                self._current_index += 1
                entry = self._keys[idx]

                if not entry.is_quarantined:
                    entry.last_used = now
                    entry.requests_count += 1
                    model = self._get_or_create_model(entry.key, model_name)
                    return model, entry.key

            # If all are quarantined, choose the one with the lowest quarantine expiry
            min_quar_entry = min(self._keys, key=lambda k: k.quarantined_until)
            wait_time = max(0.0, min_quar_entry.quarantined_until - now)
            if wait_time > 0 and wait_time < 5.0:
                time.sleep(wait_time)
                min_quar_entry.quarantined_until = 0.0
                min_quar_entry.last_used = time.time()
                min_quar_entry.requests_count += 1
                model = self._get_or_create_model(min_quar_entry.key, model_name)
                return model, min_quar_entry.key

            logger.warning("All %d Gemini API keys are currently rate-limited.", len(self._keys))
            return None, None

    def _get_or_create_model(self, key: str, model_name: str) -> genai.GenerativeModel:
        cache_key = f"{key}_{model_name}"
        if cache_key in self._models_cache:
            return self._models_cache[cache_key]

        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        self._models_cache[cache_key] = model
        return model

    def report_429(self, key: str, cooldown_seconds: float = 60.0) -> None:
        """Quarantine a key that triggered HTTP 429 / ResourceExhausted."""
        with self._lock:
            for entry in self._keys:
                if entry.key == key:
                    entry.quarantined_until = time.time() + cooldown_seconds
                    entry.errors_count += 1
                    logger.warning(
                        "Key %s hit rate limit. Quarantined for %.0fs. Errors: %d",
                        entry.masked_key, cooldown_seconds, entry.errors_count,
                    )
                    break

    def report_error(self, key: str) -> None:
        with self._lock:
            for entry in self._keys:
                if entry.key == key:
                    entry.errors_count += 1
                    break


# Global singleton instance
key_pool = KeyPoolManager()
