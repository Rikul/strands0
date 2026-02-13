"""FastAPI app factory for Strands Playground."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agent_service import DEFAULT_SYSTEM_PROMPT, StrandsPlaygroundAgent
from config import get_session_table_config
from model_provider import ModelSettings, build_openai_model, default_model_settings
from schemas import (
    ModelSettingsRequest,
    PromptRequest,
    SystemPromptRequest,
    ToolsUpdateRequest,
)
from session_store import SessionStore
from tools_registry import (
    base_available_tools,
    default_selected_tools,
    make_use_openrouter_llm,
    tool_descriptions,
)

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    system_prompt: str
    model_settings: ModelSettings
    model: object
    tools: list
    available_tools: dict
    tool_descriptions: dict[str, str]
    store: SessionStore


def create_app() -> FastAPI:
    table_name, table_region, primary_key = get_session_table_config()
    store = SessionStore(table_name=table_name, table_region=table_region, primary_key=primary_key)

    model_settings = default_model_settings()
    model = build_openai_model(model_settings)

    state = AppState(
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        model_settings=model_settings,
        model=model,
        tools=default_selected_tools(),
        available_tools={},
        tool_descriptions=tool_descriptions(),
        store=store,
    )

    # Create OpenRouter nested-agent tool bound to *current* model + tool selection.
    def tools_getter():
        return state.tools

    use_openrouter_llm = make_use_openrouter_llm(state.model, tools_getter)

    state.available_tools = base_available_tools({"use_openrouter_llm": use_openrouter_llm})

    app = FastAPI()

    @app.get("/get_conversations")
    def get_conversations(userId: str):
        try:
            agent = StrandsPlaygroundAgent(
                model=state.model,
                system_prompt=state.system_prompt,
                user_id=userId,
                tools=state.tools,
                store=state.store,
            )
            return {"messages": agent.messages}
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting conversations: {e}")

    @app.post("/strandsplayground_agent")
    def get_agent_response(request: PromptRequest):
        try:
            agent = StrandsPlaygroundAgent(
                model=state.model,
                system_prompt=state.system_prompt,
                user_id=request.userId,
                tools=state.tools,
                store=state.store,
            )
            result = agent(request.prompt)
            agent.save()
            return {
                "messages": result.message,
                "latencyMs": result.metrics.accumulated_metrics["latencyMs"],
                "totalTokens": result.metrics.accumulated_usage["totalTokens"],
                "summary": result.metrics.get_summary(),
            }
        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing agent response: {e}")

    @app.get("/system_prompt")
    def get_system_prompt():
        return {"systemPrompt": state.system_prompt}

    @app.post("/system_prompt")
    def set_system_prompt(request: SystemPromptRequest):
        state.system_prompt = request.systemPrompt
        return {"systemPrompt": state.system_prompt}

    @app.get("/model_settings")
    def get_model_settings():
        return {
            "modelId": state.model_settings.model_id,
            "region": state.model_settings.base_url,
            "maxTokens": state.model_settings.max_tokens,
            "temperature": state.model_settings.temperature,
            "topP": state.model_settings.top_p,
        }

    @app.post("/model_settings")
    def set_model_settings(request: ModelSettingsRequest):
        # NOTE: frontend uses 'region'; we treat it as base_url.
        state.model_settings.model_id = request.modelId
        state.model_settings.base_url = request.region
        if request.maxTokens is not None:
            state.model_settings.max_tokens = request.maxTokens
        if request.temperature is not None:
            state.model_settings.temperature = request.temperature
        if request.topP is not None:
            state.model_settings.top_p = request.topP

        state.model = build_openai_model(state.model_settings)
        # Rebind nested tool to updated model.
        nonlocal use_openrouter_llm
        use_openrouter_llm = make_use_openrouter_llm(state.model, tools_getter)
        state.available_tools["use_openrouter_llm"] = use_openrouter_llm
        state.tool_descriptions["use_openrouter_llm"] = "Create an isolated agent instance using OpenRouter (OpenAI-compatible)"

        return {
            "modelId": state.model_settings.model_id,
            "region": state.model_settings.base_url,
            "maxTokens": state.model_settings.max_tokens,
            "temperature": state.model_settings.temperature,
            "topP": state.model_settings.top_p,
        }

    @app.get("/get_available_tools")
    def get_available_tools():
        return {
            "available_tools": list(state.available_tools.keys()),
            "selected_tools": [t.__name__.split(".")[-1] for t in state.tools],
            "tool_descriptions": state.tool_descriptions,
        }

    @app.post("/update_tools")
    def update_tools(request: ToolsUpdateRequest):
        try:
            for tool_name in request.tools:
                if tool_name not in state.available_tools:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            state.tools = [state.available_tools[name] for name in request.tools]
            return {"success": True, "selected_tools": [t.__name__ for t in state.tools]}
        except Exception as e:
            logger.error(f"Error updating tools: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating tools: {e}")

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    @app.get("/")
    def read_root():
        return FileResponse("./static/index.html")

    app.mount("/", StaticFiles(directory="./static"), name="frontend")

    return app
