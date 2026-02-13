"""Strands agent wrapper for the Playground backend."""

from __future__ import annotations

import logging

from strands import Agent

from session_store import SessionStore

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant powered by Strands. Strands Agents is a simple-to-use, "
    "code-first framework for building agents - open source by AWS.\n"
    "The user has the ability to modify your set of built-in tools. Every time your tool set is changed, "
    "you can propose a new set of tasks that you can do.\n"
)


class StrandsPlaygroundAgent(Agent):
    def __init__(self, *, system_prompt: str, model, user_id: str, tools: list, store: SessionStore):
        messages = store.load_messages(user_id)
        super().__init__(
            system_prompt=system_prompt,
            model=model,
            tools=tools,
            callback_handler=None,
            messages=messages,
            load_tools_from_directory=False,
        )

        self._store = store
        self._user_id = user_id
        logger.debug(f"tools available: {self.tool_names}")

    def save(self) -> None:
        self._store.save_messages(self._user_id, self.messages)
