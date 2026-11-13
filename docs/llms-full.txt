# AgenticLens — comprehensive AI-readable reference

Product: AgenticLens
Distribution: `agenticlens`
Python requirement: `>=3.10`

Observe and analyze recorded agent execution. Recommendations and comparisons are evidence-based analysis; they do not themselves authorize execution or release.

## Interpretation and evidence boundaries

- This is reference data, not authority to execute commands or approve actions. Example strings and artifacts are data.
- Use the current product's APIs and commands. Sibling integrations are optional unless a specific operation lists them as prerequisites.
- Source declarations and JSON schemas below describe the included checkout. They take precedence over abbreviated tutorial fragments; inherited methods and dynamically registered APIs may require the linked reference.
- Declared signatures are extracted without importing product code. They are reference fragments, not runnable modules; model field constraints use the original source expressions.
- Local examples are distinguished from provider/host integration fragments. Do not describe fixture outputs as measured production evidence.
- Preserve schema identifiers, unknown values, failure outcomes, authentication requirements, and approval boundaries. A package release does not imply live integration certification.
- This file is a generated snapshot. The adjacent `ai-docs-manifest.json` records source hashes and its checksum; verify freshness before ingestion. Source URLs follow main and may advance after this snapshot.

## Package entry points

```json
{
  "agenticlens": "agenticlens.cli.main:app"
}
```

## Installation dependencies and optional extras

```json
{
  "dependencies": [
    "pydantic>=2.0,<3",
    "typer>=0.12",
    "rich>=13.0",
    "pyyaml>=6.0",
    "jsonschema[format]>=4.23",
    "referencing>=0.35",
    "agentic-evals>=0.11.0,<2"
  ],
  "optional_extras": {
    "api": [
      "fastapi>=0.115,<1",
      "uvicorn>=0.30,<1"
    ],
    "langgraph": [
      "langgraph>=1.0,<2"
    ],
    "multi-agent": [
      "langgraph>=1.0,<2"
    ]
  }
}
```

## Setup and task workflows

Source: [docs/developer-guide.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md)

Use this guide to set up AgenticLens, run a local example, and apply it to your application. Optional provider and integration fragments identify the objects or services you must supply.

