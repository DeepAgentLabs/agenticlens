# AgenticLens

> One decorator to profile, observe, and chaos-test any LLM call — framework-agnostic, provider-agnostic, zero config.


---

## What is AgenticLens?

`AgenticLens` is a Python package that brings **profiling** and **chaos engineering** specifically to LLM function calls — via simple decorators requiring zero configuration.

It is the first framework-agnostic, provider-agnostic library of its kind. Drop one decorator on any function that calls an LLM and instantly get a clean profile card with latency, token usage, cost, retries, and status.

---

## Install

```bash
pip install agentic-lens
```

---

## What's Inside

| Decorator | Purpose |
|---|---|
| `@token_trace` | Profiles every LLM call — latency, tokens, cost, retries, status |
| `@token_chaos` | Injects controlled failures to test resilience of your LLM calls |

---

## `@token_trace`

### Usage

```python
from agentic_lens import token_trace

@token_trace
def ask_gpt(prompt):
    return openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

That's it. Run your function and get this automatically:

### Output — Profile Card

```
╔══════════════════════════════════════╗
║           AI Profile                 ║
╠══════════════════════════════════════╣
║  Model        │  GPT-4o              ║
║  Provider     │  OpenAI              ║
║  Latency      │  1.84 s              ║
║  TTFT         │  0.34 s              ║
╠══════════════════════════════════════╣
║  Input Tokens │  1,230               ║
║  Output Tokens│  412                 ║
║  Total Tokens │  1,642               ║
║  Cost         │  $0.028              ║
╠══════════════════════════════════════╣
║  Tools Used   │  3                   ║
║  Retries      │  0                   ║
║  Status       │  ✅ Success          ║
╚══════════════════════════════════════╝
```

### What it captures

| Field | Description |
|---|---|
| Model | Model name returned by the provider |
| Provider | OpenAI, Anthropic, Gemini, Ollama, etc. |
| Latency | Total wall-clock time for the call |
| TTFT | Time to first token (for streaming calls) |
| Input Tokens | Prompt token count |
| Output Tokens | Completion token count |
| Total Tokens | Combined token count |
| Cost | Estimated cost in USD based on current model pricing |
| Tools Used | Number of tool/function calls made by the model |
| Retries | How many retries occurred before success |
| Status | Success, Failed, or Chaos Injected |

### Session Summary

When multiple calls are made, `AgenticLens` also tracks a rolling session summary:

```
╔══════════════════════════════════════╗
║        Session Summary               ║
╠══════════════════════════════════════╣
║  Total Calls  │  5                   ║
║  Total Cost   │  $0.14               ║
║  Avg Latency  │  2.1 s               ║
║  Total Tokens │  8,420               ║
║  Failures     │  1                   ║
╚══════════════════════════════════════╝
```

---

## `@token_chaos`

### Usage

```python
from agentic_lens import token_chaos

@token_chaos(
    modes=["latency", "empty_response", "rate_limit"],
    rate=0.2,        # 20% of calls get chaos'd
    severity="high",
    seed=42          # reproducible chaos for CI/CD
)
def ask_gpt(prompt):
    ...
```

### Chaos Modes

| Mode | What it does |
|---|---|
| `latency_spike` | Delays response by 3–10x normal time |
| `empty_response` | Returns a blank string instead of a real response |
| `truncated_response` | Cuts the output mid-sentence |
| `rate_limit_error` | Raises `RateLimitError` |
| `timeout_error` | Raises `APITimeoutError` |
| `garbled_response` | Returns junk / random text |
| `token_overflow` | Simulates `finish_reason: length` |
| `slow_stream` | Stalls streaming chunks artificially |
| `hallucination_inject` | Swaps known facts in the response |
| `cost_spike` | Simulates runaway token usage |

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `modes` | `list[str]` | `["latency_spike"]` | Which failure modes to enable |
| `rate` | `float` | `0.1` | Fraction of calls that get chaos'd (0.0–1.0) |
| `severity` | `str` | `"medium"` | How extreme the chaos is: `low`, `medium`, `high` |
| `seed` | `int` | `None` | Fixed seed for reproducible chaos in CI/CD |

---

## Stack Both Decorators

```python
from agentic_lens import token_trace, token_chaos

@token_trace              # captures what happened
@token_chaos(rate=0.1)    # randomly breaks things
def ask_gpt(prompt):
    return openai.chat.completions.create(...)
```

Profile card shows chaos context inline:

```
╔══════════════════════════════════════╗
║           AI Profile                 ║
╠══════════════════════════════════════╣
║  Model        │  GPT-4o              ║
║  Latency      │  8.4 s               ║
║  Cost         │  $0.028              ║
╠══════════════════════════════════════╣
║  Chaos Mode   │  ON 🔴               ║
║  Injected     │  Latency Spike       ║
║  Severity     │  High                ║
║  App handled  │  ✅ Yes              ║
║  Status       │  Chaos Injected      ║
╚══════════════════════════════════════╝
```

---

## Works With Any Provider

```python
# OpenAI
@token_trace
def call_openai(prompt):
    return openai.chat.completions.create(...)

# Anthropic
@token_trace
def call_claude(prompt):
    return anthropic.messages.create(...)

# Gemini
@token_trace
def call_gemini(prompt):
    return genai.generate_content(...)

# Ollama (local)
@token_trace
def call_ollama(prompt):
    return requests.post("http://localhost:11434/api/generate", ...)
```

Same decorator. Same output format. Any LLM.

---

## Emit To

By default `AgenticLens` prints to console. You can also emit to:

| Destination | How |
|---|---|
| Console | Default — no config needed |
| OpenTelemetry | `token_trace(emit="otel")` |
| Prometheus | `token_trace(emit="prometheus")` |
| JSON file | `token_trace(emit="json", path="./traces.json")` |
| Custom callback | `token_trace(emit=my_function)` |

---

## Why AgenticLens?

| Existing tool | Gap |
|---|---|
| LangSmith, LangFuse | Tied to LangChain ecosystem |
| OpenTelemetry | You wire everything manually |
| OpenAI dashboard | Only works for OpenAI, no code-level integration |
| `time.time()` DIY | Everyone reinvents this themselves |
| Chaos Monkey / Gremlin | Infrastructure-level only, not LLM-aware |

`AgenticLens` is the only tool that combines **profiling + chaos engineering** in a single, decorator-first, provider-agnostic Python package.

---

## Roadmap

- [ ] `v0.1` — `@token_trace` with console output
- [ ] `v0.2` — `@token_chaos` with core modes
- [ ] `v0.3` — OpenTelemetry and Prometheus emit
- [ ] `v0.4` — Session summary and cost budgets
- [ ] `v0.5` — Streaming support and TTFT tracking
- [ ] `v1.0` — Stable API, full provider support

---

## License

MIT © AgenticLens contributors
