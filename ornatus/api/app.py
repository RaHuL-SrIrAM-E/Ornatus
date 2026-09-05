"""HTTP API for Ornatus — a thin FastAPI layer over the existing runtime.

    HTTP API -> existing runtime/orchestrator -> Strands Agent ->
    existing tools/services/repositories -> existing persistence

This module contains no business logic: it validates requests, drives the
same ``build_runtime`` / ``run_agent_and_log`` path the CLI uses
(``ornatus.api.cli``), and shapes the result as JSON. Anything about how
outfits are chosen, feedback is recorded, or preferences are learned lives
in ``ornatus.services``/``ornatus.workflows`` exactly as it did before this
module existed.

Run locally without AWS:

    ORNATUS_MODEL_PROVIDER=local poetry run uvicorn ornatus.api.app:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ornatus.agent.orchestrator import OrnatusRuntime, build_runtime
from ornatus.api.demo_data import seed_demo_wardrobe
from ornatus.config.logging import configure_logging
from ornatus.config.settings import get_settings
from ornatus.models.decision import DecisionType
from ornatus.workflows.decision_logging import run_agent_and_log

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the Ornatus runtime once per process and reuse it for every
    request, instead of standing up a fresh database/service/tool graph
    per call (the way the CLI does per-process). See ``OrnatusRuntime`` for
    why the shared agent isn't reused directly across requests.
    """
    configure_logging()
    runtime = build_runtime()
    seed_demo_wardrobe(runtime.wardrobe_service)
    app.state.runtime = runtime
    try:
        yield
    finally:
        runtime.db.close()


app = FastAPI(title="Ornatus API", version="0.1.0", lifespan=lifespan)


def _get_runtime() -> OrnatusRuntime:
    return app.state.runtime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="Free-text request or feedback, close to verbatim.")

    @field_validator("message")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("message must not be blank")
        return stripped


class RecommendationOut(BaseModel):
    id: str
    item_ids: list[str]
    excluded_item_ids: list[str]
    reasoning: str
    confidence: float | None = None
    event_reference: str | None = None
    weather_summary: str | None = None


class ChatResponse(BaseModel):
    response: str
    decision_id: str
    decision_type: str
    recommendation: RecommendationOut | None = None


class HealthResponse(BaseModel):
    status: str
    model_provider: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_provider=get_settings().model_provider)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    runtime = _get_runtime()

    try:
        agent = runtime.new_agent()
        result = run_agent_and_log(agent, runtime.decision_service, runtime.user_id, request.message)
    except Exception as exc:
        logger.exception("Agent run failed for request: %s", request.message)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ornatus could not process that request. Please try again.",
        ) from exc

    recommendation = None
    if result.decision.decision_type == DecisionType.OUTFIT_RECOMMENDATION:
        try:
            latest = runtime.outfit_service.get_latest_for_user(runtime.user_id)
        except Exception as exc:
            logger.exception("Failed to load the persisted recommendation after a successful agent run")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ornatus recorded a decision but the recommendation could not be retrieved.",
            ) from exc
        if latest is not None:
            recommendation = RecommendationOut(
                id=latest.id,
                item_ids=latest.item_ids,
                excluded_item_ids=latest.excluded_item_ids,
                reasoning=latest.reasoning,
                confidence=latest.confidence,
                event_reference=latest.event_reference,
                weather_summary=latest.weather_summary,
            )

    return ChatResponse(
        response=result.response_text,
        decision_id=result.decision.id,
        decision_type=result.decision.decision_type.value,
        recommendation=recommendation,
    )