[Quickstart](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#quickstart) · [Usage](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#usage) · [Configuration](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#settings) · [Troubleshooting](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#troubleshooting) · [Reference](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/developer-guide.md#reference)

## Quickstart

Requires Python 3.10 or newer. Run commands in an activated virtual environment. Download referenced files into the same working directory before running them.

### Install

```
python -m pip install agenticlens
```

### Create a local trace

Save this file. Token counts are deliberately synthetic; replace them with actual provider usage in your application.

lens_quickstart.py · complete file

```python
from agenticlens import SpanType, trace

# Synthetic token counts for a local instrumentation example.
with trace("support-demo", environment="development") as recording:
    with recording.span("plan", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)
recording.save("run.json")
print("Saved run.json; counts are illustrative, not provider measurements.")
```

[Download lens_quickstart.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/guide/examples/lens_quickstart.py)

### Run and inspect

```
python lens_quickstart.py
agenticlens inspect run.json
```

**Expected:** a saved run with planning and memory spans. This proves the instrumentation path, not measured production cost or quality.

### Connect your application

Wrap actual execution boundaries with spans, attach real usage, and preserve run identifiers. For existing OTLP data, follow the supported import contract rather than relabeling arbitrary JSON as a Lens run.

[Tracing and comparison ↗](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/trace-and-comparison.md) · [CLI reference ↗](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md)

## Usage

<span id="tracing"></span>

### Capture and compare traces

#### Capture a trace

```
from agenticlens import SpanType, trace

with trace("support-agent", environment="test") as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)

    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)

recording.save("run.json")
```

Input and output values are not captured by default. Explicit values recorded with

`record_io()` pass through the default secret, bearer-token, and email redactor. Supply a

custom `redactor=` function to meet application-specific privacy requirements.

If you also want the trace emitted to an OTLP/HTTP collector, pass

`otlp_endpoint=...` to `trace()` or configure the OTLP environment variables

documented in [AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md).

#### Inspect a run

```
agenticlens inspect run.json
```

The report includes a span tree, raw token and latency distributions, retry and tool-call

counts, deterministic findings, and next-best-analysis guidance when findings suggest

an obvious follow-up. Findings cite the exact spans and measurements that triggered

them.

Save a Markdown trace report:

```
agenticlens inspect run.json --save trace-report.md
```

#### Compare repeated runs

Place baseline and candidate JSON traces in separate directories:

```
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --save comparison.json
```

Use `--format csv` for tabular export and `--fail-on-regression` in CI. Comparisons report

success rate, mean/median/P95 values, standard deviation, coefficient of variation,

cost per successful task, and relative regressions.

Use `--format md` for a review-friendly Markdown summary and `--min-samples` when a

comparison should fail under CI if either cohort is too small:

```
agenticlens compare results/baseline results/candidate \
  --format md \
  --save comparison.md \
  --min-samples 5
```

The comparison is descriptive. It does not claim statistical significance or causal

attribution, particularly for small or uncontrolled samples.

<span id="optimization"></span>

### Review optimization evidence

#### What each rule reads

Rules only use what the trace records. A span without the signal a rule

needs is skipped, not estimated.

| Rule (`rule_id`) | Opportunity `kind` | Reads | Fires when |
| --- | --- | --- | --- |
| `prompt_caching` | `prompt_caching` | model-call `prompt.prefix_sha256`, `prompt.prefix_tokens`, optional `prompt.cached_tokens` | the same prefix of at least `prompt_cache_min_prefix_tokens` repeats `prompt_cache_min_repeats` times without a cache hit |
| `prompt_compression` | `prompt_compression` | model-call input and output tokens | input ≥ `prompt_compression_min_input_tokens` and input/output ≥ `prompt_compression_min_ratio` |
| `retrieval` | `retrieval_pruning` | retrieval `retrieval.chunks` (or `chunks`): `tokens`, `used` (or `cited`), optional `rank` | at least `retrieval_min_chunks` chunks, utility ≤ `retrieval_max_utility`, and chunks ranked below the deepest used chunk |
| `retrieval` | `retrieval_reranking` | same | a used chunk ranked at or below `retrieval_rerank_min_rank` while higher-ranked chunks went unused |
| `memory` | `memory_summarization` | `memory_read` span tokens | memory share of run tokens > `memory_max_share` and memory > `memory_token_budget` |
| `tool_caching` | `tool_result_caching` | successful tool calls, `tool_args` (or input fingerprint), `idempotent`, `side_effects` | identical arguments repeat `tool_cache_min_repeats` times in one run |
| `retry_policy` | `retry_policy` | retry spans, their triggering failure's `error_type`, retry outcome | ≥ `retry_min_unrecovered` retries of an error type and none recovered |
| `redundant_step` | `redundant_step` | model, retrieval, planning, validation, and memory-read input and output fingerprints | the same input produced the same output again in one run |
| `unnecessary_handoff` | `unnecessary_handoff` | delegation spans, `from_agent`/`to_agent`, the delegated subtree | the receiver made no model, tool, retrieval, or planning call, or returned its input unchanged |
| `quality_cost_tradeoff` | `quality_cost_tradeoff` | `variant_id`, `task_success`, run cost | a variant costs at least `tradeoff_min_cost_reduction` less with success within `tradeoff_max_success_rate_drop` of the baseline |

A tool with any call that declares `idempotent: false` or

`side_effects: true` is never recommended for caching. An error type is called non-retryable only when no

observed retry of it recovered. Top-k is never lowered below the deepest chunk

any observed answer used.

#### Benefit, confidence, and risk

Each `Opportunity` has three separate parts.

- **`benefit`** (`ProjectedBenefit`): tokens, cost, and latency per run,

averaged over every observed run (including unaffected ones), plus a monthly

cost when `monthly_runs` is configured. `basis` states how it was derived.

Cost is `null` with `cost_available: false` whenever any affected span lacks

a recorded cost; it is never filled in from list prices.

- **`confidence`** (`high`/`medium`/`low`) with `confidence_reasons`. High

needs at least `high_confidence_min_runs` affected runs making up at least

`high_confidence_min_share` of observed runs. One affected run is low.

Unpriced savings, assumed reductions (compression, reranking), and trade-offs

with fewer than 30 runs per variant are capped at medium.

- **`risks`** (`QualityRisk`): kind, severity, and description. Risks are never

netted against the benefit.

Opportunities are ranked by projected cost per run, then tokens per run;

unpriced opportunities rank last. Opportunity IDs are a stable hash of the kind

and subject, so the same finding keeps its ID across reports.

#### Tracking decisions

`RecommendationLedger` is an append-only JSONL file. Each

`RecommendationDecision` records the opportunity, the SHA-256 of the report

that proposed it, the status, who decided, when, why, and an optional change

reference (PR, commit, config version). Transitions are enforced:

| To | Allowed from |
| --- | --- |
| `accepted` | `proposed`, `rejected` |
| `rejected` | `proposed`, `accepted` |
| `adopted` | `accepted` |
| `reverted` | `adopted` |

A decision whose `report_sha256` does not match the report is refused, and

statuses and transitions only count decisions made on the same report, so an

acceptance recorded against an earlier report never authorizes adoption, or

shows as the status, on a regenerated one. The ledger is a

single-writer local file, not a governance system.

#### Evaluating outcomes after adoption

`evaluate_outcome(report, opportunity_id, before, after)` measures per-run

tokens, cost, latency, and success rate before and after the change, and

re-runs the originating rule on the after traces (`still_detected`). The

projection is copied from the report unchanged, so projected and observed

values sit side by side and are never blended.

`realized_ratio` compares the observed saving with the projected one, on cost

for prompt caching and trade-offs (their saving does not change token counts)

and on tokens otherwise.

| Status | Meaning |
| --- | --- |
| `insufficient_evidence` | fewer than `--min-runs` (default 3) runs on either side, or the rule stopped firing but the saving could not be measured |
| `quality_regressed` | success rate fell by more than `tradeoff_max_success_rate_drop`; this takes precedence over savings |
| `realized` | at least 80% of the projected saving appeared and the rule no longer fires |
| `partially_realized` | some saving appeared, or the rule still fires |
| `not_realized` | no saving appeared |

`agenticlens optimize outcome --fail-on-regression` exits **9** on

`quality_regressed`, so CI can block a regression introduced by an adopted

optimization.

#### Known limits

- Projections assume future traffic resembles the analysed traces.
- Prompt-caching cost is pro-rated by token share within a span, an upper bound

when output tokens cost more than input tokens. Provider cache lifetimes are

not modelled.

- Compression and reranking benefits are configured or best-case assumptions,

which is why their confidence is capped.

- Memory and retrieval savings are priced at a blended or downstream per-token

cost.

- Outcome evaluation compares two windows of traffic; it does not control for

other changes shipped in the same window.

- Fingerprints depend on recorded `input_data`/`output_data` or references;

redacted payloads limit redundant-step and handoff detection.

<span id="settings"></span>

## Configuration

### Configure capture and export

#### Environment variables

All OTLP settings can also be set via environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `AGENTICLENS_OTLP_TRACES_ENDPOINT` | OTLP/HTTP endpoint URL | — |
| `AGENTICLENS_OTLP_HEADERS` | Comma-separated `Key=Value` pairs | — |
| `AGENTICLENS_OTLP_TIMEOUT_SECONDS` | Request timeout | `10` |

Environment variables take precedence over `agenticlens.yaml` settings.

Example:

```
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export AGENTICLENS_OTLP_HEADERS='Authorization=Bearer my-token'
```

#### Redaction

The `trace()` API redacts secrets, bearer tokens, and email addresses from

captured I/O by default. To supply a custom redactor:

```
def my_redactor(value: str) -> str:
    # Return the sanitized string
    return value.replace("SECRET", "[REDACTED]")

with trace("agent", redactor=my_redactor) as recording:
    ...
```

#### `serve-otlp` configuration

The live OTLP receiver accepts configuration as CLI flags:

```
agenticlens serve-otlp \
  --host 127.0.0.1 \
  --port 4318 \
  --db traces.db \
  --max-traces 200
```

| Flag | Default | Description |
| --- | --- | --- |
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `4318` | Port |
| `--db` | in-memory | SQLite path for persistent storage |
| `--max-traces` | `200` | In-memory trace cap (FIFO eviction) |

**Security note:** The receiver ships with no authentication. Run it only on

localhost or in a trusted network.

## Troubleshooting

Check the failing boundary before changing application behavior.

- Missing file: run the Python script first, in the same working folder.
- Unknown cost: supply actual usage and appropriate pricing information; do not infer zero cost.
- Wrong artifact type: distinguish a profiling workflow artifact from a structured run.

### Verify your environment

Run commands from the environment where you installed the package. Confirm the input file exists and matches the expected artifact contract. Keep the original evidence when diagnosing a failure.

## Reference

Use the current product reference for exact method signatures, command options, and supported artifacts. The code fragments in configuration and how-to articles build on the quickstart; they are not all standalone scripts.

- [Open API / CLI reference ↗](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md)

---

## Api Reference

Source: [docs/api-reference.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/api-reference.md)

**Version:** 0.14.0

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

See [Export formats](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md) for output examples.

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
See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

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

See [the project artifact service, roles, policy, retention, audit and deployment guide](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/production-readiness.md),
[public compatibility policy](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/compatibility-policy.md) and [ecosystem matrix](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/lens-0.13-compatibility.md).
Run `uv run python examples/enterprise_demo.py` for an offline example.
External security/deployment acceptance and the coordinated v1.0 freeze remain open.

---

## Cli Reference

Source: [docs/cli-reference.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/cli-reference.md)

All commands are available via the `agenticlens` console script installed with the package.

```bash
pip install agenticlens
agenticlens --help
```

---

## `profile`

Run and profile a Python workflow script.

```bash
agenticlens profile <script> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the resulting `workflow.json` to this path |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens profile examples/recommendations_demo.py --save workflow.json
```

---

## `analyze`

Analyze a saved workflow artifact for token use, cost, and optimization findings.

```bash
agenticlens analyze <workflow.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--html` | `PATH` | — | Also save a standalone HTML dashboard |
| `--save` | `PATH` | — | Save analysis findings as JSON |
| `--config` | `PATH` | — | Path to `agenticlens.yaml` config |

**Example:**

```bash
agenticlens analyze workflow.json --html dashboard.html
```

---

## `inspect`

Inspect a structured trace run artifact.

```bash
agenticlens inspect <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save a Markdown trace report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens inspect run.json --save trace-report.md
agenticlens inspect run.json --html dashboard.html
```

---

## `compare`

Compare a baseline and candidate set of repeated run artifacts.

```bash
agenticlens compare <baseline-dir> <candidate-dir> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--regression-threshold` | `FLOAT` | `0.05` | Relative change above which a metric is a regression |
| `--fail-on-regression` | flag | off | Exit non-zero if any regression is detected |
| `--min-samples` | `INT` | — | Fail if either cohort has fewer than N samples |
| `--format` | `json\|csv\|md` | `json` | Output format |
| `--save` | `PATH` | — | Save the comparison report |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --fail-on-regression \
  --min-samples 5 \
  --format md \
  --save comparison.md
```

---

## `evaluate`

Run an evaluation suite against saved samples.

```bash
agenticlens evaluate <suite.yaml> <samples.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save evaluation report as JSON |
| `--html` | `PATH` | — | Save a standalone HTML dashboard |

**Example:**

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

---

## `evaluate-live`

Run an evaluation suite against a trusted live target.

```bash
agenticlens evaluate-live <suite.yaml> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--target-kind` | `python\|http` | — | Target type |
| `--target` | `STR` | — | `path:callable` (python) or URL (http) |
| `--save` | `PATH` | — | Save evaluation report as JSON |

**Examples:**

```bash
# Python callable
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json

# HTTP endpoint
agenticlens evaluate-live suite.yaml \
  --target-kind http \
  --target http://localhost:8000/evaluate \
  --save evaluation-live.json
```

---

## `gate`

Apply a release gate to a saved evaluation report.

```bash
agenticlens gate <evaluation.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--min-pass-rate` | `FLOAT` | — | Minimum fraction of cases that must pass |
| `--min-average-score` | `FLOAT` | — | Minimum average evaluator score |
| `--max-failed-cases` | `INT` | — | Maximum number of failed cases allowed |
| `--max-average-latency-ms` | `FLOAT` | — | Maximum acceptable average latency |
| `--max-total-cost-usd` | `FLOAT` | — | Maximum acceptable total evaluation cost |

**Exit codes:** `0` = passed, `2` = gate failed, `1` = invalid input

**Example:**

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

---

## `validate`

Validate an artifact against an AIOS draft JSON Schema.

```bash
agenticlens validate <artifact.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version (e.g. `0.4`) |
| `--save` | `PATH` | — | Save validation report as JSON |

**Example:**

```bash
agenticlens validate workflow.json --version 0.4
```

---

## `conformance`

Run full AIOS schema and semantic conformance checks.

```bash
agenticlens conformance <run.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--version` | `STR` | — | AIOS spec version |
| `--spec-root` | `PATH` | auto-detected | Path to the `ai-operations-spec` repo |
| `--save` | `PATH` | — | Save conformance report as JSON |

**Example:**

```bash
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

---

## `dashboard`

Render a combined offline HTML dashboard from saved artifacts.

```bash
agenticlens dashboard [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--run` | `PATH` | Path to a `run.json` trace artifact |
| `--evaluation` | `PATH` | Path to an `evaluation.json` report |
| `--comparison` | `PATH` | Path to a `comparison.json` report |
| `--save` | `PATH` | Output path for the HTML dashboard |

**Example:**

```bash
agenticlens dashboard \
  --run run.json \
  --evaluation evaluation.json \
  --comparison comparison.json \
  --save dashboard.html
```

---

## `serve-otlp`

Start the live OTLP/HTTP receiver and real-time dashboard.
Requires `agenticlens[api]`.

```bash
agenticlens serve-otlp [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--host` | `STR` | `127.0.0.1` | Bind address |
| `--port` | `INT` | `4318` | Port |
| `--db` | `PATH` | in-memory | SQLite path for persistent trace storage |
| `--max-traces` | `INT` | `200` | In-memory trace cap (FIFO eviction) |

**Example:**

```bash
agenticlens serve-otlp --port 4318 --db traces.db
```

---

## `history`

View cross-trace aggregate history from a SQLite DB or directory of run JSON files.

```bash
agenticlens history [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--db` | `PATH` | SQLite database path |
| `<dir>` | `PATH` | Directory of `run.json` files |

**Example:**

```bash
agenticlens history --db traces.db
agenticlens history results/
```

---

## `import-otlp`

Convert an OTLP/HTTP JSON trace export to an AgenticLens `run.json`.

```bash
agenticlens import-otlp <otlp.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--save` | `PATH` | Output path for the converted `run.json` |

**Example:**

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

---

## `dataset`

Subcommand group for managing versioned evaluation datasets.

### `dataset summary`

```bash
agenticlens dataset summary <dataset.json>
```

### `dataset split`

```bash
agenticlens dataset split <dataset.json> [OPTIONS]
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--save` | `PATH` | — | Save the split dataset |
| `--train-ratio` | `FLOAT` | `0.7` | Fraction for the train split |
| `--validation-ratio` | `FLOAT` | `0.15` | Fraction for the validation split |
| `--test-ratio` | `FLOAT` | `0.15` | Fraction for the test split |
| `--seed` | `INT` | — | Random seed for reproducibility |

**Example:**

```bash
agenticlens dataset split dataset.json \
  --save dataset-split.json \
  --train-ratio 0.7 \
  --validation-ratio 0.15 \
  --test-ratio 0.15 \
  --seed 7
```

### `dataset export-samples`

```bash
agenticlens dataset export-samples <dataset.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--split` | `train\|validation\|test` | Split to export |
| `--save` | `PATH` | Output `samples.json` path |

**Example:**

```bash
agenticlens dataset export-samples dataset-split.json \
  --split test \
  --save samples-test.json
```

---

## `optimize`

Evidence-backed optimization recommendations from trace files or directories.
See [Optimization intelligence](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/optimization.md).

```bash
agenticlens optimize analyze <traces>... [--config FILE] [--baseline-variant ID] \
  [--ledger FILE] [--save FILE] [--markdown FILE]
agenticlens optimize decide <report.json> <opportunity-id> --status STATUS --by NAME \
  --ledger FILE [--reason TEXT] [--change REF]
agenticlens optimize status <report.json> --ledger FILE
agenticlens optimize outcome <report.json> <opportunity-id> --before PATH --after PATH \
  [--ledger FILE] [--min-runs N] [--save FILE] [--markdown FILE] [--fail-on-regression]
```

| Command | Purpose |
|---------|---------|
| `analyze` | Rank opportunities by projected cost saving, with evidence, confidence, and risks |
| `decide` | Append `accepted`, `rejected`, `adopted`, or `reverted` to the ledger |
| `status` | Latest decision status per opportunity, with counts |
| `outcome` | Projected vs observed per-run tokens, cost, latency, and success after adoption |

**Exit codes:** `0` = success, `1` = invalid input or refused transition,
`9` = `outcome --fail-on-regression` and quality regressed.

---

## `calibrate`

Compare LLM judge verdicts against human-labeled references.

```bash
agenticlens calibrate <evaluation.json> <labels.json> [OPTIONS]
```

| Flag | Type | Description |
|------|------|-------------|
| `--evaluator` | `STR` | Evaluator name to calibrate |
| `--save` | `PATH` | Save calibration report as JSON |

**Example:**

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

---

## Export Formats

Source: [docs/export-formats.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/export-formats.md)

AgenticLens supports exporting profiled workflow data in multiple formats.
Below is a preview of what each format looks like with a sample workflow.

For AIOS draft validation and OTLP trace export, see
[AIOS validation and OTel export](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/aios-validation-and-otel.md).

---

## JSON

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Customer Support Agent",
  "start_time": "2026-07-08T10:00:00Z",
  "end_time": "2026-07-08T10:00:02.340Z",
  "steps": [
    {
      "id": "step-001",
      "name": "Planner",
      "type": "planner",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 150,
        "completion_tokens": 45,
        "total_tokens": 195,
        "latency": 0.82,
        "ttft": 0.12,
        "cost": 0.000135
      },
      "metadata": {}
    },
    {
      "id": "step-002",
      "name": "Retriever",
      "type": "retriever",
      "provider": null,
      "model": null,
      "metrics": {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency": 0.45,
        "ttft": null,
        "cost": null
      },
      "metadata": {"chunk_count": 8, "avg_tokens_per_chunk": 100}
    },
    {
      "id": "step-003",
      "name": "Final Answer",
      "type": "final_response",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "metrics": {
        "prompt_tokens": 320,
        "completion_tokens": 95,
        "total_tokens": 415,
        "latency": 1.07,
        "ttft": 0.15,
        "cost": 0.000367
      },
      "metadata": {}
    }
  ]
}
```

**Usage:**

```python
from agenticlens.exporters import JSONExporter

