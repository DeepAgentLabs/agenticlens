# Limitations

This page lists what the current AgenticLens release does not do, so you can
plan around it. The package is early-stage (PyPI classifier: Alpha). Planned
improvements appear in [Roadmap](roadmap.md). Topic guides list further limits
for their own features.

---

## Instrumentation

### Explicit instrumentation only

AgenticLens does not automatically intercept framework events. You must wrap
agent calls with `profile()` / `step()` or `trace()` / `recording.span()`
explicitly. The `[langgraph]` and `[multi-agent]` extras ship an offline
LangGraph reference workflow, but LangGraph nodes are still instrumented by
hand. Automatic framework event capture (LangGraph, LangChain, etc.) is
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

Prices resolve from your overrides, then the optional live pricing feed
(LiteLLM's public price list, cached), then the bundled pricing table. Any of
these can lag behind actual rate changes. Unknown prices stay unknown rather
than counting as zero. Cost estimates are for budgeting and trend analysis,
not billing.

### Optimization projections assume similar traffic

`agenticlens optimize` projects savings from the analysed traces. Compression
and reranking benefits are configured or best-case assumptions, prompt-caching
cost is pro-rated by token share, and outcome evaluation compares two traffic
windows without controlling for other changes shipped in between.

### Comparison is descriptive only

`agenticlens compare` reports descriptive statistics (mean, median, P95,
standard deviation). It does not claim statistical significance or causal
attribution, especially for small or uncontrolled samples. For significance
tests and confidence intervals, use `agenticlens experiment run`.

### Experiments

- One suite per experiment; every variant must answer the same cases.
- No multiple-comparison correction across variants.
- Live variants run trials sequentially; `--max-workers` parallelises cases
  within a trial only.

See [Experiments](experiments.md#limitations).

### Diagnosis sees only the recorded trace

Rules and attribution follow what the trace recorded. A root cause outside the
trace (for example an upstream data change) is reported as the first recorded
symptom. Anomaly detection assumes baseline runs of the same workflow and does
not correct for multiple comparisons. See [Diagnosis](diagnosis.md#limitations).

### ModelFit and routing use only your evidence

ModelFit does not call models or use public benchmarks; it ranks only the
variants in experiment reports you recorded. Routing runs
through host-owned callbacks, and Lens does not authenticate approvers. See
[ModelFit](modelfit.md) and [Routing](routing.md).

---

## Evaluation

### No built-in provider clients

AgenticLens does not ship LLM clients for evaluation. You supply the
callable that calls your model. The `LLMJudgeEvaluator` wraps your function
and normalizes the score; it does not make model API calls itself.

### Synchronous evaluator APIs

Evaluator APIs such as `evaluate_suite` are synchronous. `evaluate-live
--max-workers N` calls a live target for several cases at once, but async
evaluator APIs are roadmap work.

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

## Enterprise artifact service

The optional artifact service (`agenticlens[api]`) uses SQLite as a trusted
single-node boundary: run one worker on local block storage. Horizontal
scaling, OIDC/SSO and high availability are outside this release. Deleting data
does not erase SQLite free pages or backups, and registry and audit records are
not removed by trace retention. See [Production readiness](production-readiness.md).

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

AgenticLens supports Python 3.10 to 3.14. Older Python versions are not
supported.
