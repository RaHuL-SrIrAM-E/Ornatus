"""A deterministic, rule-based stand-in for a real model.

This is NOT a language model and does not call any LLM. It exists so the
full agent -> tools -> reasoning -> recommendation -> decision-log ->
feedback loop can be exercised locally, without AWS credentials, while the
AWS account backing Bedrock/Nova is mid-verification. It implements
``strands.models.model.Model`` the same way a real provider would, so the
orchestrator, tools, and services underneath it don't know or care that
they're not talking to Bedrock.

It reasons the only way a non-LLM safely can: by inspecting which of
Ornatus's own tools have already been called and what they returned, and
picking the next tool + arguments with fixed rules. That is a real
difference from a language model (fixed rules vs. free-form understanding)
and callers should not mistake one for the other — hence keeping this in a
distinctly named module, selected only via ``ORNATUS_MODEL_PROVIDER=local``,
never the default.

Switch back to the real provider at any time with
``ORNATUS_MODEL_PROVIDER=bedrock`` (the default) — see
``ornatus.agent.model_provider``.
"""

import json
from collections.abc import AsyncIterable
from typing import Any
from uuid import uuid4

from strands.models.model import Model
from strands.types.content import Messages
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolSpec

from ornatus.agent.messages import initial_user_text, tool_call_names, tool_result_for

_GARMENT_KEYWORDS = [
    "blazer",
    "shirt",
    "trouser",
    "chino",
    "denim",
    "jean",
    "sneaker",
    "loafer",
    "shoe",
    "jacket",
    "coat",
]

_FEEDBACK_MARKERS = [
    "don't want",
    "do not want",
    "i like",
    "i love",
    "actually",
    "but i",
    "not a fan",
    "instead of",
]

_NEGATIVE_WORDS = ["don't", "do not", "not ", "avoid", "hate", "dislike"]
_POSITIVE_WORDS = ["like", "love", "great", "good", "perfect", "nice"]


def _tool_use_id() -> str:
    return f"tool_{uuid4().hex[:8]}"


def _looks_like_feedback(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _FEEDBACK_MARKERS)


def _sentiment(text: str) -> str:
    lowered = text.lower()
    negative = any(w in lowered for w in _NEGATIVE_WORDS)
    positive = any(w in lowered for w in _POSITIVE_WORDS)
    if positive and negative:
        return "mixed"
    if negative:
        return "negative"
    if positive:
        return "positive"
    return "neutral"


def _match_garment_ids(text: str, wardrobe_items: list[dict]) -> list[str]:
    lowered = text.lower()
    matched = []
    for item in wardrobe_items or []:
        haystack = " ".join(
            filter(None, [item.get("name", ""), item.get("subcategory", ""), item.get("category", "")])
        ).lower()
        for keyword in _GARMENT_KEYWORDS:
            if keyword in lowered and keyword in haystack:
                matched.append(item["id"])
                break
    return matched


def _select_outfit(wardrobe_items: list[dict], event: dict, weather: dict) -> tuple[list[str], str]:
    formality = event.get("formality", "casual")
    by_category: dict[str, list[dict]] = {}
    for item in wardrobe_items:
        if item.get("status") == "active":
            by_category.setdefault(item["category"], []).append(item)

    def best(category: str) -> dict | None:
        candidates = by_category.get(category, [])
        exact = [i for i in candidates if i.get("formality") == formality]
        pool = exact or candidates
        return pool[0] if pool else None

    cold_or_wet = (
        weather.get("temperature_low_f", 60) < 55 or weather.get("precipitation_probability", 0) >= 0.4
    )

    selected = [best("top"), best("bottom"), best("shoes")]
    if cold_or_wet:
        selected.append(best("outerwear"))
    selected = [item for item in selected if item]

    item_ids = [item["id"] for item in selected]
    names = ", ".join(item["name"] for item in selected)

    reasoning = (
        f"Picked {names} for {event.get('occasion', 'the occasion')}: it calls for "
        f"{str(formality).replace('_', ' ')} attire, and the forecast "
        f"({weather.get('condition')}, {weather.get('temperature_low_f')}-"
        f"{weather.get('temperature_high_f')}F) "
        + ("suggests layering with the outerwear." if cold_or_wet else "is mild enough to skip a layer.")
    )
    return item_ids, reasoning