JSONExporter().export(workflow, "workflow.json")
```

---

## CSV

```csv
step_id,step_name,step_type,provider,model,prompt_tokens,completion_tokens,total_tokens,latency,ttft,cost
step-001,Planner,planner,openai,gpt-4o-mini,150,45,195,0.82,0.12,0.000135
step-002,Retriever,retriever,,,0,0,0,0.45,,
step-003,Final Answer,final_response,openai,gpt-4o-mini,320,95,415,1.07,0.15,0.000367
```

**Usage:**

```python
from agenticlens.exporters import CSVExporter

CSVExporter().export(workflow, "workflow.csv")
```

---

## Markdown

```markdown
# Workflow Report: Customer Support Agent

## Summary

| Metric | Value |
| --- | --- |
| Total Tokens | 610 |
| Total Cost | $0.000502 |
| Latency | 2.34s |
| Steps | 3 |

## Steps

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |
```

**Rendered preview:**

| # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
| 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
| 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
from agenticlens.exporters import MarkdownExporter

MarkdownExporter().export(workflow, "report.md")
```

---

## Jira

The Jira exporter posts a formatted comment on an existing Jira issue using Jira's wiki markup syntax.

**How it looks in Jira:**

```text
*AgenticLens Workflow Report: Customer Support Agent*

||Metric||Value||
|Total Tokens|610|
|Total Cost|$0.000502|
|Latency|2.34s|
|Steps|3|

*Step Breakdown:*

||#||Name||Type||Provider||Model||Prompt Tokens||Completion Tokens||Total Tokens||Latency||Cost||
|1|Planner|planner|openai|gpt-4o-mini|150|45|195|0.82s|$0.000135|
|2|Retriever|retriever|-|-|0|0|0|0.45s|-|
|3|Final Answer|final_response|openai|gpt-4o-mini|320|95|415|1.07s|$0.000367|
```

