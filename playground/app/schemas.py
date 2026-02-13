"""Pydantic request/response schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    userId: str


class SystemPromptRequest(BaseModel):
    systemPrompt: str


class ModelSettingsRequest(BaseModel):
    modelId: str
    region: str  # NOTE: frontend uses 'region' but we treat it as base_url
    maxTokens: Optional[int] = None
    temperature: Optional[float] = None
    topP: Optional[float] = None


class ToolsUpdateRequest(BaseModel):
    tools: list[str]
