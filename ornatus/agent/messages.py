"""Helpers for reading a finished (or in-progress) Strands conversation.

Used by ``ornatus.agent.local_model`` (to decide what to do next while a run
is in progress) and ``ornatus.workflows.decision_logging`` (to summarize a
run after it finishes). Both need the same thing: which tools were called,
and what they returned.
"""

import json
from typing import Any

from strands.types.content import Messages


def initial_user_text(messages: Messages) -> str:
    for message in messages:
        if message.get("role") == "user":
            for block in message.get("content", []):
                if "text" in block:
                    return block["text"]
    return ""


def tool_call_names(messages: Messages) -> list[str]:
    return [
        block["toolUse"]["name"]
        for message in messages
        if message.get("role") == "assistant"
        for block in message.get("content", [])
        if "toolUse" in block
    ]


def tool_result_for(messages: Messages, tool_name: str) -> Any | None:
    """Parsed JSON payload of the most recent result for `tool_name`, if any."""
    matching_ids = [
        block["toolUse"]["toolUseId"]
        for message in messages
        if message.get("role") == "assistant"
        for block in message.get("content", [])
        if "toolUse" in block and block["toolUse"]["name"] == tool_name
    ]
    if not matching_ids:
        return None
    wanted_id = matching_ids[-1]

    for message in messages:
        if message.get("role") != "user":
            continue
        for block in message.get("content", []):
            result = block.get("toolResult")
            if result and result.get("toolUseId") == wanted_id:
                try:
                    return json.loads(result["content"][0]["text"])
                except (KeyError, IndexError, json.JSONDecodeError):
                    return None
    return None


def final_assistant_text(messages: Messages) -> str:
    for message in reversed(messages):
        if message.get("role") != "assistant":
            continue
        texts = [block["text"] for block in message.get("content", []) if "text" in block]
        if texts:
            return " ".join(texts)
    return ""
