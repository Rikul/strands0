"""Strands Playground FastAPI entrypoint.

Run:
  uvicorn main:app --host 0.0.0.0 --port 8003
"""

from __future__ import annotations

from config import load_env
from logging_setup import setup_logging
from app_factory import create_app

load_env()
setup_logging()

app = create_app()