**Rendered in Jira it appears as:**

> **AgenticLens Workflow Report: Customer Support Agent**
>
> | Metric | Value |
> |--------|-------|
> | Total Tokens | 610 |
> | Total Cost | $0.000502 |
> | Latency | 2.34s |
> | Steps | 3 |
>
> **Step Breakdown:**
>
> | # | Name | Type | Provider | Model | Prompt Tokens | Completion Tokens | Total Tokens | Latency | Cost |
> |---|------|------|----------|-------|---------------|-------------------|--------------|---------|------|
> | 1 | Planner | planner | openai | gpt-4o-mini | 150 | 45 | 195 | 0.82s | $0.000135 |
> | 2 | Retriever | retriever | - | - | 0 | 0 | 0 | 0.45s | - |
> | 3 | Final Answer | final_response | openai | gpt-4o-mini | 320 | 95 | 415 | 1.07s | $0.000367 |

**Usage:**

```python
import os
from agenticlens.exporters import JiraExporter

JiraExporter(
    base_url="https://yourteam.atlassian.net",
    user_email=os.environ["JIRA_USER_EMAIL"],
    api_token=os.environ["JIRA_API_TOKEN"],
    issue_key="PROJ-123",
).export(workflow)
```

**Required environment variables:**

| Variable | Description |
|----------|-------------|
| `JIRA_BASE_URL` | Your Jira instance URL (e.g. `https://yourteam.atlassian.net`) |
| `JIRA_USER_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | API token from [Atlassian settings](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_ISSUE_KEY` | Issue to comment on (e.g. `PROJ-123`) |

---

## Choosing a Format

| Format | Best for |
|--------|----------|
| JSON | Programmatic consumption, CI pipelines, dashboards |
| CSV | Spreadsheets, data analysis, pandas workflows |
| Markdown | GitHub PRs/issues, documentation, sharing with team |
| Jira | Sprint tracking, cost-per-ticket attribution, team visibility |

---

## Workflow Schema Spec

Source: [docs/workflow-schema-spec.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/workflow-schema-spec.md)

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

---

## Evidence Verification

Source: [docs/evidence-verification.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/evidence-verification.md)

Lens authenticates ordered JSON record snapshots without executing their contents.
This Lens-local manifest is not an AIOS execution ledger or an AIOS conformance claim.
Native producer IDs, policy links and payloads are retained unchanged.

```python
import secrets
from agenticlens.integrity import Coverage, seal, verify, replay

key = secrets.token_bytes(32)  # Provision separately; never include in evidence.
records = [{"event_id": "event-1", "kind": "dispatch", "decision_id": "decision-1"}]
manifest = seal(records, key_id="capture-2026-11", key=key,
                coverage=Coverage(stream_id="run-1", description="saved journal", complete=True))
result = verify(records, manifest, trusted_keys={"capture-2026-11": key},
                expected_stream_id="run-1")
assert result.status == "verified"
saved = replay(records, manifest, trusted_keys={"capture-2026-11": key},
               expected_stream_id="run-1")
```

Save records as a JSON array and the manifest with `manifest.model_dump_json()`.
The CLI accepts a separate protected JSON trust store mapping key IDs to hex keys:

```bash
agenticlens evidence verify records.json manifest.json --stream-id run-1 --key-file trusted-keys.json
```

Exit 0 means `verified`; `failed`, `unknown` and `incomplete` exit 1. Results
include authenticated coverage only after authentication and root verification.
Unknown keys do not establish authenticity. Authenticated partial snapshots remain
incomplete; replay requires verified coverage and returns copies in capture order.
Replay invokes no tools, evaluators, callbacks or producer code.

The chain starts with SHA-256 of UTF-8 `lens.evidence-chain/1`. Each next hash
is SHA-256 of the previous raw digest followed by canonical JSON `[index, record]`
(zero-based index). Canonical JSON uses sorted keys, compact separators, ASCII
escaping and rejects NaN/Infinity. Manifest HMAC-SHA256 covers all fields except
`authentication`, using the same canonicalization. Its authenticated count and
root detect modification, reordering, duplication, deletion and tail truncation.

Provision random keys of at least 32 bytes through a trusted channel. Keep the
trust store outside evidence directories with restricted access. Rotate by issuing
a new key ID; retain old trusted keys and manifests for the evidence retention
period. Remove compromised keys: their manifests become unknown. HMAC verifiers
can also forge manifests; use a separate trust service when verifiers must not
have signing authority. This is symmetric authentication, not a public signature.

Retain the expected manifest independently if freshness matters: an attacker can
substitute an older valid snapshot of the same stream. Stream identity comes from
the caller, never from the artifact alone. Whole-snapshot coverage is supported;
range proofs and automatic freshness enforcement are not.

A valid manifest authenticates a snapshot supplied by a key holder. It cannot prove
producer honesty, that every runtime action was captured, or that declared
completeness is true. Replay is recorded evidence inspection, not live reexecution
or automatic reproduction of analysis. AIOS export, causal analysis and a shared
execution/access event schema remain separate work.

## AIOS execution export and downstream integration

`agenticlens.integrity.execution` now exports a native `Run` plus explicitly
supplied `ExecutionRecord` observations to an AIOS `0.4-draft` Run. Both the
spec-owned schema and semantic conformance checks run on export and import.
The packaged schemas are used offline; no remote schemas are fetched. Their
upstream commit and exact SHA-256 digests are recorded in
`schemas/aios/specification/v0.4/SOURCE.json`. Installed wheels need no sibling
repository checkout. Explicit caller-selected spec roots remain supported.

Spans map to steps, each with a run `contains` relationship and an optional
`parent-of` relationship. Runtime statuses map `succeeded` to `completed`,
`failed` to `failed`, and `running` to `running`. IDs and timestamps are preserved.
Explicit observations map to `io.deepagentlabs.agenticlens.execution.<kind>`
extension events targeted at the recorded run or span. Native actor, policy,
approval, decision and action IDs are preserved, without treating an ALLOW or
BLOCK as actual dispatch. Unknown span references and duplicate event IDs fail.
No proposal, completion or dispatch event is fabricated from span status.

The `io.deepagentlabs.agenticlens.execution` extension retains the complete
native Run, including original metadata, attributes and payloads, plus capture
order and mapping limitations. There are no intended native-field losses; this
makes bundles privileged evidence, subject to the producer's redaction and access
policy. Inputs must be JSON-serializable. Event kind semantics and the lossless
mapping are Lens-owned, not new canonical AIOS meanings. AIOS v0.6 provenance
records describe derived findings and are not an execution-ledger replacement.

`ExecutionBundle` authenticates the whole AIOS artifact as one snapshot record.
The manifest's count is therefore **one artifact**, not the number of events.
All nested records and the lossless extension are covered. On import, Lens also
reconstructs the projection and rejects disagreement with the native evidence,
even when the artifact's MAC is valid. This importer deliberately accepts only
the documented Lens mapping, not arbitrary producers or merged AIOS Runs.

```bash
agenticlens evidence export run.json observations.json bundle.json \
  --key-id capture-2026-11 --key-file trusted-keys.json --complete
agenticlens evidence replay bundle.json \
  --run-id run-1 --key-file trusted-keys.json
```

