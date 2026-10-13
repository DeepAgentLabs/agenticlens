# Diagnosis and Failure Attribution

AgenticLens 0.7.0 adds a deterministic diagnosis layer on top of structured
traces (`Run`/`Span`). Given one run, it answers:

- **What failed, and what kind of failure was it?** (failure taxonomy)
- **Which step and which agent caused it**, as opposed to failing as a
  consequence? (faulty-step and faulty-agent attribution)
- **In what order did things happen?** (incident timeline)
- **Is anything unusual compared with healthy runs?** (anomaly detection)
- **What did the failure cost, and what should I check next?** (investigation
  narrative)

Every diagnosis comes from a rule that cites recorded spans. Nothing here
calls a model, and the same saved trace always produces the same report.

```bash
agenticlens diagnose run.json --baseline healthy-runs/ \
  --save diagnosis.json --markdown investigation.md
```

```python
from agenticlens.diagnosis import diagnose_run, explain_run

report = diagnose_run(run, baseline=healthy_runs)
print(report.attribution.faulty_step, report.attribution.confidence)
print(explain_run(report))
```

A complete, offline example lives in
[`examples/diagnosis_demo.py`](https://github.com/DeepAgentLabs/agenticlens/blob/main/examples/diagnosis_demo.py);
its saved report and narrative are in `examples/diagnosis/artifacts/`.

## Failure taxonomy

Taxonomy version `1.0` (`agenticlens.diagnosis.TAXONOMY_VERSION`). Each
category records its layer, default severity, an attribution weight (how
strongly it points at its own span as the cause), and a next step.

| Category | Layer | Meaning | Attribution weight |
| --- | --- | --- | --- |
| `tool_error` | tool | A tool call returned an error or raised | 0.90 |
| `model_error` | model | A model call failed (provider error, refusal, malformed output) | 0.90 |
| `retrieval_error` | retrieval | A retrieval step failed before returning results | 0.90 |
| `timeout` | environment | A span failed with a timeout or exceeded `timeout_ms` | 0.85 |
| `validation_failure` | quality | An output or intermediate result failed validation | 0.85 |
| `delegation_failure` | orchestration | Delegating work to another agent failed | 0.85 |
| `retry_exhausted` | orchestration | Every retry of a failed operation also failed | 0.80 |
| `tool_loop` | orchestration | The same tool ran repeatedly with the same input | 0.70 |
| `handoff_loop` | orchestration | Agents handed control back and forth | 0.70 |
| `stagnation` | quality | Consecutive model calls produced identical output | 0.65 |
| `empty_retrieval` | retrieval | Retrieval returned no documents | 0.60 |
| `budget_exceeded` | resource | Run cost, tokens, or latency exceeded a configured budget | 0.40 |
| `injected_fault` | environment | A deliberately injected fault (agentic-chaos) hit the span | 1.00 |
| `incomplete_task` | outcome | The task failed and nothing more specific explains it | 0.30 |

## Diagnosis rules

| Rule | Detects | Needs in the trace |
| --- | --- | --- |
| `failed_span` | Origin failures (failed spans whose children did not fail first), grouped when identical, with propagation to failed ancestors and recovery by retries or a later successful attempt | span `status`, `error_type`/`error_message` |
| `injected_fault` | agentic-chaos faults on spans that did not fail themselves (for example injected latency) | `chaos.injected` / `chaos.fault_type` attributes |
| `retry_exhaustion` | Retries of one failure that never succeeded | `retry` spans |
| `tool_loop` | `loop_threshold` (3) identical consecutive tool calls per agent | `input_data`, `input_reference`, or `tool_args` (lower confidence without them) |
| `handoff_loop` | `handoff_round_trips` (2) A→B→A round trips | `delegation` spans with `to_agent` (or a child span of the receiving agent) |
| `stagnation` | `stagnation_threshold` (3) identical consecutive model outputs per agent | captured `output_data` or `output_reference` |
| `empty_retrieval` | Retrieval spans that returned zero results | `result_count`, `documents`, or list `output_data` |
| `budget` | Run cost, token, or latency above `DiagnosisConfig` budgets | span costs (budget is skipped and noted when cost is incomplete) |
| `incomplete_task` | Fallback when the run failed but every other diagnosis was recovered | run `status` / `task_success` |

Rules are versioned (`rule_id@version` on every diagnosis). Pass your own
rules with `diagnose_run(run, rules=[...])`; each rule implements
`diagnose(view, config) -> list[Diagnosis]`.

## Faulty-step and faulty-agent attribution

Blame is assigned only from diagnoses. Each diagnosis contributes to its
origin span:

```text
weight = taxonomy attribution_weight × diagnosis confidence
         × 0.3   if the failure was recovered
         × 1.15  for the earliest unrecovered origin (causal precedence)
         × 0.5   for unrecovered origins that start after it (likely consequences)
```

Contributions are summed per span and normalized into shares that sum to 1.
The top candidate is the faulty step; its agent (inherited from the nearest
ancestor that names one) is the faulty agent, and `agent_scores` gives every
agent's share. The attribution confidence is the top share scaled by the
confidence of its strongest diagnosis, so a single weak lead stays
low-confidence.

`Attribution.status` is `attributed`, `recovered` (failures happened but the
run did not fail), `unattributed` (the run failed and no span explains it),
or `no_failure`.

!!! note "Shares are not probabilities"
    Attribution shares are rule-weighted blame. Measure how often they are
    right on controlled failures before relying on them (below).

## Attribution accuracy on controlled failures

A controlled failure is a trace whose faulty step is known in advance: either
a span carries agentic-chaos markers (`chaos.injected`), or the producer sets
`run.metadata["expected_faulty_span_id"]` (and optionally
`expected_faulty_agent`, `expected_category`).

```bash
agenticlens attribution-accuracy examples/diagnosis/controlled_failures \
  --save accuracy.json --min-step-accuracy 0.9
```

The report gives top-1 and top-3 faulty-step accuracy, faulty-agent and
category accuracy, each with a Wilson interval, and a calibration gap (mean
confidence minus top-1 accuracy).

The repository ships a 40-case corpus across ten scenarios (tool timeouts
with exhausted retries, a recovered transient error followed by a validation
failure, injected latency causing a downstream deadline, injected tool
errors, tool loops, planner model errors with propagation, empty retrieval,
stagnation, handoff loops, and nested tool failures), built by
`examples/diagnosis/build_controlled_failures.py`. Variants change agents and
add distractors. On this corpus, attribution identifies the faulty step,
agent, and category in 40/40 cases (95% Wilson interval 91.2%–100%); mean
confidence is 79.5%, so the confidence is conservative here.

!!! warning "Scope of that result"
    The corpus is synthetic and was written alongside the rules it tests. It
    shows the rules behave as designed on known failure shapes; it is not
    independent evidence of accuracy on production traces. Add your own
    controlled failures (agentic-chaos runs are a good source) and track the
    accuracy report in CI.

## Incident timeline

`report.timeline` orders run start, span starts, failures, retries, handoffs,
injected faults, recoveries, and run completion by timestamp, with offsets
from the run start. The attributed root cause is marked. Routine span starts
are dropped first when a timeline exceeds `max_events` (500).

```bash
agenticlens trace timeline run.json --save timeline.json
```

## Anomaly detection

With `baseline=` runs (or `--baseline` on the CLI), run-level and per-span
latency, tokens, and cost are compared with the baseline using the modified
z-score `0.6745 × (x − median) / MAD` (threshold 3.5). Spans match across
runs by `<span_type>:<name>`; repeated spans are summed per run. When the
MAD is zero the score falls back to the mean absolute deviation, and when
every baseline value is identical only differences above a relative
tolerance (25%) are reported. At least five baseline runs are required per
metric; keys with fewer are listed in `warnings`.

## Guardrails for automated analysis

`AnalysisBudget` caps spans analyzed (`max_spans`), span-tree depth
(`max_depth`, the recursion cap), diagnoses kept (`max_diagnoses`), wall-clock
time (`max_seconds`), and, for iterative analyzers, iterations
(`max_iterations`), spend (`max_cost_usd`), and stagnation
(`stagnation_limit` consecutive iterations that find nothing new).

`diagnose_run(..., budget=AnalysisBudget(...))` applies the span, depth,
diagnosis, and time limits and records what was cut short in
`report.guardrails`. Your own analyzers can use the same guard:

```python
from agenticlens.diagnosis import AnalysisBudget, AnalysisGuard

guard = AnalysisGuard(AnalysisBudget(max_iterations=10, max_cost_usd=0.50))
while not guard.exhausted:
    finding = investigate_next()          # e.g. a model-assisted step
    guard.charge(cost_usd=finding.cost)
    guard.record([finding.fingerprint])   # stagnation detection
status = guard.status()
```

## Investigation narratives

`explain_run(report)` writes Markdown with a verdict, the root cause and its
supporting spans, contributing factors, the key timeline events, the tokens,
latency, and cost spent in failed and retry spans, efficiency findings,
anomalies, next steps from the taxonomy, and limitations.

`explain_recommendations(workflow, recommendations)` explains *why* each
optimization recommendation's waste occurred (repeated prompts, oversized
retrieval, history growth, duplicate tool calls, handoff bloat, model tier,
unabsorbed faults), what was measured, the projected impact, the quality
risk, and the cited evidence.

