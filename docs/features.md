# Features

Every capability below is implemented and available in AgenticLens 0.5.0.
Planned capabilities appear only in [Roadmap](roadmap.md).

---

## Workflow profiling

**Status:** Stable

Profile any Python workflow with two context managers:

```python
from agenticlens import profile, step

with profile("My Workflow") as wf:
    with step("Planner", type="planner") as s:
        response = llm.invoke(prompt)
        s.record(response)
```

- Captures prompt tokens, completion tokens, total tokens, latency, and TTFT per step
- Supports step types: `planner`, `retriever`, `tool_call`, `llm_call`, `memory`, `final_response`
- Saves portable `workflow.json` artifacts

**Limitations:**
- Token capture requires a provider response object with `.usage.prompt_tokens` and `.usage.completion_tokens`
- No automatic framework event capture; instrumentation is explicit

---

## Structured run and span tracing

**Status:** Experimental

```python
from agenticlens import SpanType, trace

with trace("support-agent", environment="staging") as recording:
    with recording.span("planner", SpanType.PLANNING) as s:
        s.record_tokens(input_tokens=120, output_tokens=30)
        s.record_io(input="user query", output="plan")

recording.save("run.json")
```

- Hierarchical parent-child span tree
- Built-in payload redaction (secrets, bearer tokens, email addresses)
- Custom `redactor=` function supported
- Versioned JSON Schema: `schemas/trace.schema.json`

**Limitations:** Experimental API — schema may evolve

---

## Cost and token analysis

**Status:** Stable

```bash
agenticlens analyze workflow.json
```

- Per-step token breakdown (prompt, completion, total)
- Dollar cost per step and per run using live provider pricing
- On-disk pricing cache; bundled fallback data
- Monthly cost projections
- Tokens-per-second throughput

**Supported providers:** OpenAI, Anthropic

---

## Optimization recommendations

**Status:** Stable

AgenticLens automatically surfaces rule-based recommendations after analysis:

| Recommender | Finding |
|-------------|---------|
| Prompt | Repeated prompt prefixes that should be cached or deduplicated |
| RAG chunk | Low-utility retrieved chunks (see [RAG chunk utility](rag-chunk-utility.md)) |
| Memory | Excessive conversation history that should be summarized |
| Tool | Duplicate tool calls that should be cached |
| Handoff | Oversized multi-agent context passed between agents |
| Chaos impact | Unhandled failures and silent degradation from `chaos_events` |

Every finding includes source evidence (step/span reference, measured value, threshold),
confidence, quality risk, estimated token savings, and dollar-savings projection.

---

## Repeated-run comparison

**Status:** Experimental

Compare a baseline and candidate set of runs:

```bash
agenticlens compare results/baseline results/candidate \
  --regression-threshold 0.05 \
  --save comparison.json
```

Reports: success rate, mean/median/P95 latency, standard deviation,
coefficient of variation, cost per successful task, and relative regression deltas.

```bash
agenticlens compare results/baseline results/candidate \
  --format md \
  --save comparison.md \
  --fail-on-regression \
  --min-samples 5
```

**Limitations:** Descriptive only — does not claim statistical significance

---

## Evaluation framework

**Status:** Experimental

Run deterministic and custom evaluators against saved samples:

```bash
agenticlens evaluate suite.yaml samples.json \
  --save evaluation.json \
  --html evaluation.html
```

Built-in checks:

| Check | Type |
|-------|------|
| Exact match | Deterministic |
| Required output phrases | Deterministic |
| Required tools | Trace-aware |
| Required tool arguments | Trace-aware |
| JSON Schema output validation | Deterministic |
| Required output fields | Deterministic |
| Max turn count | Trace-aware |
| Max latency | Operational |
| Max cost | Operational |

Custom evaluators via `EvaluatorRegistry`: `CallableEvaluator`,
`LLMJudgeEvaluator`, `BusinessRuleEvaluator`. See [API reference](api-reference.md).

---

## Versioned evaluation datasets

**Status:** Experimental

