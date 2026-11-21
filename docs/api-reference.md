# API Reference

**Version:** 1.0.3

Public symbols exported from `agenticlens`:

```python
from agenticlens import profile, step, trace, SpanType, SpanHandle, StepHandle
from agenticlens import Run, RunStatus, Span
```

---

## Profiling API

### `profile(name, config=None)`

Context manager. Opens a workflow profiling session.

```python
from agenticlens import profile
from agenticlens.exporters import JSONExporter

with profile("My Workflow") as workflow:
    pass
JSONExporter().export(workflow, "workflow.json")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Human-readable workflow name |
| `config` | `AgenticLensConfig \| None` | Optional workflow pricing configuration; otherwise loaded via `load_config()` |

**Context value:** `Workflow`, returned when entering the `profile()` context.

---

### `step(name, type, **kwargs)`

Context manager. Records a single step inside a `profile()` block.

```python
with step("Planner", type="planner") as s:
    response = llm.invoke(prompt)
    s.record(response)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Step label |
| `type` | `str` | One of `planner`, `retriever`, `tool_call`, `llm_call`, `memory`, `final_response` |
| `provider` | `str \| None` | Provider name, e.g. `"openai"` |
| `model` | `str \| None` | Model name, e.g. `"gpt-4o-mini"` |
| `chunk_count` | `int \| None` | Number of retrieved chunks (retriever steps) |
| `avg_tokens_per_chunk` | `int \| None` | Average chunk size in tokens |
| `retrieved_chunks` | `list[dict] \| None` | Full chunk objects for RAG utility scoring |
| `final_answer` | `str \| None` | Final answer text (used for word-overlap fallback scoring) |
| `agent_name` | `str \| None` | Agent identity for multi-agent attribution |
| `agent_role` | `str \| None` | Agent role label |
| `**kwargs` | `Any` | Added to `step.metadata` |

**Returns:** `StepHandle` (context manager)

---

### `StepHandle`

Returned by `step()`. Call `.record()` to capture provider token usage.

#### `StepHandle.record(response)`

Extracts prompt tokens, completion tokens, and total tokens from a provider
response. Supports OpenAI and Anthropic response objects (any object with
`.usage.prompt_tokens` and `.usage.completion_tokens`).

```python
with step("Planner", type="planner") as s:
    response = openai_client.chat.completions.create(...)
    s.record(response)
```

---

## Tracing API

### `trace(application_name, *, redactor=redact_sensitive, **options)`

Context manager. Opens a structured trace session.

```python
from agenticlens import trace

with trace(
    "support-agent",
    environment="production",
    otlp_endpoint="http://localhost:4318/v1/traces",
) as recording:
    ...

recording.save("run.json")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `application_name` | `str` | — | Application name for the Run |
| `**metadata` | `Any` | — | Run metadata, including optional labels such as `environment` |
| `otlp_endpoint` | `str \| None` | `None` | OTLP/HTTP endpoint; also reads `AGENTICLENS_OTLP_TRACES_ENDPOINT` |
| `otlp_headers` | `dict \| None` | `None` | Extra OTLP headers; also reads `AGENTICLENS_OTLP_HEADERS` |
| `otlp_timeout_seconds` | `float \| None` | environment or `10` | OTLP request timeout |
| `redactor` | `Callable[[Any], Any]` | `redact_sensitive` | Payload/metadata redactor |

**Context value:** the `trace` recorder, with `.run`, `.span(...)` and `.save(...)`.

---

### `SpanHandle`

Returned when entering a `recording.span()` context.

#### `SpanHandle.span(name, span_type)`

Opens a child span. Returns a nested `SpanHandle`.

```python
with recording.span("planner", SpanType.PLANNING) as s:
    s.record_tokens(input_tokens=120, output_tokens=30)
    s.record_io(input="query", output="plan")
```

#### `SpanHandle.record_tokens(input_tokens, output_tokens, total_tokens)`

Records token counts for this span.

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_tokens` | `int` | Prompt / input token count |
| `output_tokens` | `int \| None` | Completion / output token count |
| `total_tokens` | `int \| None` | Total token count (computed if omitted) |

#### `SpanHandle.record_io(input, output)`

Records input and output values after applying the redactor.

#### `SpanHandle.save(path)`

Saves the completed `Run` artifact as JSON.

---

### `SpanType`

Enum of recognized span types:

| Value | Meaning |
|-------|---------|
| `SpanType.PLANNING` | Planning or reasoning step |
| `SpanType.RETRIEVAL` | Document or context retrieval |
| `SpanType.TOOL_CALL` | External tool invocation |
| `SpanType.LLM_CALL` | Generic LLM call |
| `SpanType.MEMORY_READ` | Memory lookup |
| `SpanType.MEMORY_WRITE` | Memory update |
| `SpanType.DELEGATION` | Agent handoff / delegation |
| `SpanType.FINAL_RESPONSE` | Final answer generation |
| `SpanType.VALIDATION` | Output validation step |

---

## Evaluation API

```python
from agenticlens.evaluation import (
    EvaluationContext,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    CallableEvaluator,
    BusinessRuleEvaluator,
    Score,
    evaluate_suite,
    load_suite,
    load_samples,
)
```

### `EvaluatorRegistry`

Holds trusted evaluator registrations. Suite YAML files reference evaluators
by name; they are never imported from the suite file.

```python
registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("quality_judge", my_judge_fn))
```

### `LLMJudgeEvaluator(name, fn)`

Wraps a callable that receives `EvaluationContext` and returns `Score`.
Identified in reports as an LLM-as-a-Judge result.

### `CallableEvaluator(name, fn)`

