# AgenticLens developer guide

Use this guide to set up AgenticLens, run a local example, and apply it to your application. Optional provider and integration fragments identify the objects or services you must supply.

[Quickstart](#quickstart) · [Usage](#usage) · [Configuration](#settings) · [Troubleshooting](#troubleshooting) · [Reference](#reference)

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

[Download lens_quickstart.py](guide/examples/lens_quickstart.py)

### Run and inspect

```
python lens_quickstart.py
agenticlens inspect run.json
```

**Expected:** a saved run with planning and memory spans. This proves the instrumentation path, not measured production cost or quality.

### Connect your application

Wrap actual execution boundaries with spans, attach real usage, and preserve run identifiers. For existing OTLP data, follow the supported import contract rather than relabeling arbitrary JSON as a Lens run.

[Tracing and comparison ↗](trace-and-comparison.md) · [CLI reference ↗](cli-reference.md)

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

documented in [AIOS validation and OTel export](aios-validation-and-otel.md).

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

- [Open API / CLI reference ↗](cli-reference.md)