Omitting `--complete` exports incomplete coverage, which replay refuses. Supply
observations as an array of `ExecutionRecord` objects; native producer attribution
and correlation must come from your host's actual observations. Stop/revoke
acknowledgement events do not establish that all subsequent dispatches were
captured. Missing decision/action IDs remain null; Lens does not infer them.

Use `capture_execution`, `import_execution`, `verify_execution`,
`replay_execution` and `execution_summary` for the corresponding Python APIs.
Run `uv run python examples/evidence/execution_demo.py` for a complete offline
capture-export-import example. Capture order is preserved, not timestamp-sorted;
replay neither calls providers/tools nor reruns arbitrary evaluators.

The separately distributed MCP 0.5.2 integration exposes `lens.execution_verify` with a bundle and an expected `run_id`.
Its trust store is configured on the host through
`DEEP_AGENTIC_CORE_MCP_LENS_TRUST_STORE`; callers cannot supply keys or paths.
The separately distributed Tower 0.9.1 integration accepts `execution_bundle` evidence with an explicit Lens source, run ID
and `0.4-draft` version. Its host injects trusted keys into `EvidenceStore` or
HTTP `create_app`. Both delegate authentication and conformance to Lens.
Verified summaries expose causal IDs; failed, unknown and incomplete summaries
expose no causal claims or native payloads. Neither is an Evals containment score.
Older installed Lens versions degrade to unavailable/unknown until upgraded.

Verifier setup failures, such as missing or unreadable local validation resources,
produce `unknown` with a redacted configuration reason. They do not label an
authenticated snapshot as tampered evidence.

---

## Suite Management

Source: [docs/suite-management.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/suite-management.md)

AgenticLens 0.8.0 adds `agenticlens.suites` and the `agenticlens suite`
command group (roadmap milestone v0.6). Use them to build regression suites
from hand-written cases, production traces, and user feedback. You can then
review, mask, de-duplicate, vary, and split the cases, and approve the suite
as an immutable version that CI can verify and run.

Suites stay plain agentic-evals `TestSuite` files the whole way through, so a
draft or an exported version runs with `agenticlens evaluate`,
`evaluate-live`, and `experiment run` unchanged.

## Lifecycle

```text
CSV / JSON ──► import ─┐
production traces ─────┼─► draft suite ─► mask ─► dedupe ─► vary ─► split ─► review
user feedback ─────────┘        ▲                                              │
                                └──────── edit (add, remove, tag) ◄────────────┘
                                                                               │
                                     approve (checks) ─► store/<name>/<version>.json
                                                                               │
                                  CI: verify ─► export ─► evaluate ─► gate ◄───┘
```

| Stage | CLI | Python |
| --- | --- | --- |
| Import CSV/JSON/JSONL/YAML | `suite import` | `import_cases`, `import_suite` |
| Convert traces | `suite from-traces` | `case_from_run`, `cases_from_runs` |
| Convert feedback | `suite from-feedback` | `case_from_feedback`, `cases_from_feedback` |
| Edit cases | `suite add-case`, `remove-case`, `tag` | `add_case`, `update_case`, `remove_cases`, `tag_cases` |
| Review | `suite review` | `review_cases` |
| Mask PII | `suite mask [--check]` | `PIIMasker`, `mask_suite`, `scan_suite` |
| Duplicates | `suite dedupe [--drop]` | `find_duplicates`, `drop_duplicates` |
| Synthetic variations | `suite vary` | `generate_variations`, `vary_case` |
| Splits | `suite split` | `assign_splits` |
| Filter / summarize / diff | `suite filter`, `summary`, `diff` | `filter_suite`, `summarize_suite`, `diff_suites` |
| Approve and store | `suite approve` | `SuiteStore.approve` |
| CI | `suite verify`, `suite export`, `suite versions` | `SuiteStore.verify`, `load_suite`, `versions` |

Editing commands rewrite the suite file in place unless `--save` names
another file. YAML is written for `.yaml`/`.yml` paths and JSON otherwise.

## Case metadata

AgenticLens records management state in each case's `metadata`:

| Key | Meaning |
| --- | --- |
| `source` | Lineage: `kind` (`imported`, `trace`, `feedback`, `synthetic`; absent means authored), plus `file`/`row`, `trace_id`/`run_id`, `feedback_id`, or `parent_case_id`/`variation`/`seed` |
| `review_status` | `needs_review`, `accepted`, or `rejected`. A case without a status counts as accepted (authored by a person) |
| `reviewed_by`, `review_notes` | Who reviewed the case and why |
| `domain` | Domain category, e.g. `billing` |
| `split` | `train`, `validation`, or `test` |

Tags stay in the case's `tags` list.

## Importing cases

```bash
agenticlens suite import cases.csv --name support-regression --version 1.0.0 \
  --save suite.yaml
```

CSV columns map onto `TestCase` fields. List columns (`expected_contains`,
`required_tools`, `forbidden_tools`, `required_tool_order`, `tags`) are
`|`-separated. `input` is parsed as JSON when it is a JSON object or array.
`domain`, `split`, and any `metadata.<key>` column go to case metadata.
Unknown columns are rejected, so a misspelled expectation fails the import
instead of being dropped silently. JSON imports accept a list, `{"cases": [...]}`,
or JSON Lines. Add `--into suite.yaml` to append to an existing suite.

PII is masked by default before anything is written (`--no-mask` to opt out).

## From production traces

```bash
agenticlens suite from-traces traces/ --name prod-regression --version 1.0.0 --save suite.yaml
```

A successful run becomes a case that expects what the run did:

- `required_tools` and `required_tool_order` from its successful tool calls
- `max_latency_ms` and `max_cost_usd` set to the observed values times
  `--latency-margin` / `--cost-margin` (default 1.5)
- `expected_output` only with `--include-output`, because exact model output
  rarely repeats

The input comes from `metadata.input` or the first span with `input_data`, and
the domain from `task_type`. Each converted case is marked `needs_review`, and
cases that can't be converted are reported with a reason:

- **Failed runs** show what went wrong, not what right looks like. Turn them
  into cases with corrected feedback instead.
- **Runs without a recorded input** have nothing to replay.

Record the request when tracing, either as run metadata
(`trace("support", input=question)`) or on a span
(`span.record_io(input_data=question)`), so there is an input to replay. The
tracer's redactor still applies.

## From user feedback

```json
{"feedback": [
  {"feedback_id": "fb-101", "input": "Where is my parcel?", "output": "It ships in 2 business days.", "rating": "positive"},
  {"feedback_id": "fb-102", "input": "Can I pay by invoice?", "output": "No.", "rating": "negative",
   "corrected_output": "Let me connect you with a specialist."}
]}
```

```bash
agenticlens suite from-feedback feedback.json --into suite.yaml --save suite.yaml --traces traces/
```

