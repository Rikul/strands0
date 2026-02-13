"""Tool registry for the Strands Playground backend."""

from __future__ import annotations

from typing import Any

from strands import Agent, tool

from strands_tools import (
    agent_graph,
    calculator,
    cron,
    current_time,
    editor,
    environment,
    file_read,
    file_write,
    generate_image,
    http_request,
    image_reader,
    journal,
    load_tool,
    mem0_memory,
    memory,
    nova_reels,
    python_repl,
    retrieve,
    shell,
    slack,
    speak,
    stop,
    swarm,
    think,
    use_aws,
    use_llm,
    workflow,
)


@tool
def weather_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city (dummy tool)."""

    return f"Weather forecast for {city} for the next {days} days..."


def make_use_openrouter_llm(openai_model: Any, tools_getter) -> Any:
    """Create a tool that runs a one-off nested agent using the provided model."""

    @tool
    def use_openrouter_llm(prompt: str, system_prompt: str) -> str:
        agent = Agent(
            model=openai_model,
            system_prompt=system_prompt,
            tools=list(tools_getter()),
            messages=[],
        )
        result = agent(prompt)
        return str(result)

    return use_openrouter_llm


def base_available_tools(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    tools: dict[str, Any] = {
        "agent_graph": agent_graph,
        "calculator": calculator,
        "cron": cron,
        "current_time": current_time,
        "editor": editor,
        "environment": environment,
        "file_read": file_read,
        "file_write": file_write,
        "generate_image": generate_image,
        "http_request": http_request,
        "image_reader": image_reader,
        "journal": journal,
        "load_tool": load_tool,
        "mem0_memory": mem0_memory,
        "memory": memory,
        "nova_reels": nova_reels,
        "python_repl": python_repl,
        "retrieve": retrieve,
        "shell": shell,
        "slack": slack,
        "speak": speak,
        "stop": stop,
        "swarm": swarm,
        "think": think,
        "use_aws": use_aws,
        "use_llm": use_llm,
        "workflow": workflow,
        "weather_forecast": weather_forecast,
    }
    if extra:
        tools.update(extra)
    return tools


def tool_descriptions() -> dict[str, str]:
    return {
        "agent_graph": "Create and manage graphs of agents with different topologies and communication patterns",
        "calculator": "Perform mathematical calculations with support for advanced operations",
        "cron": "Manage crontab entries for scheduling tasks, with special support for Strands agent jobs",
        "current_time": "Get the current time in various timezones",
        "editor": "Editor tool designed to do changes iteratively on multiple files",
        "environment": "Manage environment variables at runtime",
        "file_read": "File reading tool with search capabilities, various reading modes, and document mode support",
        "file_write": "Write content to a file with proper formatting and validation based on file type",
        "generate_image": "Create images using Stable Diffusion models",
        "http_request": "Make HTTP requests to external APIs with authentication support",
        "image_reader": "Read and process image files for AI analysis",
        "journal": "Create and manage daily journal entries with tasks and notes",
        "load_tool": "Dynamically load Python tools at runtime",
        "mem0_memory": "Memory management tool for storing, retrieving, and managing memories in Mem0",
        "memory": "Store and retrieve data in Bedrock Knowledge Base",
        "nova_reels": "Create high-quality videos using Amazon Nova Reel",
        "python_repl": "Execute Python code in a REPL environment with PTY support and state persistence",
        "retrieve": "Retrieves knowledge based on the provided text from Amazon Bedrock Knowledge Bases",
        "shell": "Interactive shell with PTY support for real-time command execution and interaction",
        "slack": "Comprehensive Slack integration for messaging, events, and interactions",
        "speak": "Generate speech from text using say command or Amazon Polly.",
        "stop": "Stops the current event loop cycle by setting stop_event_loop flag",
        "swarm": "Create and coordinate a swarm of AI agents for parallel processing and collective intelligence",
        "think": "Process thoughts through multiple recursive cycles",
        "use_aws": "Execute AWS service operations using boto3",
        "use_llm": "Create isolated agent instances for specific tasks (may default to Bedrock if model not provided)",
        "workflow": "Advanced workflow orchestration system for parallel AI task execution",
        "weather_forecast": "Return a dummy weather tool output",
        "use_openrouter_llm": "Create an isolated agent instance using OpenRouter (OpenAI-compatible)",
    }


def default_selected_tools() -> list[Any]:
    # Keep defaults conservative.
    return [calculator, http_request, use_aws]
