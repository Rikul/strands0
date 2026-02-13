"""CLI test runner for Strands Playground (OpenRouter).

Usage:
  source .venv/bin/activate
  python cli_test.py --prompt "Hello" \
    --system-prompt "You are helpful" \
    --model "anthropic/claude-3.5-sonnet"

Environment (.env supported):
  OPENROUTER_API_KEY (required)
  OPENROUTER_BASE_URL (default https://openrouter.ai/api/v1)
  OPENROUTER_MODEL (default anthropic/claude-3.5-sonnet)
  OPENROUTER_SITE_URL (optional, sent as HTTP-Referer)
  OPENROUTER_APP_NAME (optional, sent as X-Title)
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator


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


def main(argv: list[str]) -> int:
    load_dotenv()

    ap = argparse.ArgumentParser(description="Test Strands/OpenRouter from the command line")
    ap.add_argument("--prompt", required=True, help="User prompt")
    ap.add_argument(
        "--system-prompt",
        default="You are a helpful assistant.",
        help="System prompt for the agent",
    )
    ap.add_argument(
        "--model",
        default=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        help="OpenRouter model id (OpenAI compatible)",
    )
    ap.add_argument(
        "--base-url",
        default=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        help="OpenAI-compatible base URL",
    )

    args = ap.parse_args(argv)

    model = OpenAIModel(
        client_args=_openai_client_args(args.base_url),
        model_id=args.model,
        params={"temperature": 0.3, "max_tokens": 1000},
    )

    agent = Agent(model=model, system_prompt=args.system_prompt, tools=[calculator])
    result = agent(args.prompt)

    # stdout: model response only (avoid tool-trace noise)
    sys.stdout.write(str(result).strip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