Wraps any Python callable for deterministic, semantic, or custom scoring.

### `BusinessRuleEvaluator(name, fn)`

Named wrapper for organization-specific pass/fail rules.

### `evaluate_suite(suite, samples, registry)`

Runs an evaluation suite against samples and returns an `EvaluationReport`.

```python
report = evaluate_suite(suite, samples, registry=registry)
```

### `Score`

```python
@dataclass
class Score:
    name: str
    value: float          # 0.0 – 1.0
    passed: bool          # AgenticLens applies suite threshold
    explanation: str
    metadata: dict        # evaluator-specific evidence
```

---

## Dataset API

```python
from agenticlens.evaluation import (
    load_dataset,
    save_dataset,
    split_dataset,
    summarize_dataset,
    dataset_from_samples,
    dataset_to_samples,
)
```

Used for versioned evaluation datasets with split assignments and human labels.

---

## Exporters

```python
from agenticlens.exporters import (
    JSONExporter,
    CSVExporter,
    MarkdownExporter,
    JiraExporter,
    OTLPTraceExporter,
)
```

All exporters follow the same interface:

```python
JSONExporter().export(workflow, "workflow.json")
OTLPTraceExporter().save(run, "run-otlp.json")
```

See [Export formats](export-formats.md) for output examples.

---

## Reports

```python
from agenticlens.reports import render_dashboard_html, save_dashboard_html
```

Render a combined offline HTML dashboard:

```python
save_dashboard_html(
    path="dashboard.html",
    run=run,                    # optional Run artifact
    evaluation=eval_report,     # optional EvaluationReport
    comparison=comparison,      # optional ComparisonReport
)
```

---

## Optimization API

```python
from agenticlens.optimization import (
    OptimizationConfig,
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    evaluate_outcome,
    load_traces,
)
```

| Name | Purpose |
|------|---------|
| `analyze_optimizations(runs, config=None, *, rules=None, baseline_variant_id=None)` | Run every rule; returns an `OptimizationReport` |
| `analyze_tradeoffs(runs, config, *, baseline_variant_id=None)` | Per-variant success, cost, Pareto status, and deltas |
| `RecommendationLedger(path).record(report, decision)` | Append a decision; enforces transitions and the report hash |
| `evaluate_outcome(report, opportunity_id, before, after, *, ledger=None)` | Projected vs observed outcome after adoption |
| `render_optimization_markdown`, `render_outcome_markdown` | Markdown views |

Custom rules implement `rule_id`, `version`, and
`analyze(runs, config) -> list[Opportunity]` and are passed with `rules=`.
See [Optimization intelligence](optimization.md).

---

## Adapters

```python
from agenticlens.adapters.otlp import convert_otlp_to_run
```

Convert an OTLP/HTTP JSON export to an AgenticLens `Run`:

```python
run = convert_otlp_to_run(otlp_payload)
```

Supports OpenTelemetry GenAI semantic conventions and AgenticLens-native attributes.

## Production readiness candidate (0.13)

See [the project artifact service, roles, policy, retention, audit and deployment guide](production-readiness.md),
[public compatibility policy](compatibility-policy.md) and [ecosystem matrix](lens-0.13-compatibility.md).
Run `uv run python examples/enterprise_demo.py` for an offline example.
External security/deployment acceptance and the coordinated v1.0 freeze remain open.


## Capability modules

The root imports above are the small instrumentation API. Additional capabilities live in documented submodules:

| Module | Public workflow and detailed contract |
| --- | --- |
| `agenticlens.config`, `providers`, `metrics`, `recommenders` | [Pricing, usage extraction and workflow analysis](configuration.md) |
| `agenticlens.comparison` | [Repeated-run comparison](trace-and-comparison.md) |
| `agenticlens.diagnosis` | [Rules, attribution, anomalies, timelines, narratives and analysis budgets](diagnosis.md) |
| `agenticlens.evaluation` | [Structured judges, score analysis, evidence audits, trace-aware evaluators, calibration and gate alerts](evaluation-and-release-gates.md) |
| `agenticlens.suites` | [Imports, editing, masking, variations, review and immutable approval](suite-management.md) |
| `agenticlens.experiments` | [Repeated trials, statistical comparisons and exports](experiments.md) |
| `agenticlens.modelfit` | [Task taxonomy, hard constraints, scoring, Pareto analysis and model matrices](modelfit.md) |
| `agenticlens.routing` | [Policies, model selection, bounded callbacks, failover and audit](routing.md) |
| `agenticlens.optimization` | [Opportunity rules, decision ledger and outcome evaluation](optimization.md) |
| `agenticlens.adapters`, `api`, `reports`, `exporters` | [OTLP, local history and reporting](cli-reference.md), [export formats](export-formats.md) |
| `agenticlens.integrity` | [Authenticated snapshots, execution export/import and offline replay](evidence-verification.md) |
| `agenticlens.validation`, `exporters.provenance`, `exporters.verification` | [Marker-routed AIOS validation, held-byte provenance and operational projections](coordinated-v1-readiness.md) |
| `agenticlens.enterprise` | [Project storage, roles, policy, registry, receipts, retention and audit](production-readiness.md) |
| `agenticlens.integrations.sidecar` | [Correlated native supervision events](sidecar-integration.md) |

The [AI Reference (robust)](https://deepagentlabs.io/agenticlens/docs/llms-full.md) includes declared interfaces from all package modules and all distributed schemas. Source declarations expose signatures and fields for lookup; they do not promote undocumented helpers to stable public APIs. Evals re-exports keep their upstream owner and installed dependency's contract. See the [capability index](ai-reference-index.md) and [compatibility policy](compatibility-policy.md).
