# Workflow Schema Spec

`workflow.json` is the data contract AgenticLens reads with `agenticlens report`
and `agenticlens analyze`, and that other tools — such as
[agentic-chaos](https://github.com/DeepAgentLabs/agentic-chaos) — write to, so
they can share AgenticLens's reporting, costing, and recommendation engine
instead of building their own.

The document is the JSON serialization of the `Workflow` Pydantic model
(`agenticlens.models.Workflow`). Extensions are additive: a producer that adds
a new top-level field does not break older AgenticLens versions, and an
AgenticLens version that doesn't know about a field still reports correctly on
everything it does understand.

## v1.0 — base schema

```json
{
  "id": "uuid",
  "name": "Customer Support Agent",
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-01-01T00:00:18Z",
  "steps": [
    {
      "id": "uuid",
      "name": "Planner",
      "type": "planner",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 850,
        "completion_tokens": 210,
        "total_tokens": 1060,
        "latency": 1.1,
        "ttft": null,
        "cost": 0.02
      },
      "metadata": {}
    }
  ]
}
```

`steps[].type` is one of `planner`, `retriever`, `tool_call`, `llm_call`,
`memory`, `final_response`. `steps[].metadata` is a free-form dict — recommender
rules read specific keys out of it (e.g. `tool_name`/`tool_args` for
`DuplicateToolCallsRecommender`, `chunk_count` for `ExcessiveChunksRecommender`).

## v1.1 — `chaos_events` (fault injection)

Adds one top-level field to `Workflow`:

```json
"chaos_events": [
  {
    "id": "uuid",
    "fault_type": "token_timeout",
    "step_id": "uuid-of-a-step-above",
    "step_name": "Planner",
    "timestamp": "2026-01-01T00:00:05Z",
    "outcome": "errored",
    "message": "human-readable summary of what happened",
    "detail": { "...": "fault-specific fields" }
  }
]
```

Field semantics:

| Field | Type | Required | Notes |
|---|---|---|---|
| `fault_type` | `str` | yes | Producer-defined identifier, e.g. `token_timeout`, `rate_limit_storm`, `silent_degradation`. Not an enum — new fault types don't require an AgenticLens release. |
| `step_id` | `str \| null` | no | Correlates the event to `steps[].id` in the same document. Omit if the fault wasn't attributable to one step. |
| `step_name` | `str \| null` | no | Denormalized step name, used as a fallback label when `step_id` doesn't resolve (e.g. the event was recorded outside of an `agenticlens.step()` block). |
| `outcome` | `str` | yes | How the wrapped call resolved. AgenticLens's `ChaosImpactRecommender` currently assigns severity for `errored` (critical), `degraded` (critical — silent failures are the highest-value class of bug to surface), and `delayed` (warning); any other value is treated as informational. |
| `message` | `str` | recommended | One-line human-readable summary, surfaced directly in recommendation text. |
| `detail` | `dict` | no | Fault-specific structured data (e.g. `hang_seconds`, `retry_after`, `attempt_number`). Not read by AgenticLens today; reserved for future recommender rules. |

`chaos_events` is deliberately typed as `list[dict[str, Any]]` on the
AgenticLens side rather than a strict submodel — AgenticLens has no import-time
dependency on `agentic-chaos` or any other producer. Any tool that appends
well-formed entries to this list gets `ChaosImpactRecommender` support for
free; no AgenticLens code change is required to add a new `fault_type`.

### Multiple events per step

A fault firing on every retry of the same step produces one event per attempt,
all sharing `step_id`. `ChaosImpactRecommender` groups by
`(step, fault_type, outcome)` and reports one recommendation per group with an
occurrence count, rather than one recommendation per event.

## Planned extensions

| Version | Field | Producer | Status |
|---|---|---|---|
| v1.2 | `agent_topology` | agentic-chaos (Agent Failure Injector) | planned |
| v1.3 | drift report fields | agentic-chaos (Drift Detector) | planned |

These will be documented here once their producer module ships. See
[agentic-chaos's roadmap](https://github.com/DeepAgentLabs/agentic-chaos) for
the build order.
