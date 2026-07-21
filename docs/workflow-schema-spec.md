# AI Operations Workflow Specification

This document defines the **AI Operations Workflow Specification** for the
DeepAgentLabs ecosystem.

The specification elevates `workflow.json` from an internal file format to a
versioned, open contract for representing production AI workflow runs,
observability data, evaluation evidence, resilience events, and future
operational metadata.

The long-term architecture is:

```text
Operational model
        |
        v
AI Operations Workflow Specification
        |
        v
Reference implementations
        |
        +-- AgenticLens
        +-- Agentic Chaos
        +-- deep-agentic-core-mcp
```

## Purpose

The specification exists so multiple tools can read and write a shared workflow
artifact rather than inventing incompatible per-tool formats.

Today, the primary producers and consumers are:

- `agenticlens`, which profiles, analyzes, evaluates, and reports on workflows
- `agentic-chaos`, which appends resilience and fault-injection evidence
- `deep-agentic-core-mcp`, which will expose workflow-oriented capabilities
  through a unified MCP surface

Future tools should be able to consume the same contract for dashboards,
pipelines, benchmarks, postmortems, and standards-readiness reporting.

## Naming and Versioning

- Canonical name: `AI Operations Workflow Specification`
- Short name: `Workflow Spec`
- Current version: `v1`
- Current schema baseline: `v1.1`

The serialized artifact remains JSON and is commonly saved as `workflow.json`,
but the file name is not the specification name.

## Design Principles

- **Open and versioned**: the schema should evolve intentionally with published
  versions.
- **Additive by default**: new top-level fields should not break older readers.
- **Tool-independent**: the spec should outlive any single package.
- **Local-first**: artifacts should work well as ordinary files in codebases,
  CI pipelines, and research workflows.
- **Operationally meaningful**: the model should represent real production AI
  system behavior, not only trace spans.

## Compatibility Model

The document is the JSON serialization of the `Workflow` Pydantic model
(`agenticlens.models.Workflow`) plus additive ecosystem extensions.

Compatibility rules:

- a producer may add new top-level fields without breaking older readers
- a reader that does not understand a field should still report correctly on
  the fields it does understand
- extension producers should prefer additive fields over breaking schema
  rewrites

## Workflow Spec v1.0 - Base Schema

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
`memory`, `final_response`. `steps[].metadata` is a free-form dict; downstream
analysis rules may read specific keys from it.

## Workflow Spec v1.1 - `chaos_events`

`v1.1` adds one top-level field to represent fault-injection and resilience
evidence:

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
| --- | --- | --- | --- |
| `fault_type` | `str` | yes | Producer-defined identifier such as `token_timeout`, `rate_limit_storm`, `silent_degradation`. Not an enum. |
| `step_id` | `str \| null` | no | Correlates the event to `steps[].id` in the same document. |
| `step_name` | `str \| null` | no | Fallback label when `step_id` is unavailable or unresolved. |
| `outcome` | `str` | yes | Resolution of the wrapped call, such as `errored`, `degraded`, or `delayed`. |
| `message` | `str` | recommended | One-line human-readable summary. |
| `detail` | `dict` | no | Fault-specific structured data reserved for producer-specific detail and future analysis rules. |

`chaos_events` is deliberately typed loosely on the AgenticLens side so
AgenticLens does not need an import-time dependency on `agentic-chaos` or any
other producer.

## Planned Extensions

These additions are expected to land as future additive versions of the
specification:

| Version | Field | Primary Producer | Status |
| --- | --- | --- | --- |
| v1.2 | `agent_topology` | `agentic-chaos` | planned |
| v1.3 | drift-report fields | `agentic-chaos` | planned |
| v1.x | lineage and provenance fields | `agenticlens` | planned |
| v1.x | evaluation and audit evidence | `agenticlens` | planned |

Each new field family should be documented here once shipped.

## Reference Implementations

The specification is intended to be implemented by the DeepAgentLabs ecosystem:

- `agenticlens` as the flagship observability, evaluation, and operational
  intelligence package
- `agentic-chaos` as the resilience testing and failure-validation package
- `deep-agentic-core-mcp` as the MCP-native interface over shared workflow
  artifacts

## Positioning Guidance

This specification should be described as:

- an open workflow specification
- an AI operations workflow specification
- a versioned operational data contract

It should not be described as an official IEEE specification unless it is
formally incorporated into an approved IEEE standards process.
