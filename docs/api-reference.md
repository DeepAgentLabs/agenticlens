# API Reference (Detailed)

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
| `SpanType.MODEL_CALL` | LLM / model call |
| `SpanType.MEMORY_READ` | Memory lookup |
| `SpanType.MEMORY_WRITE` | Memory update |
| `SpanType.DELEGATION` | Agent handoff / delegation |
| `SpanType.FINAL_RESPONSE` | Final answer generation |
| `SpanType.VALIDATION` | Output validation step |
| `SpanType.RETRY` | Retry of a failed step |
| `SpanType.CUSTOM` | Application-defined span |

---

## Metrics and trace analysis API

Pure functions over a saved structured run (`Run`). They read recorded spans
only; they never call providers. `agenticlens inspect` uses them to build its
report.

```python
from pathlib import Path

from agenticlens.analysis import analyze_trace, next_best_analyses
from agenticlens.analysis.trace import memory_share, retry_token_share
from agenticlens.metrics.trace import (
    latency_by_span_type,
    retry_count,
    tokens_by_span_type,
    tool_call_count,
)
from agenticlens.models.trace import Run

run = Run.model_validate_json(Path("run.json").read_text(encoding="utf-8"))

print(run.total_tokens)                 # input + output tokens across all spans
print(tokens_by_span_type(run))         # {SpanType.PLANNING: 150, SpanType.MEMORY_READ: 80}
print(latency_by_span_type(run))        # milliseconds per span type
print(retry_count(run), tool_call_count(run))
print(memory_share(run), retry_token_share(run))

findings = analyze_trace(run)
for finding in findings:
    print(finding.category, finding.title, finding.span_ids)
print(next_best_analyses(findings))
```

Use the `run.json` saved by the [developer guide quickstart](developer-guide.md#quickstart),
or any run saved with `recording.save()`.

### Run totals

Properties on `Run` (and the matching per-span properties on `Span`):

| Property | Returns |
|----------|---------|
| `run.total_input_tokens` | Sum of span input tokens |
| `run.total_output_tokens` | Sum of span output tokens |
| `run.total_tokens` | Input + output tokens (`span.total_tokens` per span) |

### `agenticlens.metrics.trace`

| Function | Returns |
|----------|---------|
| `tokens_by_span_type(run)` | `dict[SpanType, int]`: total tokens per span type |
| `latency_by_span_type(run)` | `dict[SpanType, float]`: summed latency (ms) per span type |
| `retry_count(run)` | `int`: number of `RETRY` spans |
| `tool_call_count(run)` | `int`: number of `TOOL_CALL` spans |

Span types with no spans are absent from the dictionaries.

### `agenticlens.analysis.trace`

| Function | Returns |
|----------|---------|
| `memory_tokens(run)` | `int`: tokens in `MEMORY_READ` and `MEMORY_WRITE` spans |
| `memory_share(run)` | `float`: memory tokens / total tokens (`0.0` when there are no tokens) |
| `retry_tokens(run)` | `int`: tokens in `RETRY` spans |
| `retry_latency_ms(run)` | `float`: latency of `RETRY` spans |
| `retry_cost_usd(run)` | `float`: estimated cost of `RETRY` spans; spans without a cost count as `0.0` |
| `retry_token_share(run)` | `float`: retry tokens / total tokens |
| `retry_latency_share(run)` | `float`: retry latency / total run latency |
| `retry_attribution(run)` | `dict[str, dict]`: per retry span ID, the `triggering_failure_span_id` and `triggering_failure_type` (parent span if it failed, otherwise the nearest earlier failed span; `None` when none is found) |
| `classify_retry_outcomes(run)` | `dict[str, int]`: counts of `recovered`, `failed` and `unknown` retries, judged from each retry's child spans |
| `duplicated_context_groups(run)` | `list[list[str]]`: groups of span IDs that share the same `input_reference` or identical `input_data` |

`retry_cost_usd` treats missing cost as zero, so it is a lower bound when some
retry spans have no price.

### `analyze_trace(run, *, memory_share_threshold=0.5, retry_share_threshold=0.2, duplicated_context_threshold=2)`

Returns deterministic `Finding` objects. Each finding has `category`, `title`,
`description`, `severity`, `confidence`, `span_ids` and `evidence` pointing at
the spans and measurements that triggered it.

| Category | Raised when |
|----------|-------------|
| `memory` | `memory_share(run)` is above `memory_share_threshold` |
| `retry` | `retry_token_share(run)` is above `retry_share_threshold`; evidence includes retry tokens, latency, cost, outcomes and attribution |
| `context` | A duplicated-context group has at least `duplicated_context_threshold` spans |

### `next_best_analyses(findings)`

Returns follow-up suggestions (`list[str]`) for the categories present in
`findings`, or an empty list when there are none.

### `count_round_trips(transitions)`

From `agenticlens.analysis.handoffs`. Counts non-overlapping agent handoff
round trips (`A→B` immediately followed by `B→A`) in a chronological list of
`(source, target)` pairs:

```python
from agenticlens.analysis.handoffs import count_round_trips

count_round_trips([("planner", "coder"), ("coder", "planner")])  # 1
```

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
