"""Vercel Python entrypoint for the FastAPI backend.

This file exposes `app` at repository root so Vercel can detect it.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

# Ensure imports like `from app.main import app` resolve on Vercel.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402