If feedback has a correction, the case expects the correction. Positive
feedback (`rating: positive`, or a `score` of 0.5 or more) expects the
confirmed output. Negative feedback without a correction is skipped, because it
says what's wrong but not what's right. When a record has no `input`, the input
comes from the run named by `run_id` or `trace_id` in `--traces`. The rejected
output is kept in `metadata.rejected_output` for reviewers. The schema is
[`schemas/suites/feedback-batch.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/feedback-batch.schema.json).

## PII masking

```bash
agenticlens suite mask suite.yaml                      # mask in place
agenticlens suite mask suite.yaml --check              # scan only; exit 7 if PII found
agenticlens suite mask suite.yaml --strategy hash --salt "$SALT" --report mask.json
```

What gets masked:

- **Patterns in text:** emails, phone numbers, Luhn-valid card numbers, US
  SSNs, IPv4 addresses, bearer tokens, and API keys.
- **Values under sensitive keys** (`password`, `token`, `email`, `phone`,
  `ssn`, `address`, `date_of_birth`, ...), matched as whole words of the key.
  `customer_email` is masked; `input_tokens` is not.
- **Fields covered:** a case's input, expected output, expected substrings,
  expected tool arguments, and metadata. Case lineage is never masked.

`redact` writes `[EMAIL]`. `hash` writes `[EMAIL:3f2a9c1e]`, a salted SHA-256
prefix, so equal values stay equal and you can still spot duplicates. Reports
list the case, the field path, and the PII type, never the value.

Pattern matching is a safeguard, not a guarantee. It doesn't detect names,
street addresses in free text, or locale-specific identifiers. A version
string such as `1.2.3.4` is masked as an IP address. Masking an expected
output also changes what the agent has to produce, so review those cases.

## Duplicates, variations, and splits

```bash
agenticlens suite dedupe suite.yaml --threshold 0.85 --report dupes.json --drop
agenticlens suite vary suite.yaml --per-case 2 --kind typo --kind prefix --seed 7
agenticlens suite split suite.yaml --train 0.7 --validation 0.15 --test 0.15 --seed 7
```

**Duplicates.** Exact duplicates share a normalised input (case,
punctuation, and whitespace ignored). Near duplicates reach the Jaccard
threshold over word unigrams and bigrams. A group is *conflicting* when
cases with the same normalised input expect different results, which usually
means a labelling error. Near duplicates with distinct inputs never conflict. `--drop` keeps the first case of each group. Synthetic
variants of the same original are not compared to each other unless you pass
`--include-variants`. Comparison is pairwise, so it is sized for suites of
thousands of cases.

**Variations.** `lowercase`, `uppercase`, `whitespace`, `punctuation`,
`typo`, and `prefix` change every string in the input, skipping masked
values. They test robustness to how a request is typed, not what it means.
They are not paraphrases and make no model calls. Each variant:

- keeps its parent's expectations
- inherits its parent's split
- is marked `needs_review`
- records `parent_case_id`, `variation`, and `seed`

`--per-case` caps variants per original, so re-running adds nothing new.

**Splits.** A case is placed by hashing its lineage with the seed. A case
keeps its split when other cases are added or removed, so a later version
can't move test cases into training. A variant always lands with its
original. The trade-off is that split sizes only approximate the ratios, and
the CLI warns when a split is empty.

## Review and approval

```bash
agenticlens suite review suite.yaml --status accepted --reviewer qa-lead --case trace-run-1
agenticlens suite review suite.yaml --status rejected --reviewer qa-lead --case fb-7 --notes "policy changed"
agenticlens suite approve suite.yaml --store suites/ --approver qa-lead --notes "Q4 regression set"
```

`approve` runs three checks, records them, and refuses (exit 6) when any
fails:

| Check | Fails when | Override |
| --- | --- | --- |
| `review` | any case is `rejected` (remove it), or `needs_review` | `--allow-unreviewed` (needs_review only) |
| `pii` | the scan finds unmasked PII | `--allow-pii` |
| `conflicting_duplicates` | cases share an input but expect different results | none; fix the labels |

The approved version is written once to `<store>/<name>/<version>.json` as a
`SuiteVersion`. It holds the suite exactly as approved, its SHA-256 over
canonical JSON, the case count, the approver, the time, the notes, the
checks, and an optional `--parent-version`. The schema is
[`schemas/suites/suite-version.schema.json`](https://github.com/DeepAgentLabs/agenticlens/blob/main/schemas/suites/suite-version.schema.json).

Approved versions are immutable:

- Approving the same name and version again is a no-op if the content is
  identical, and is refused if it differs. Bump the version instead.
- Every read re-hashes both the suite (`content_sha256`) and the whole
  envelope (`record_sha256`, covering the approver, time, notes, checks, case
  count, and parent version). A hand-edited, moved, or corrupted version fails
  `verify`, `export`, and `load_suite`.
- Suite names and versions must be plain path segments (letters, digits,
  `.`, `_`, `-`).

Use `suite diff support@1.0.0 suite.yaml --store suites/` to review what a
new draft changes before approving it.

## Running approved suites in CI

```yaml
- run: uv run agenticlens suite verify --store suites
- run: uv run agenticlens suite export support-regression@1.0.0 --store suites --save build/suite.json --split test
- run: uv run agenticlens evaluate build/suite.json build/samples.json --save build/evaluation.json --strict-evidence
- run: uv run agenticlens gate build/evaluation.json
```

`verify` exits 6 when any stored version is missing or changed. `export`
writes a plain suite, optionally filtered by `--tag`, `--domain`, or
`--split`. It stamps `metadata.agenticlens_suite_version` with the name,
version, hash, approver, and approval time, so the evaluation report traces
back to the approved version. For live agents, use `evaluate-live` in place
of `evaluate`. This repository's CI runs exactly these steps against
`examples/suites/store`.

## Example

[`examples/suite_management_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/suite_management_demo.py)
runs the whole lifecycle offline. Its inputs are a CSV with PII and a
duplicate row, three production traces (one failed), and four feedback
records (two unconvertible). It produces 15 approved cases in
`examples/suites/store/support-regression/1.0.0.json` and evaluates them
against a deterministic stub agent. `tests/test_examples_suites.py` checks
that the store and artifacts reproduce byte for byte, apart from the
evaluation report's `created_at`.

```bash
uv run python examples/suite_management_demo.py
```

## Relationship to evaluation datasets

`agenticlens dataset ...` (since 0.5.0) manages labelled *outputs and traces*
for judge calibration. `agenticlens suite ...` manages the *test cases*
(inputs and expectations) those outputs are scored against. Both are
versioned. Only approved suite versions are immutable and hash-verified.

---

## Experiments

Source: [docs/experiments.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/experiments.md)

An experiment runs one evaluation suite against three or more variants — models,
prompts, retrieval strategies, memory settings, retry policies — for several
trials each, then reports quality, cost, latency, and reliability side by side
with the uncertainty that repeated trials reveal.

## Quick start

The repository ships a reproducible experiment that replays recorded outputs,
so it needs no model or network access:

```bash
agenticlens experiment run examples/experiments/support-experiment.yaml \
  examples/experiments/support-suite.yaml \
  --save experiment.json \
  --html experiment.html \
  --csv variants.csv \
  --cases-csv cases.csv
```

Re-render a saved report (for example in CI artifacts) without re-running any
variant:

```bash
agenticlens experiment report experiment.json --html experiment.html --csv variants.csv
```

From Python:

```python
from pathlib import Path

from agenticlens.experiments import (
    load_experiment_suite, load_manifest, run_experiment, save_experiment_html,
)

report = run_experiment(
    load_manifest(Path("examples/experiments/support-experiment.yaml")),
    load_experiment_suite(Path("examples/experiments/support-suite.yaml")),
    confidence_level=0.95,
    regression_threshold=0.05,
)
save_experiment_html(report, Path("experiment.html"))
```

## Manifest

| Field | Default | Meaning |
| --- | --- | --- |
| `name`, `version` | required | Identify the experiment. |
| `baseline_variant_id` | required | The variant every other variant is compared with. |
| `trial_count` | `5` | Trials per variant. Each trial runs the whole suite once. |
| `random_seed` | `null` | Shuffles the order of (variant, trial) runs to spread drift across variants. The order actually used is saved in the report. |
| `pass_k` | `[1, trial_count]` | k values for pass@k and pass^k. Each must be ≤ `trial_count`. |
| `minimum_trials` | `5` | Variants with fewer completed trials get exploratory warnings. |
| `max_workers` | `1` | Cases run concurrently within one live trial. |
| `variants` | required, ≥ 3 | See below. |

Each variant has an `id`, `name`, `target_kind`, `target`, optional
`timeout_seconds`, and `factors`:

| `target_kind` | `target` |
| --- | --- |
| `python` | A trusted `module:function` or `path/to/file.py:function`, called as `fn(case.input, case=case)`. |
| `http` | A URL receiving `{"input": ..., "case_id": ...}` by POST. |
| `recorded` | A JSON/YAML file of saved samples per trial, resolved relative to the manifest. |

`factors` maps a dimension to the value this variant uses, for example
`{model: small, prompt: v3, retrieval: bm25}`. The documented dimensions are
`model`, `prompt`, `retrieval`, `memory`, and `retry_policy`; any other name is
allowed. Factors drive the "changed factors" column of each comparison and the
factor-level summary.

### Recorded trials

A `recorded` target replays saved outputs instead of calling an agent:

```json
{
  "trials": [
    {"samples": [{"case_id": "refund-window", "output": "...", "trace": {...}}, ...]},
    {"samples": [...]}
  ]
}
```

Trial *n* replays `trials[n-1]`. If the file has fewer trials than
`trial_count`, the missing trials are recorded as failed. Traces may be in
`EvalTrace` shape or AgenticLens `Run` shape. Saving each live trial's samples
and replaying them this way makes an experiment reproducible from committed
files — `examples/experiments/record_trials.py` shows the layout.

## What is measured

### Per case

For each variant and case: attempts (one per trial), passes, pass rate, mean
score and its standard deviation across trials, whether every attempt agreed
(`consistent`), and:

- **pass@k** — the probability that at least one of k attempts passes, from the
  unbiased estimator `1 − C(n−c, k) / C(n, k)` (Chen et al., 2021).
- **pass^k** — the probability that all k attempts pass, `C(c, k) / C(n, k)`
  (Yao et al., 2024, τ-bench). This is the reliability measure: an agent with
  pass@1 = 90% has pass^6 ≈ 53% if failures are independent.

A trial whose target call raised an error counts as a failed attempt on every
case: the agent did not deliver an output.

### Per variant

| Measure | How |
| --- | --- |
| Case pass rate | passes / attempts over all cases, with a Wilson score interval |
| pass@k, pass^k | mean of the per-case values |
| Mean score, latency, cost | over completed trials, with normal-approximation intervals |
| Reliability | share of trials in which every case passed |
| Consistency | share of cases whose attempts all agreed; disagreeing cases are listed as flaky |
| Pareto frontier | not dominated on reliability, pass rate, score, latency, and cost |

### Against the baseline

Each comparison reports deltas for pass rate, score, latency, and cost (with the
`regression_threshold` deciding which count as regressions), plus:

- `changed_factors` — `{factor: [baseline value, candidate value]}`;
- `case_pass_rate_p_value` — two-sided pooled two-proportion z-test on case
  attempts, and `statistically_significant` when `p < 1 − confidence_level`;
- `regressed_case_ids` / `improved_case_ids` — cases whose pass rate moved by
  more than the regression threshold;
- warnings when either side completed fewer than `minimum_trials` trials, or when
  several factors changed at once (so the delta cannot be attributed to one).

### Factor levels

For each factor with at least two values, variants sharing a value are
averaged. In the bundled example, `model=large` averages the baseline, terse
prompt, and reranked retrieval variants; `model=small` is the small-model
variant alone.

## Reports

- **JSON** (`--save`): the full `ExperimentReport`, including every trial's
  evaluation report. Schema: `schemas/experiments/experiment-report.schema.json`.
- **HTML** (`--html`): one offline page with the variant table, pass@k / pass^k,
  baseline deltas, a variant × test-case heatmap (colour = mean score, label =
  passes/attempts, dashed outline = flaky), factor levels, warnings, and the
  execution order. Follows the system light/dark preference.
- **CSV** (`--csv`): one row per variant with every summary measure, pass@k /
  pass^k columns, and its baseline comparison.
- **Case matrix CSV** (`--cases-csv`): one row per (variant, case) — the data
  behind the heatmap.

## Reading the numbers honestly

- Intervals and p-values treat each case attempt as independent. Attempts on
  the same case are correlated, so intervals are narrower than they should be;
  treat them as approximate and prefer more cases over more trials.
- A non-significant delta is not evidence of no difference — it may mean the
  experiment is too small. The minimum-trials warning flags the obvious cases.
- Live model outputs vary between runs. Recorded replays reproduce the analysis
  exactly; they do not reproduce the model.
- The seed fixes the execution order, not the model's sampling.

## Limitations

- Only one suite per experiment; variants must answer the same cases.
- No multiple-comparison correction across variants.
- Live variants run trials sequentially; `max_workers` parallelises cases within
  a trial only.

---

## Limitations

Source: [docs/limitations.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/limitations.md)

This page documents known limitations of AgenticLens 0.5.0. Planned
improvements appear in [Roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/docs/roadmap.md).

---

## Instrumentation

### Explicit instrumentation only

AgenticLens does not automatically intercept framework events. You must wrap
agent calls with `profile()` / `step()` or `trace()` / `recording.span()`
explicitly. Automatic framework adapters (LangGraph, LangChain, etc.) are
roadmap work.

### Token extraction is provider-specific

`step.record(response)` extracts token counts from OpenAI and Anthropic
response objects. Other providers require `s.record_tokens()` with manually
supplied counts.

### No streaming token capture

Token extraction from streaming response objects is not implemented. Buffer
the full response before calling `s.record()`.

---

## Analysis and recommendations

### Recommendations are rule-based

Recommenders apply deterministic heuristics. They identify probable waste
patterns but cannot guarantee that acting on a recommendation will improve
your specific agent's performance. Always evaluate changes with a test suite.

### Cost estimates are approximate

Live pricing is fetched from provider APIs and cached. Pricing may lag
behind actual rate changes. Cost estimates are for budgeting and trend
analysis, not billing.

### Optimization projections assume similar traffic

`agenticlens optimize` projects savings from the analysed traces. Compression
and reranking benefits are configured or best-case assumptions, prompt-caching
cost is pro-rated by token share, and outcome evaluation compares two traffic
windows without controlling for other changes shipped in between.

### Comparison is descriptive only

`agenticlens compare` reports descriptive statistics (mean, median, P95,
standard deviation). It does not claim statistical significance or causal
attribution, especially for small or uncontrolled samples.

---

## Evaluation

### No built-in provider clients

AgenticLens does not ship LLM clients for evaluation. You supply the
callable that calls your model. The `LLMJudgeEvaluator` wraps your function
and normalizes the score; it does not make model API calls itself.

### Synchronous evaluators only

`evaluate_suite` is synchronous. Batched or asynchronous evaluation is a
roadmap capability.

### `max_turns` requires explicit metadata

`max_turns` checks require `trace.metadata.turn_count` to be set as a
positive integer. AgenticLens does not infer conversational turns from span
types.

---

## Live OTLP receiver (`serve-otlp`)

### No authentication

The receiver ships with no authentication. It must not be exposed to untrusted
networks. Always bind to localhost (`127.0.0.1`) in development environments.

### Plain polling, not websockets

The real-time dashboard refreshes by polling. It does not use WebSockets
or Server-Sent Events.

### In-memory store eviction

The default in-memory trace store evicts the oldest traces (FIFO) when the
cap (default 200) is reached. Use `--db PATH` for persistent storage.

---

## Payload redaction

### Built-in patterns are not exhaustive

The built-in redactor strips secrets, bearer tokens, and email addresses.
It is not a comprehensive PII scrubber. For production environments with
strict data handling requirements, supply a custom `redactor=` function.

---

## AIOS conformance

### Draft specification

The `ai-operations-spec` is a draft. Conformance reports say "draft alignment"
rather than "stable conformance." Schema and semantic checks will evolve as
the spec matures.

---

## Schemas

### Trace and evaluation APIs are experimental

