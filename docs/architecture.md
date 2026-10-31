# Architecture

AgenticLens is a layered, local-first toolkit. Each layer has a single
responsibility and strict import boundaries that the test suite enforces.

---

## Layer overview

```
┌──────────────────────────────────────────────────┐
│                   CLI (typer)                    │  agenticlens/cli/
│  profile · analyze · inspect · compare ·         │
│  evaluate · gate · validate · conformance ·      │
│  dashboard · serve-otlp · history · calibrate    │
└────────────────────┬─────────────────────────────┘
                     │ composes
┌────────────────────▼─────────────────────────────┐
│             Analysis & Evaluation                │
│  analysis/ · analyzers/ · evaluation/ ·          │
│  comparison/ · recommenders/ · reports/          │
└────────────────────┬─────────────────────────────┘
                     │ reads
┌────────────────────▼─────────────────────────────┐
│            Instrumentation & Models              │
│  profiler/ · instrumentation/ · models/ ·        │
│  providers/ · metrics/ · exporters/              │
└────────────────────┬─────────────────────────────┘
                     │ reads
┌────────────────────▼─────────────────────────────┐
│             Config & Schemas                     │
│  config/ · schemas/ · validation/                │
└──────────────────────────────────────────────────┘
```

---

## Key components

### Profiler (`profiler/`)

Provides the `profile()` and `step()` context managers. A `profile()` block
becomes a `Workflow` artifact; each `step()` block becomes a `Step`. Token
usage is captured by calling `step.record(provider_response)`, which delegates
to the provider extraction layer.

### Instrumentation (`instrumentation/`)

Provides the `trace()` context manager and `SpanHandle`. A `trace()` block
becomes a `Run` artifact; each `recording.span()` block becomes a `Span`.
Supports explicit `record_tokens()` and `record_io()` with built-in payload
redaction (secrets, bearer tokens, email addresses). Optionally exports to an
OTLP/HTTP collector on trace completion.

### Models (`models/`)

Pydantic data models: `Workflow`, `Step`, `Run`, `Span`, `SpanType`,
`RunStatus`, `ChaosEvent`. All serializable to JSON. Models do not import
from `recommenders/`, `analysis/`, or `cli/`.

### Providers (`providers/`)

Extracts token usage from raw provider responses (OpenAI, Anthropic). No
analysis logic lives here.

### Metrics (`metrics/`)

Calculates cost and performance from workflow steps using live or bundled
pricing data. Pricing data is cached on disk to avoid repeated network
requests.

### Analysis (`analysis/`) and Analyzers (`analyzers/`)

`analysis/` contains memory and retry diagnostics. `analyzers/` contains
modular analyzer implementations. Both read models and produce findings.

### Recommenders (`recommenders/`)

Rule-based optimization suggestions. Each recommender reads a `Workflow` and
returns `Finding` objects. Every finding must include source evidence (step or
span reference, measured value, and threshold). Registered in
`recommenders/engine.py`.

**Default recommenders:**

| Recommender | Signal |
|-------------|--------|
| `PromptRecommender` | Repeated prompt prefixes |
| `RAGChunkUtilityRecommender` | Low-utility retrieved chunks |
| `MemoryRecommender` | Excessive conversation history |
| `ToolRecommender` | Duplicate tool calls |
| `HandoffRecommender` | Oversized multi-agent handoffs |
| `ChaosImpactRecommender` | Unhandled failures and silent degradation from `chaos_events` |

### Evaluation (`evaluation/`)

Deterministic and custom evaluators, versioned test suites (YAML/JSON),
evaluation datasets, judge calibration, and release gate checks. Provider-neutral
through the `EvaluatorRegistry` and normalized `Score` contract.

### Comparison (`comparison/`)

Repeated-run baseline/candidate comparison with regression detection.
Produces JSON or CSV reports with success rate, mean/median/P95 latency, cost,
variability, and relative regression deltas.

### Exporters (`exporters/`)

Serializes workflow data to JSON, CSV, Markdown, Jira wiki markup, and OTLP
JSON. Must not import from `cli/`.

### Reports (`reports/`)

Renders standalone HTML dashboards combining agent timelines, cost breakdowns,
waste findings, release gates, and comparison data. No external fonts or
network requests — fully offline.

### Adapters (`adapters/`)

The `otlp` adapter converts OTLP/HTTP JSON trace exports — including
third-party exports following OpenTelemetry GenAI semantic conventions — into
AgenticLens `Run` artifacts.

### API (`api/`) — optional `[api]` extra

Live OTLP/HTTP receiver and real-time dashboard powered by FastAPI + uvicorn.
Bounded in-memory trace store (default cap 200, FIFO eviction) with an optional
SQLite-backed persistent store (`--db PATH`). Binds to `127.0.0.1` by default;
ships with no authentication.

### Validation (`validation/`)

AIOS draft schema and semantic conformance checks backed by local
`ai-operations-spec` draft schemas.

---

### Optimization (`optimization/`)

Trace-level, cross-run optimization intelligence. Rules read `Run` traces and
return `Opportunity` objects with run/span evidence, a projected benefit and
its basis, confidence with reasons, and separate quality risks. A local ledger
tracks accepted, rejected, adopted, and reverted decisions, and
`evaluate_outcome` compares projected and observed results after adoption.
See [Optimization intelligence](optimization.md).

## Workflow artifact

Artifacts are portable local JSON files. The core format is the
[AI Operations Workflow Specification](workflow-schema-spec.md) v1.1.

```
profile() → workflow.json   (Workflow model)
trace()   → run.json        (Run model, JSON Schema: schemas/trace.schema.json)
evaluate  → evaluation.json (EvaluationReport)
compare   → comparison.json (ComparisonReport)
```

---

## Module boundary rules

| Module | May import from | Must not import from |
|--------|----------------|---------------------|
| `exporters/` | `models/`, `metrics/` | `cli/` |
| `models/` | stdlib, pydantic | `recommenders/`, `analysis/`, `cli/` |
| `providers/` | `models/` | `analysis/`, `recommenders/` |
| `recommenders/` | `models/`, `metrics/` | `cli/` |
| `cli/` | everything | — |

---

## Ecosystem position

AgenticLens is the **OBSERVE / EVALUATE** layer in the DeepAgentLabs ecosystem:

```
agentic-sidecar     →  SUPERVISE (pre-action governance)
agenticlens         →  OBSERVE / EVALUATE (post-run intelligence)
agentic-chaos       →  EXPERIMENT (fault injection)
agentic-evals       →  SCORE / GATE (standalone release gating)
agenticops-control-tower → ORCHESTRATE (fleet inventory and control plane)
deep-agentic-core-mcp    → DELIVER (MCP-native surface)
```

AgenticLens consumes `chaos_events` written by `agentic-chaos`, composes
`agentic-evals` for standalone scoring, and exports to `agenticops-control-tower`
as attributed native evidence.
