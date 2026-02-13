"""Model provider wiring (OpenRouter via OpenAI-compatible API)."""

from __future__ import annotations

from dataclasses import dataclass

from strands.models.openai import OpenAIModel

from config import (
    get_openrouter_api_key,
    get_openrouter_base_url,
    get_openrouter_headers,
    get_openrouter_model_id,
)


@dataclass
class ModelSettings:
    model_id: str
    base_url: str
    max_tokens: int = 1000
    temperature: float = 0.3
    top_p: float = 0.9


def default_model_settings() -> ModelSettings:
    return ModelSettings(
        model_id=get_openrouter_model_id(),
        base_url=get_openrouter_base_url(),
        max_tokens=1000,
        temperature=0.3,
        top_p=0.9,
    )


def build_openai_model(settings: ModelSettings) -> OpenAIModel:
    api_key = get_openrouter_api_key()
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY (or OPENAI_API_KEY)")

    client_args: dict = {
        "api_key": api_key,
        "base_url": settings.base_url,
    }

    headers = get_openrouter_headers()
    if headers:
        client_args["default_headers"] = headers

    return OpenAIModel(
        client_args=client_args,
        model_id=settings.model_id,
        params={
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "top_p": settings.top_p,
        },
    )
