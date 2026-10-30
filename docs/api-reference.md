# API Reference

**Version:** 0.5.0

Public symbols exported from `agenticlens`:

```python
from agenticlens import profile, step, trace, SpanType, SpanHandle, StepHandle
from agenticlens import Run, RunStatus, Span
```

---

## Profiling API

### `profile(name, **kwargs)`

Context manager. Opens a workflow profiling session.

```python
from agenticlens import profile

with profile("My Workflow") as wf:
    ...
# wf.workflow  →  Workflow model
# wf.save("workflow.json")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Human-readable workflow name |
| `**kwargs` | `Any` | Passed to the `Workflow` model as metadata |

**Returns:** `StepHandle` (context manager)

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

### `trace(name, environment, otlp_endpoint, otlp_headers, redactor)`

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
| `name` | `str` | — | Trace name |
| `environment` | `str \| None` | `None` | Environment label (e.g. `"production"`) |
| `otlp_endpoint` | `str \| None` | `None` | OTLP/HTTP endpoint; also reads `AGENTICLENS_OTLP_TRACES_ENDPOINT` |
| `otlp_headers` | `dict \| None` | `None` | Extra OTLP headers; also reads `AGENTICLENS_OTLP_HEADERS` |
| `redactor` | `Callable[[str], str] \| None` | built-in | Custom payload redactor |

**Returns:** `SpanHandle` (context manager)

---

### `SpanHandle`

Returned by `trace()` and `recording.span()`.

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

## Adapters

```python
from agenticlens.adapters.otlp import convert_otlp_to_run
```

Convert an OTLP/HTTP JSON export to an AgenticLens `Run`:

```python
run = convert_otlp_to_run(otlp_payload)
```

Supports OpenTelemetry GenAI semantic conventions and AgenticLens-native attributes.