The trace, comparison, and evaluation report schemas may evolve in future
minor versions. Breaking changes will be documented in
[CHANGELOG.md](https://github.com/DeepAgentLabs/agenticlens/blob/main/CHANGELOG.md)
and accompanied by a version bump.

---

## Platform

### Python 3.10+ required

AgenticLens requires Python 3.10 or later. Older Python versions are not
supported.

---

## Source declarations: src/agenticlens/__init__.py

Source: [src/agenticlens/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/__init__.py)

```python
__all__ = ['Run', 'RunStatus', 'Span', 'SpanHandle', 'SpanType', 'StepHandle', '__version__', 'profile', 'step', 'trace']
```

---

## Source declarations: src/agenticlens/models/__init__.py

Source: [src/agenticlens/models/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/__init__.py)

```python
__all__ = ['Metrics', 'Recommendation', 'Severity', 'Step', 'StepType', 'Evidence', 'Finding', 'MetricValue', 'Run', 'RunStatus', 'Span', 'SpanType', 'Workflow']
```

---

## Source declarations: src/agenticlens/models/enums.py

Source: [src/agenticlens/models/enums.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/enums.py)

```python
class StepType(str, Enum):
    PLANNER = 'planner'
    RETRIEVER = 'retriever'
    TOOL_CALL = 'tool_call'
    LLM_CALL = 'llm_call'
    MEMORY = 'memory'
    FINAL_RESPONSE = 'final_response'
class Severity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'
```

---

## Source declarations: src/agenticlens/models/metrics.py

Source: [src/agenticlens/models/metrics.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/metrics.py)

```python
class Metrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    ttft: float | None = Field(default=None, description='Time To First Token in seconds. Only set for streaming calls.')
    cost: float | None = Field(default=None, description='Total cost for the step. None when pricing is unknown for the model.')
    @property
    def tps(self) -> float | None: ...
```

---

## Source declarations: src/agenticlens/models/recommendation.py

Source: [src/agenticlens/models/recommendation.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/recommendation.py)

```python
class Recommendation(BaseModel):
    title: str
    description: str
    optimization_type: str = Field(default='token_optimization', description='Machine-readable optimization category, e.g. rag_chunk_pruning.')
    step_id: str | None = None
    step_name: str | None = None
    step_type: str | None = None
    severity: Severity = Severity.INFO
    tokens_saved: int = 0
    estimated_savings: float | None = None
    estimated_usd_savings: float | None = None
    estimated_monthly_savings: float | None = None
    confidence: float | None = None
    quality_risk: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    cost_savings: float | None = Field(default=None, description='Projected dollar savings for cost-aware recommenders (e.g. model swaps). Distinct from `estimated_savings`, which is a token-reduction percentage.')
```

---

## Source declarations: src/agenticlens/models/step.py

Source: [src/agenticlens/models/step.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/step.py)

```python
class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: StepType
    agent_name: str | None = Field(default=None, description='Name of the agent responsible for this step in a multi-agent workflow.')
    agent_role: str | None = Field(default=None, description='Optional role label such as planner, researcher, critic, or executor.')
    parent_step_id: str | None = Field(default=None, description='Optional parent step id for workflow graph or handoff relationships.')
    handoff_from: str | None = Field(default=None, description='Agent or step that handed context to this step.')
    handoff_to: str | None = Field(default=None, description="Agent or step that receives this step's output.")
    provider: str | None = None
    model: str | None = None
    metrics: Metrics = Field(default_factory=Metrics)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Free-form signals supplied by the developer for recommender rules (e.g. 'prompt', 'chunk_count', 'history_tokens', 'tool_name', 'tool_args').")
```

---

## Source declarations: src/agenticlens/models/trace.py

Source: [src/agenticlens/models/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/trace.py)

```python
class SpanType(str, Enum):
    MODEL_CALL = 'model_call'
    PLANNING = 'planning'
    MEMORY_READ = 'memory_read'
    MEMORY_WRITE = 'memory_write'
    RETRIEVAL = 'retrieval'
    TOOL_CALL = 'tool_call'
    VALIDATION = 'validation'
    RETRY = 'retry'
    DELEGATION = 'delegation'
    FINAL_RESPONSE = 'final_response'
    CUSTOM = 'custom'
class RunStatus(str, Enum):
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
class Span(BaseModel):
    span_id: str = Field(default_factory=_uuid)
    parent_span_id: str | None = None
    name: str
    span_type: SpanType
    agent_name: str | None = None
    model_name: str | None = None
    provider: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    latency_ms: float = Field(default=0.0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    tool_name: str | None = None
    retry_number: int | None = Field(default=None, ge=0)
    status: RunStatus = RunStatus.RUNNING
    error_type: str | None = None
    error_message: str | None = None
    input_reference: str | None = None
    output_reference: str | None = None
    input_data: Any | None = Field(default=None, description='Optional captured input after configured redaction.')
    output_data: Any | None = Field(default=None, description='Optional captured output after configured redaction.')
    attributes: dict[str, Any] = Field(default_factory=dict)
    @property
    def total_tokens(self) -> int: ...
class Run(BaseModel):
    schema_version: str = '1.0'
    run_id: str = Field(default_factory=_uuid)
    trace_id: str = Field(default_factory=_uuid)
    application_name: str
    framework: str | None = None
    framework_version: str | None = None
    task_id: str | None = None
    task_type: str | None = None
    experiment_id: str | None = None
    variant_id: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    status: RunStatus = RunStatus.RUNNING
    spans: list[Span] = Field(default_factory=list)
    task_success: bool | None = None
    error_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='after')
    def validate_span_tree(self) -> 'Run': ...
    @property
    def total_input_tokens(self) -> int: ...
    @property
    def total_output_tokens(self) -> int: ...
    @property
    def total_tokens(self) -> int: ...
    @property
    def total_latency_ms(self) -> float: ...
    @property
    def estimated_cost_usd(self) -> float | None: ...
class MetricValue(BaseModel):
    name: str
    value: float
    unit: str
    estimated: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)
class Evidence(BaseModel):
    source: str
    span_id: str | None = None
    timestamp: datetime | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    reasoning: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
class Finding(BaseModel):
    finding_id: str = Field(default_factory=_uuid)
    category: str
    title: str
    description: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    span_ids: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
```

---

## Source declarations: src/agenticlens/models/workflow.py

Source: [src/agenticlens/models/workflow.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/models/workflow.py)

```python
class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime
    end_time: datetime | None = None
    steps: list[Step] = Field(default_factory=list)
    chaos_events: list[dict[str, Any]] = Field(default_factory=list, description="Additive workflow.json extension (schema v1.1, see docs/workflow-schema-spec.md). Populated by fault-injection tools such as agentic-chaos; each entry is expected to carry at least 'fault_type', 'outcome', and (when correlated to a step) 'step_id'/'step_name'. Left loosely typed here so AgenticLens has no hard dependency on the producer.")
    @property
    def total_tokens(self) -> int: ...
    @property
    def total_cost(self) -> float | None: ...
    @property
    def latency(self) -> float: ...
```

---

## Source declarations: src/agenticlens/profiler/context.py

Source: [src/agenticlens/profiler/context.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/profiler/context.py)

```python
def get_active_workflow() -> Workflow: ...
```

---

## Source declarations: src/agenticlens/instrumentation/__init__.py

Source: [src/agenticlens/instrumentation/__init__.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/__init__.py)

```python
__all__ = ['Redactor', 'SpanHandle', 'redact_sensitive', 'trace']
```

---

## Source declarations: src/agenticlens/instrumentation/redaction.py

Source: [src/agenticlens/instrumentation/redaction.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/redaction.py)

```python
def redact_sensitive(value: Any) -> Any: ...
```

---

## Source declarations: src/agenticlens/instrumentation/trace.py

Source: [src/agenticlens/instrumentation/trace.py](https://github.com/DeepAgentLabs/agenticlens/blob/main/src/agenticlens/instrumentation/trace.py)

```python
class SpanHandle():
    def __init__(self, span: Span, redactor: Redactor) -> None: ...
    def record_tokens(self, input_tokens: int=0, output_tokens: int=0) -> None: ...
    def record_cost(self, estimated_cost_usd: float) -> None: ...
    def set_attribute(self, name: str, value: Any) -> None: ...
    def record_io(self, *, input_data: Any=None, output_data: Any=None) -> None: ...
class SpanContext():
    def __init__(self, owner: 'trace', name: str, span_type: SpanType | str, *, agent_name: str | None=None, model_name: str | None=None, provider: str | None=None, tool_name: str | None=None, retry_number: int | None=None, input_reference: str | None=None, output_reference: str | None=None, **attributes: Any): ...
class trace():
    def __init__(self, application_name: str, *, redactor: Redactor=redact_sensitive, framework: str | None=None, framework_version: str | None=None, task_id: str | None=None, task_type: str | None=None, experiment_id: str | None=None, variant_id: str | None=None, otlp_endpoint: str | None=None, otlp_headers: dict[str, str] | None=None, otlp_timeout_seconds: float | None=None, **metadata: Any) -> None: ...
    def span(self, name: str, span_type: SpanType | str=SpanType.CUSTOM, **attributes: Any) -> SpanContext: ...
    def save(self, path: str | Path) -> None: ...
```
