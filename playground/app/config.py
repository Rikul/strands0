"""Configuration helpers for the Strands Playground backend."""

from __future__ import annotations

import os

from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env (if present)."""
    load_dotenv()


def get_openrouter_base_url() -> str:
    return os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def get_openrouter_model_id() -> str:
    return os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")


def get_openrouter_api_key() -> str | None:
    return os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")


def get_openrouter_headers() -> dict[str, str]:
    """Optional headers recommended by OpenRouter."""
    headers: dict[str, str] = {}
    if os.environ.get("OPENROUTER_SITE_URL"):
        headers["HTTP-Referer"] = os.environ["OPENROUTER_SITE_URL"]
    if os.environ.get("OPENROUTER_APP_NAME"):
        headers["X-Title"] = os.environ["OPENROUTER_APP_NAME"]
    return headers


def get_session_table_config() -> tuple[str | None, str | None, str | None]:
    """Optional DynamoDB session storage config."""
    table_name = os.environ.get("TABLE_NAME") or None
    table_region = os.environ.get("TABLE_REGION") or None
    primary_key = os.environ.get("PRIMARY_KEY") or None
    return table_name, table_region, primary_key
