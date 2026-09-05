# Ornatus

*Your wardrobe, quietly taken care of.*

Ornatus is an autonomous personal wardrobe agent. It is not a stylist chatbot —
it manages a person's clothing life end-to-end: understanding the wardrobe,
tracking context (weather, calendar, occasions), turning clothing intent into
real purchases with human approval, tracking deliveries and returns, and
learning from what actually gets worn.

Guiding principle: **the user should not manage Ornatus — Ornatus manages the
wardrobe.**

This is Phase 1. The first real use case is proven end-to-end, including a
closed learning loop: asking what to wear, the agent gathering
occasion/weather/wardrobe/preference context through tools, recommending a
real outfit, logging that decision, recording feedback, converting it into
a remembered preference signal, and using that signal to change the *next*
recommendation. Shopping, purchase approval, deliveries, and returns are
intentionally not built yet — see [Status](#status--whats-next).

## Architecture

Seven layers, kept separate on purpose so the codebase doesn't collapse into
one agent that does everything:

| Layer | Location | Responsibility |
|---|---|---|
| Agent | `ornatus/agent/` | The orchestrating Strands Agent: system prompt, model wiring, tool registry. One agent in Phase 1. |
| Tools | `ornatus/tools/` | Thin, agent-callable, structured-I/O wrappers over services. No business logic. |
| Services | `ornatus/services/` | Deterministic business logic — no LLM. |
| Workflows | `ornatus/workflows/` | Durable multi-step processes that outlive a single agent turn (purchase approval → order → delivery). Reserved, not yet populated. |
| Persistence | `ornatus/persistence/` | Repository abstraction + SQLite implementation. |
| Triggers | `ornatus/triggers/` | Proactive entrypoints (scheduled prep, webhooks) that invoke the agent. Reserved, not yet populated. |
| API | `ornatus/api/` | The human-facing surface — a CLI, and now a thin HTTP API (`ornatus/api/app.py`). |

Data models for the full domain (wardrobe items, user profile, preferences,
outfit history/recommendations, purchases, deliveries, returns, events,
agent decisions, feedback, learned preferences, agent memory) live in
`ornatus/models/`, and the SQLite schema in `ornatus/persistence/schema.sql`
mirrors all of them. Working slices as of Phase 1: wardrobe, occasion/
weather context, outfit recommendations, agent decisions, feedback, and
learned preferences — each with a repository, service, and (where
agent-facing) tools. User profile, the coarser `Preferences` aggregate,
purchases, deliveries, returns, and generic event-log memory remain
schema-only, reserved for later phases.

### The learning loop

    user feedback ("...don't want to wear the blazer")
      -> record_feedback tool
      -> FeedbackService: rejected_item_ids become item-level LearnedPreference
         signals automatically (mechanical, no NLP); broader category/context
         signals are persisted only when the agent explicitly supplies them
      -> next outfit request
      -> get_user_preferences tool (scoped to the occasion, when given)
      -> agent excludes the disliked item and explains why in plain language
      -> record_outfit_recommendation tool records what was picked *and*
         what was deliberately left out (excluded_item_ids, preferences_considered)

`LearnedPreference` (`ornatus/models/preferences.py`) is scoped —
item/category/context/general — on purpose: rejecting one item should not
silently become "avoid this whole category everywhere." See
`ornatus/services/feedback_service.py` for exactly what gets inferred
automatically vs. what requires the agent to say so explicitly.

### The outfit recommendation workflow

    user request
      -> Ornatus agent (Strands)
      -> get_event_context tool  (CalendarService — deterministic/mock)
      -> get_weather tool        (WeatherService — deterministic/mock)
      -> get_wardrobe_items tool (WardrobeService — real SQLite data)
      -> get_user_preferences tool (PreferenceService — learned from past feedback)
      -> agent reasons over the returned items, excluding anything it's learned to avoid
      -> record_outfit_recommendation tool (validates item ids, persists OutfitRecommendation)
      -> ornatus.workflows.decision_logging records an AgentDecision (tools used, items selected, outcome)
      -> concise response to the user

Feedback ("I don't want to wear the blazer") follows the same shape: the
agent may look up the wardrobe to resolve which item was meant, then calls
`record_feedback`, which resolves to the user's latest recommendation when
none is given explicitly (feedback commonly arrives as a separate CLI
invocation, so "the latest recommendation" is read from persistence, not
conversation memory) — and turns rejected items into remembered preferences
(see [The learning loop](#the-learning-loop)).

The exact tool sequence is chosen by the model at runtime from the tools'
descriptions — it isn't hardcoded in the application. See
`ornatus/agent/system_prompt.py` for the guidance given to the model and
`ornatus/tools/` for the tool set.

### Why one agent

Strands supports multiple agents (graph/swarm/agent-as-tool), but Phase 1
uses a single orchestrating `Agent` with a growing tool registry, per the
product decision to keep one strong generalist agent rather than several
narrow ones. `build_orchestrator()` in `ornatus/agent/orchestrator.py` is the
one seam where that could change — nothing elsewhere assumes there's only
ever one agent.

### Model provider

`ornatus/agent/model_provider.py` is the only place that knows which model
backend is in use, selected via `ORNATUS_MODEL_PROVIDER`:

- **`bedrock`** (default) — the real, production provider (Amazon Bedrock /
  Nova 2 Lite). Requires AWS credentials with Bedrock access.
- **`local`** — a deterministic, rule-based stand-in
  (`ornatus.agent.local_model.LocalDeterministicModel`) with no real model
  behind it at all. It implements the same `strands.models.model.Model`
  interface a real provider would, so the orchestrator/tools/services don't
  know the difference, but it picks its next tool call with fixed rules
  rather than understanding language — it exists purely so the agent loop
  can be developed and tested without AWS access (the AWS account backing
  this hackathon is currently mid-verification for Bedrock). It is never
  the default and is not a claim that a real model is running.

Switching providers is a config change plus a branch in
`model_provider.py`, not a change to the agent, tools, or services.

### Human approval boundary

Encoded in the system prompt (`ornatus/agent/system_prompt.py`): any action
that spends money or irreversibly changes the wardrobe (discard/donate/
return) requires explicit approval. Suggestions, lookups, and reversible
organization don't. This becomes an enforced workflow gate once purchase
workflows are built — for now it's a prompt-level constraint.

## Requirements

- Python 3.11–3.13
- [Poetry](https://python-poetry.org/)
- AWS credentials with Bedrock access in `us-west-2` (or wherever
  `ORNATUS_BEDROCK_REGION` points) — only needed for the real Bedrock/Nova
  provider. Everything else (tests, the CLI with
  `ORNATUS_MODEL_PROVIDER=local`) runs without AWS.

## Setup

```bash
poetry install
cp .env.example .env   # optional — defaults work as-is
```

## Running the Phase 1 milestone

Without AWS access, using the deterministic local model:

```bash
ORNATUS_MODEL_PROVIDER=local poetry run ornatus "What should I wear to my client dinner Friday?"
ORNATUS_MODEL_PROVIDER=local poetry run ornatus "I like that outfit, but I don't want to wear the blazer."
ORNATUS_MODEL_PROVIDER=local poetry run ornatus "What should I wear to my client dinner Friday?"
```

The third command repeats the first, verbatim — the point is that the
answer is now different: the blazer is left out, and the reply explains why
in plain language, without mentioning any tool or database.

With real Bedrock/Nova access (once AWS verification completes), drop the
env var — `bedrock` is the default:

```bash
poetry run ornatus "What should I wear to my client dinner Friday?"
```

## HTTP API

A thin FastAPI layer sits in front of the same runtime the CLI uses — it
adds no business logic of its own:

    HTTP API -> existing runtime/orchestrator -> Strands Agent ->
    existing tools/services/repositories -> existing persistence

Unlike the CLI (a fresh process, and therefore a fresh database/service/
tool graph, per invocation), the API builds the runtime **once** at process
startup (`ornatus/api/app.py`, via a FastAPI `lifespan`) and reuses the same
database connection and services across requests. Each `/chat` request
still gets its own, stateless Strands `Agent` (`OrnatusRuntime.new_agent()`)
bound to those shared tools — a Strands `Agent` accumulates conversation
history in `agent.messages`, and Phase 1 requests are single-turn, so
reusing one `Agent` instance across unrelated HTTP requests would leak
state between them. This mirrors exactly how the CLI already behaves
(each invocation is its own turn; state persists via SQLite, not
conversation memory) — the API just avoids repeating the database/schema/
service setup per request.

Run it locally without AWS credentials:

```bash
ORNATUS_MODEL_PROVIDER=local poetry run uvicorn ornatus.api.app:app --reload
```

Once AWS Bedrock access is available, drop the env var and it runs against
Nova 2 Lite (`bedrock` is the default provider) instead.

### `GET /health`

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status": "ok", "model_provider": "local"}
```

### `POST /chat`

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I wear to my client dinner Friday?"}'
```

```json
{
  "response": "Picked White Oxford Shirt, Charcoal Trousers, Brown Loafers, Navy Blazer for client dinner: it calls for business casual attire, and the forecast (clear, 52.0-68.0F) suggests layering with the outerwear.",
  "decision_id": "dec-ea5e9db37d51",
  "decision_type": "outfit_recommendation",
  "recommendation": {
    "id": "rec-4f04fb867b02",
    "item_ids": ["item-shirt-oxford-white", "item-trousers-charcoal", "item-loafers-brown", "item-blazer-navy"],
    "excluded_item_ids": [],
    "reasoning": "Picked White Oxford Shirt, Charcoal Trousers, Brown Loafers, Navy Blazer for client dinner: it calls for business casual attire, and the forecast (clear, 52.0-68.0F) suggests layering with the outerwear.",
    "confidence": 0.75,
    "event_reference": "Client Dinner",
    "weather_summary": "clear, 52.0-68.0F"
  }
}
```

Feedback works the same way as a second request — `recommendation` is
`null` for a feedback-type decision (there's nothing new to recommend yet):

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I like that outfit, but I do not want to wear the blazer."}'
```

A single demo user is used for every request in Phase 1 (no auth, no
sessions, no multi-user routing) — same as the CLI. An empty or blank
`message` is rejected with `422`; an agent or persistence failure returns a
clean `502`/`500` with no stack trace or credentials in the response body
(diagnostics are logged server-side only).

On first run this seeds a small, deterministic sample wardrobe (navy
blazer, oxford shirt, chinos, loafers, ...) into `ornatus.db` (SQLite,
git-ignored) for a demo user. Any free-text request works — asking what to
wear runs the full [outfit recommendation workflow](#the-outfit-recommendation-workflow);
other requests fall back to the agent's general tool set (wardrobe
lookup/search, marking an item worn).

## Testing

```bash
poetry run pytest
```

Everything except `tests/test_agent_smoke.py` runs without AWS — including
the full agent loop, via `LocalDeterministicModel`
(`tests/test_local_agent_workflow.py`), and the HTTP API
(`tests/test_api.py`, using FastAPI's `TestClient` against
`ORNATUS_MODEL_PROVIDER=local`). `test_agent_smoke.py` makes real Bedrock
calls and is skipped automatically when no AWS credentials are available.

## Status & what's next

Built in Phase 1:
- Full project structure and layer separation
- Full data/schema layer for the domain model
- Working repositories/services/tools: wardrobe (list/search/get/mark-worn),
  occasion + weather context (deterministic mocks, real-integration-shaped),
  outfit recommendations (validated against real wardrobe items), agent
  decision logging, feedback, and learned preferences
- A closed learning loop: feedback -> preference signal -> retrieved and
  applied on the next matching request — see
  [The learning loop](#the-learning-loop)
- The single orchestrating agent, wired to Bedrock/Nova by default, with a
  deterministic local model for development without AWS
- A small, realistic seed wardrobe and a proven end-to-end scenario
  ("client dinner Friday") including the learn-and-adapt loop
- A thin HTTP API (`ornatus/api/app.py`, FastAPI/Uvicorn) over the same
  runtime the CLI uses — `GET /health`, `POST /chat` — with no business
  logic of its own; see [HTTP API](#http-api)
- Tests for all of the above, none requiring AWS

Deferred (deliberately, to stay in scope for this milestone):
- Frontend/UI, auth, sessions, multi-user support, WebSockets/streaming for
  the API — the API is a request/response JSON endpoint only, for now
- Rolling learned preferences up into the coarser `Preferences` aggregate
  (`learned_weights`) — each signal is its own row; nothing distills them
  into a per-user summary profile yet
- Automatically inferring a *general* (item/context-independent) category
  dislike from bare feedback text ("I don't like blazers") — the local
  model only derives item-level and context-level signals, both grounded in
  a resolved item; a bare category claim needs real language understanding
  to distinguish from an item-specific complaint, which is exactly the kind
  of guess this milestone avoided making (a real agent can still supply a
  `category_dislike`/`general` signal explicitly via `record_feedback`)
- Reinforcing/strengthening a preference's confidence when the same signal
  recurs — each occurrence is currently its own row, not merged
- Shopping/purchase workflows, delivery tracking, returns
- Proactive triggers (scheduled prep, calendar/weather-change webhooks) —
  the workflow above is user-initiated only
- Packing/laundry/repair assistance
- Multi-user auth (`current_user_id` is a single configured user)

These land as additional tools/services/workflows behind the same
orchestrator, following the pattern the outfit-recommendation slice
establishes.
