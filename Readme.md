# Ornatus

*Your wardrobe, quietly taken care of.*

Ornatus is an autonomous personal wardrobe agent. It is not a stylist chatbot —
it manages a person's clothing life end-to-end: understanding the wardrobe,
tracking context (weather, calendar, occasions), turning clothing intent into
real purchases with human approval, tracking deliveries and returns, and
learning from what actually gets worn.

Guiding principle: **the user should not manage Ornatus — Ornatus manages the
wardrobe.**

This is Phase 1. The first real use case is proven end-to-end: asking what
to wear, the agent gathering occasion/weather/wardrobe context through
tools, recommending a real outfit, logging that decision, and recording
feedback. Shopping, purchase approval, deliveries, and returns are
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
| API | `ornatus/api/` | The human-facing surface — a CLI for now. |

Data models for the full domain (wardrobe items, user profile, preferences,
outfit history/recommendations, purchases, deliveries, returns, events,
agent decisions, feedback, agent memory) live in `ornatus/models/`, and the
SQLite schema in `ornatus/persistence/schema.sql` mirrors all of them.
Working slices as of Phase 1: wardrobe, occasion/weather context, outfit
recommendations, agent decisions, and feedback — each with a repository,
service, and (where agent-facing) tools. User profile, preferences (beyond
the model shape), purchases, deliveries, returns, and generic event-log
memory remain schema-only, reserved for later phases.

### The outfit recommendation workflow

    user request
      -> Ornatus agent (Strands)
      -> get_event_context tool  (CalendarService — deterministic/mock)
      -> get_weather tool        (WeatherService — deterministic/mock)
      -> get_wardrobe_items tool (WardrobeService — real SQLite data)
      -> agent reasons over the returned items
      -> record_outfit_recommendation tool (validates item ids, persists OutfitRecommendation)
      -> ornatus.workflows.decision_logging records an AgentDecision (tools used, items selected, outcome)
      -> concise response to the user

Feedback ("I don't want to wear the blazer") follows the same shape: the
agent may look up the wardrobe to resolve which item was meant, then calls
`record_feedback`, which resolves to the user's latest recommendation when
none is given explicitly (feedback commonly arrives as a separate CLI
invocation, so "the latest recommendation" is read from persistence, not
conversation memory).

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
```

With real Bedrock/Nova access (once AWS verification completes), drop the
env var — `bedrock` is the default:

```bash
poetry run ornatus "What should I wear to my client dinner Friday?"
```

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
(`tests/test_local_agent_workflow.py`). `test_agent_smoke.py` makes real
Bedrock calls and is skipped automatically when no AWS credentials are
available.

## Status & what's next

Built in Phase 1:
- Full project structure and layer separation
- Full data/schema layer for the domain model
- Working repositories/services/tools: wardrobe (list/search/get/mark-worn),
  occasion + weather context (deterministic mocks, real-integration-shaped),
  outfit recommendations (validated against real wardrobe items), agent
  decision logging, feedback
- The single orchestrating agent, wired to Bedrock/Nova by default, with a
  deterministic local model for development without AWS
- A small, realistic seed wardrobe and one proven end-to-end scenario
  ("client dinner Friday")
- Tests for all of the above, none requiring AWS

Deferred (deliberately, to stay in scope for this milestone):
- Folding feedback into `Preferences.learned_weights` — feedback is
  recorded, but nothing reads it back into future recommendations yet
- Shopping/purchase workflows, delivery tracking, returns
- Proactive triggers (scheduled prep, calendar/weather-change webhooks) —
  the workflow above is user-initiated only
- Packing/laundry/repair assistance
- Multi-user auth (`current_user_id` is a single configured user)

These land as additional tools/services/workflows behind the same
orchestrator, following the pattern the outfit-recommendation slice
establishes.
