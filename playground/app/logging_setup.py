"""Logging setup for the Strands Playground backend."""

from __future__ import annotations

import logging


def setup_logging() -> None:
    # Keep it simple; uvicorn will add its own loggers.
    logging.basicConfig(
        format="%(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )

    logging.getLogger("strands").setLevel(logging.DEBUG)
    logging.getLogger("agent-web-service").setLevel(logging.DEBUG)