class LocalDeterministicModel(Model):
    """Rule-based ``Model`` for local development without Bedrock access."""

    def get_config(self) -> Any:
        return {"provider": "ornatus-local-deterministic"}

    def update_config(self, **model_config: Any) -> None:
        pass

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs):
        raise NotImplementedError(
            "LocalDeterministicModel does not support structured_output; it exists only "
            "to exercise the tool-calling agent loop."
        )
        yield  # pragma: no cover — makes this an async generator per the Model interface

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        tool_choice: Any | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        called = tool_call_names(messages)
        request_text = initial_user_text(messages)

        def tool_call(name: str, arguments: dict) -> list[StreamEvent]:
            tool_use_id = _tool_use_id()
            return [
                {"messageStart": {"role": "assistant"}},
                {"contentBlockStart": {"start": {"toolUse": {"name": name, "toolUseId": tool_use_id}}}},
                {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(arguments)}}}},
                {"contentBlockStop": {}},
                {"messageStop": {"stopReason": "tool_use"}},
            ]

        def final_text(text: str) -> list[StreamEvent]:
            return [
                {"messageStart": {"role": "assistant"}},
                {"contentBlockStart": {"start": {}}},
                {"contentBlockDelta": {"delta": {"text": text}}},
                {"contentBlockStop": {}},
                {"messageStop": {"stopReason": "end_turn"}},
            ]

        events: list[StreamEvent]

        if _looks_like_feedback(request_text):
            events = self._feedback_turn(request_text, called, messages, tool_call, final_text)
        else:
            events = self._outfit_turn(request_text, called, messages, tool_call, final_text)

        for event in events:
            yield event

    def _feedback_turn(self, request_text, called, messages, tool_call, final_text):
        wardrobe_result = tool_result_for(messages, "get_wardrobe_items")
        needs_wardrobe_lookup = wardrobe_result is None and any(
            keyword in request_text.lower() for keyword in _GARMENT_KEYWORDS
        )
        if needs_wardrobe_lookup and "get_wardrobe_items" not in called:
            return tool_call("get_wardrobe_items", {})

        if "record_feedback" not in called:
            rejected_ids = _match_garment_ids(request_text, wardrobe_result or [])
            return tool_call(
                "record_feedback",
                {
                    "feedback_text": request_text,
                    "rejected_item_ids": rejected_ids,
                    "preference_signal": _sentiment(request_text),
                },
            )

        return final_text("Got it — I've noted that feedback for next time.")

    def _outfit_turn(self, request_text, called, messages, tool_call, final_text):
        if "get_event_context" not in called:
            return tool_call("get_event_context", {"query": request_text})

        event = tool_result_for(messages, "get_event_context") or {}
        if "get_weather" not in called:
            return tool_call(
                "get_weather",
                {"location": event.get("location") or "local", "on_date": event.get("start_time", "")[:10]},
            )

        weather = tool_result_for(messages, "get_weather") or {}
        if "get_wardrobe_items" not in called:
            return tool_call("get_wardrobe_items", {})

        wardrobe_items = tool_result_for(messages, "get_wardrobe_items") or []
        if "record_outfit_recommendation" not in called:
            item_ids, reasoning = _select_outfit(wardrobe_items, event, weather)
            weather_summary = (
                f"{weather.get('condition')}, {weather.get('temperature_low_f')}-"
                f"{weather.get('temperature_high_f')}F"
                if weather
                else None
            )
            return tool_call(
                "record_outfit_recommendation",
                {
                    "request_text": request_text,
                    "item_ids": item_ids,
                    "reasoning": reasoning,
                    "event_reference": event.get("title"),
                    "weather_summary": weather_summary,
                    "confidence": 0.75,
                },
            )

        recommendation = tool_result_for(messages, "record_outfit_recommendation") or {}
        return final_text(recommendation.get("reasoning", "Here's an outfit recommendation."))
