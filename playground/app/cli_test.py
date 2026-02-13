"""CLI utilities for Strands Playground (OpenRouter).

This script has two roles:
1) Quick direct utilities (no LLM): calc + current time.
2) LLM smoke test against OpenRouter (OpenAI-compatible).

Usage:
  source .venv/bin/activate

  # Direct (no LLM)
  python cli_test.py calc "123*456"
  python cli_test.py time America/Chicago

  # LLM smoke test
  python cli_test.py llm --prompt "Hello" --system-prompt "You are helpful"

Environment (.env supported):
  OPENROUTER_API_KEY (required for llm)
  OPENROUTER_BASE_URL (default https://openrouter.ai/api/v1)
  OPENROUTER_MODEL (default anthropic/claude-3.5-sonnet)
  OPENROUTER_SITE_URL (optional, sent as HTTP-Referer)
  OPENROUTER_APP_NAME (optional, sent as X-Title)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


def _cmd_calc(expr: str) -> int:
    # Keep this simple + local for predictable CLI output.
    import sympy as sp

    try:
        value = sp.sympify(expr)
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"error: could not parse expression: {e}\n")
        return 2

    sys.stdout.write(str(value) + "\n")
    return 0


def _cmd_time(tz: str) -> int:
    try:
        now = datetime.now(ZoneInfo(tz))
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"error: invalid timezone '{tz}': {e}\n")
        return 2

    sys.stdout.write(now.isoformat() + "\n")
    return 0


def _openai_client_args(base_url: str) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY (or OPENAI_API_KEY)")

    headers = {}
    if os.environ.get("OPENROUTER_SITE_URL"):
        headers["HTTP-Referer"] = os.environ["OPENROUTER_SITE_URL"]
    if os.environ.get("OPENROUTER_APP_NAME"):
        headers["X-Title"] = os.environ["OPENROUTER_APP_NAME"]

    client_args = {"api_key": api_key, "base_url": base_url}
    if headers:
        client_args["default_headers"] = headers
    return client_args


def _cmd_llm(prompt: str, system_prompt: str, model_id: str, base_url: str) -> int:
    # Import only when needed.
    from strands import Agent
    from strands.models.openai import OpenAIModel

    model = OpenAIModel(
        client_args=_openai_client_args(base_url),
        model_id=model_id,
        params={"temperature": 0.3, "max_tokens": 1000},
    )

    agent = Agent(model=model, system_prompt=system_prompt, tools=[])
    result = agent(prompt)
    sys.stdout.write(str(result).strip() + "\n")
    return 0


def main(argv: list[str]) -> int:
    load_dotenv()

    ap = argparse.ArgumentParser(description="Playground CLI helpers")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_calc = sub.add_parser("calc", help="Evaluate a math expression locally (no LLM)")
    ap_calc.add_argument("expression")

    ap_time = sub.add_parser("time", help="Print current time (ISO8601) in timezone")
    ap_time.add_argument("timezone")

    ap_llm = sub.add_parser("llm", help="LLM smoke test against OpenRouter")
    ap_llm.add_argument("--prompt", required=True)
    ap_llm.add_argument("--system-prompt", default="You are a helpful assistant.")
    ap_llm.add_argument(
        "--model",
        default=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
    )
    ap_llm.add_argument(
        "--base-url",
        default=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )

    args = ap.parse_args(argv)

    if args.cmd == "calc":
        return _cmd_calc(args.expression)
    if args.cmd == "time":
        return _cmd_time(args.timezone)
    if args.cmd == "llm":
        return _cmd_llm(args.prompt, args.system_prompt, args.model, args.base_url)

    sys.stderr.write("error: unknown command\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
