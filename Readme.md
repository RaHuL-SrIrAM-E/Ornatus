# Ornatus

*Your wardrobe, quietly taken care of.*

Ornatus is an autonomous personal wardrobe agent. It is not a stylist chatbot —
it manages a person's clothing life end-to-end: understanding the wardrobe,
tracking context (weather, calendar, occasions), turning clothing intent into
real purchases with human approval, tracking deliveries and returns, and
learning from what actually gets worn.

Guiding principle: **the user should not manage Ornatus — Ornatus manages the
wardrobe.**

This is Phase 1: the architectural foundation and a single proven,
tool-driven agent loop. Business workflows (outfit planning, shopping,
purchase approval, deliveries, returns) are intentionally not built yet — see
[Status](#status--whats-next).

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
outfit history, purchases, deliveries, returns, events, agent memory) live in
`ornatus/models/`, and the SQLite schema in
`ornatus/persistence/schema.sql` mirrors all of them — but only the wardrobe
slice (`WardrobeRepository`, `WardrobeService`, `wardrobe_tools`) has a
working implementation. The rest exist as schema/types so the shape of the
system is settled without writing workflow logic that isn't proven yet.

### Why one agent

Strands supports multiple agents (graph/swarm/agent-as-tool), but Phase 1
uses a single orchestrating `Agent` with a growing tool registry, per the
product decision to keep one strong generalist agent rather than several
narrow ones. `build_orchestrator()` in `ornatus/agent/orchestrator.py` is the
one seam where that could change — nothing elsewhere assumes there's only
ever one agent.

### Model provider

`ornatus/agent/model_provider.py` is the only place that knows which model
backend is in use. Phase 1 uses Amazon Bedrock (`BedrockModel`); switching
providers later means adding a branch there, not touching the agent, tools,
or services.

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
  `ORNATUS_BEDROCK_REGION` points), for anything that actually calls the
  model. Everything else (tests, tool/service/repository code) runs without
  AWS.

## Setup

```bash
poetry install
cp .env.example .env   # optional — defaults work as-is
```

## Running the Phase 1 milestone

The milestone proves the full loop: **user request → Ornatus agent → tool
invocation → structured data → agent reasoning → response**, using a
wardrobe-lookup tool backed by real (SQLite) persistence.

```bash
poetry run ornatus "What's in my wardrobe?"
```

On first run this seeds a small sample wardrobe into `ornatus.db` (SQLite,
git-ignored) for a demo user, then asks the agent your question. The agent
calls `get_wardrobe_items`, gets real structured data back, and reasons over
it in its response.

## Testing

```bash
poetry run pytest
```

Repository, service, tool, and orchestrator-wiring tests run without AWS.
One end-to-end test (`tests/test_agent_smoke.py`) makes a real Bedrock call
and is skipped automatically when no AWS credentials are available.

## Status & what's next

Built in Phase 1:
- Full project structure and layer separation
- Full data/schema layer for the domain model
- SQLite persistence abstraction + one working repository (wardrobe)
- One working service (wardrobe) and one working tool
  (`get_wardrobe_items`)
- The single orchestrating agent, wired to Bedrock
- Tests for everything above

Not built yet (by design — see the architecture proposal this phase
followed): outfit planning, shopping/purchase workflows, delivery tracking,
returns, proactive triggers, preference learning, packing/laundry/repair
assistance. These land as additional tools/services/workflows behind the
same orchestrator, following the pattern the wardrobe slice establishes.