```bash
agenticlens dataset summary dataset.json
agenticlens dataset split dataset.json --train-ratio 0.7 --validation-ratio 0.15 --test-ratio 0.15
agenticlens dataset export-samples dataset.json --split test --save samples-test.json
```

---

## Live evaluation targets

**Status:** Experimental

Run the same suite against a live Python callable or HTTP endpoint:

```bash
agenticlens evaluate-live suite.yaml \
  --target-kind python \
  --target examples/live_evaluation_demo.py:run_case \
  --save evaluation-live.json
```

---

## Release gates

**Status:** Experimental

```bash
agenticlens gate evaluation.json \
  --min-pass-rate 0.95 \
  --min-average-score 0.98 \
  --max-failed-cases 1 \
  --max-average-latency-ms 1500 \
  --max-total-cost-usd 0.25
```

Exit codes: `0` = passed, `2` = gate failed, `1` = invalid input.
CI-safe: gates wire directly into build pipelines.

---

## Judge calibration

**Status:** Experimental

Compare LLM judge verdicts against a human-labeled reference set:

```bash
agenticlens calibrate evaluation.json labels.json \
  --evaluator answer_quality \
  --save calibration.json
```

Reports: agreement rate with 95% Wilson confidence interval, confusion counts
(true/false accept, true/false reject), and trace-linked evidence per case.

---

## HTML dashboard

**Status:** Experimental

```bash
agenticlens dashboard \
  --run run.json \
  --evaluation evaluation.json \
  --comparison comparison.json \
  --save dashboard.html
```

Combines: agent timeline, cost-by-area breakdown, waste findings, release gate,
and baseline-vs-candidate comparison. No external fonts or network requests —
renders fully offline.

Also produced automatically by `analyze`, `inspect`, and `compare` with `--html`.

---

## Live OTLP receiver

**Status:** Experimental · Requires `agenticlens[api]`

```bash
agenticlens serve-otlp --port 4318 --db traces.db
```

Receives OTLP/HTTP JSON traces and renders a real-time dashboard at
`http://127.0.0.1:4318`. Bounded in-memory store (default cap 200, FIFO eviction);
`--db` enables SQLite persistence across restarts.

**Known limitation:** No authentication; documented as a stated limitation.
Bind to localhost only.

---

## Persistent trace history

**Status:** Experimental

```bash
agenticlens history --db traces.db
agenticlens history results/
```

Shows aggregate tokens, cost, error rate, and P95 latency across recent
traces. Cost aggregates note "N of M traces priced" when pricing is incomplete.

---

## OTLP import and export

**Status:** Experimental

Export a run as OTLP:

```python
from agenticlens.exporters import OTLPTraceExporter
OTLPTraceExporter().save(recording.run, "run-otlp.json")
```

Import a third-party OTLP trace:

```bash
agenticlens import-otlp third-party-trace.json --save run.json
```

Supports OpenTelemetry GenAI semantic conventions (`gen_ai.*` attributes).

---

## AIOS validation and conformance

**Status:** Experimental

```bash
agenticlens validate workflow.json --version 0.4
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

Validates against AI Operations Specification draft schemas. See
[AIOS validation and OTel export](aios-validation-and-otel.md).

---

## RAG chunk utility scoring

**Status:** Stable

Identifies low-utility retrieved chunks that waste tokens. Supports citation
signals, reranker scores, embedding similarity, generic utility scores, and
word-overlap fallback. See [RAG chunk utility](rag-chunk-utility.md).

---

## Multi-agent support

**Status:** Experimental

Attach `agent_name`, `agent_role`, and handoff metadata to steps. AgenticLens
reports token usage by agent and flags oversized handoffs. Reference LangGraph
supervisor workflow included. See [Multi-agent reference workflows](multi-agent-reference-workflows.md).

---

## Export formats

**Status:** Stable

JSON, CSV, Markdown, Jira wiki markup, OTLP JSON. See [Export formats](export-formats.md).

---

## Chaos event analysis

**Status:** Stable

AgenticLens reads `chaos_events` written by `agentic-chaos` and surfaces
resilience findings via `ChaosImpactRecommender`. See
[Workflow schema spec](workflow-schema-spec.md).