```bash
agenticlens explain run.json          # trace -> diagnose and explain
agenticlens explain diagnosis.json    # saved diagnosis report
agenticlens explain workflow.json     # workflow -> recommendations narrative
```

## CLI summary

| Command | Purpose |
| --- | --- |
| `diagnose RUN` | Diagnoses, attribution, anomalies (`--baseline`), budgets, guardrails; `--fail-on-unrecovered` exits 4 |
| `explain FILE` | Investigation narrative for a trace, diagnosis report, or workflow |
| `trace show RUN [--span ID]` | Span tree and metrics, or one span's full record |
| `trace timeline RUN` | Incident timeline with the root cause marked |
| `attribution-accuracy PATH` | Accuracy on controlled failures; `--min-step-accuracy` exits 5 |

## Report contract

`DiagnosisReport` (schema version `1.0`) and `AttributionAccuracyReport` are
published as JSON Schemas in `schemas/diagnosis/` and included in the wheel.
Reports carry the taxonomy, engine, and rule versions they were produced
with and contain no wall-clock timestamp of their own, so they reproduce
exactly from the saved trace.

## Limitations

- Rules only see what the trace recorded. Missing statuses, inputs, or
  outputs make some rules silent or lower their confidence.
- Attribution follows recorded structure and timing. A root cause outside the
  trace (for example an upstream data change) is reported as the first
  recorded symptom.
- Validation failures are attributed to the validation span; the step that
  produced the rejected value may be the real cause.
- Anomaly detection assumes baseline runs of the same workflow and is
  per-metric; it does not correct for multiple comparisons.
