# Limitations

This page documents known limitations of AgenticLens 0.5.0. Planned
improvements appear in [Roadmap](roadmap.md).

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
