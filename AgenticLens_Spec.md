# AgenticLens — Project Master Specification (MVP)

---

## Project Overview

**AgenticLens** is an open-source Python library that helps developers **profile, analyze, and optimize token consumption** in LLM-powered applications and agentic workflows.

Unlike traditional observability tools that only display token usage and cost, AgenticLens explains:

- **Where** tokens were consumed
- **Why** they were consumed
- **Which** workflow step was responsible
- **Which** tool calls were expensive
- **How** developers can reduce token usage and cost

> **Design principle:** Framework-agnostic and provider-agnostic.

---

## Vision

Modern AI applications consist of multiple LLM calls, planning agents, memory systems, retrieval pipelines, tool calls, MCP servers, and multi-agent workflows.

Current observability tools show traces and token counts but provide **limited guidance on optimization**.

AgenticLens should become the **"performance profiler" for AI applications**, similar to:

| Analogy | Domain |
|---|---|
| `cProfile` | Python runtime |
| Chrome DevTools | Browser performance |
| TensorBoard | ML training |

### The library should ultimately answer three questions

1. Where did the tokens go?
2. Why were they spent?
3. How can developers reduce them?

---

## Initial Scope (MVP)

The first version focuses on **profiling and reporting**.

> **Out of scope for MVP:** dashboards, databases, web applications, enterprise features.

Keep the MVP lightweight and suitable for publishing as a PyPI package.

---

## Primary Features

### 1. Workflow Profiler

Profile an entire workflow with a single context manager:

```python
from agenticlens import profile

with profile("Customer Support"):
    agent.run(question)
```

The profiler establishes the workflow context (start/end time, id) but does **not** auto-capture LLM calls — see [Instrumentation Model](#instrumentation-model) below.

---

### 2. Step Profiling

Every workflow consists of multiple steps. Each step should have independent metrics, and is wrapped **explicitly** by the developer:

```python
from agenticlens import profile, step

with profile("Customer Support"):
    with step("Planner", type="planner") as s:
        plan = planner_llm.invoke(prompt)
        s.record(plan)  # attaches token usage from the provider response

    with step("Retriever", type="retriever") as s:
        chunks = retriever.search(query)

    with step("Final Response", type="llm_call") as s:
        answer = response_llm.invoke(context)
        s.record(answer)
```

`step()` yields a handle whose `.record(response)` extracts token usage from a provider response (auto-detected via the provider registry) and attaches it to the step. Steps are recorded against the currently active workflow via a `contextvar`-based stack, so calling `step()` outside of a `profile()` block raises a clear error.

**Example step types:**

- Planner
- Retriever
- Tool Call
- LLM Call
- Memory
- Final Response

#### Instrumentation Model

> **Decision:** AgenticLens uses an **explicit step API**, not automatic SDK monkey-patching.

Rationale:

- Reliable across provider SDK versions — no breakage when OpenAI/Anthropic change internal client internals.
- Testable without mocking global state.
- Step boundaries (Planner vs. Retriever vs. Tool Call) are a workflow concept the library cannot infer reliably; the developer already knows them.

Trade-off accepted: integrating AgenticLens requires adding `with step(...):` around LLM/tool calls. This cost is acceptable for an MVP and can be revisited post-MVP with optional auto-instrumentation adapters (e.g. for LangChain callbacks) once the core model is stable.

---

### 3. Token Metrics

Collected per step:

| Metric | Description |
|---|---|
| `prompt_tokens` | Tokens in the input prompt |
| `completion_tokens` | Tokens in the model output |
| `total_tokens` | Sum of prompt + completion |

---

### 4. Cost Metrics

| Metric | Description |
|---|---|
| `input_cost` | Cost of prompt tokens |
| `output_cost` | Cost of completion tokens |
| `total_cost` | Total spend for the step |

**Pricing source of truth:** live pricing fetched from [LiteLLM's community-maintained pricing feed](https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json), cached on disk with a TTL (default 24h) so cost lookups don't hit the network on every step. Resolution order:

1. User-supplied pricing override (via `pyproject.toml` / YAML config / env var) — always wins.
2. Live pricing feed, if `live_pricing.enabled` (default `True`) and reachable — matched by exact model name, `provider/model`, or a known alias for versioned model names (e.g. `claude-3-5-sonnet` → `claude-3-5-sonnet-20241022`).
3. Bundled static `pricing.yaml` fallback for the exact `provider:model` — used when live pricing is disabled, unreachable, and no cached copy exists.
4. Unknown model → cost fields are `None` and a `UnknownModelPricingWarning` is emitted. **Never silently report `$0.00`** for an unpriced model — that's misleading, not a graceful fallback.

Live pricing can be disabled per-config (`live_pricing.enabled: false`) or hard-disabled via the `AGENTICLENS_DISABLE_LIVE_PRICING` env var (used by this project's own test suite to stay hermetic).

---

### 5. Performance Metrics

| Metric | Description |
|---|---|
| `latency` | Total step duration |
| `ttft` | Time To First Token. `float \| None` — only populated when the wrapped call is a streaming call; `None` for non-streaming calls (the common case). Not an error or missing-data condition. |
| `tps` | Tokens Per Second (`completion_tokens / latency`) |

---

### 6. Workflow Summary Output

```
╔══════════════════════════════╗
║   Customer Support Agent     ║
╠══════════════════════════════╣
║  Total Tokens    │  24,581   ║
║  Total Cost      │  $0.24    ║
║  Latency         │  18.2 sec ║
╚══════════════════════════════╝
```

---

### 7. Step Breakdown Output

```
Planner
───────────────────────────────
  Prompt Tokens      850
  Completion Tokens  210
  Cost               $0.02
  Latency            1.1 sec
```

Repeated for every workflow step.

---

## Recommendation Engine (Rule-Based)

AgenticLens does not stop at reporting — it **analyzes** the workflow and generates actionable optimization suggestions.

> Initial recommendations use **simple heuristics**, not AI-generated analysis.

### MVP Heuristic Rules

Each rule below detects a pattern and estimates the tokens it would save (`tokens_saved`), which feeds the savings calculation.

| Rule | Detection logic | `tokens_saved` estimate |
|---|---|---|
| **Repeated system prompt** | Hash the first N tokens (configurable, default 50) of each step's prompt. If the same hash appears in ≥2 steps, flag all occurrences after the first. | Sum of token counts of the repeated prefix across the duplicate occurrences. |
| **Excessive retrieved chunks** | Retriever step returns more than `max_chunks` (configurable, default 8) chunks. | `(chunk_count - max_chunks) × avg_tokens_per_chunk`. |
| **Long conversation history** | A step's `prompt_tokens` attributable to history/memory content exceeds `history_token_limit` (configurable, default 4000). | `prompt_tokens_from_history - history_token_limit`. |
| **Duplicate tool calls** | Two or more Tool Call steps in the same workflow share an identical `(tool_name, arguments)` signature. | Sum of `prompt_tokens + completion_tokens` for every duplicate occurrence after the first. |

All thresholds live in `RecommenderConfig` and are user-overridable; defaults above are starting points, not hard-coded constants.

### Model-Swap Simulator

Unlike the token-pattern rules above, this one is cost-driven: for each step with
a known `provider`/`model`, it recomputes the step's cost and compares it
against a pool of candidate models with the *same token usage*, surfacing the
cheapest viable swap.

- **Candidate pool**: primarily the live LiteLLM pricing feed (see "Cost
  Metrics" below), filtered to `mode == "chat"`, excluding fine-tune (`ft:`)
  entries, and restricted to a curated allowlist of direct/first-party model
  providers — `openai, anthropic, gemini, mistral, xai, deepseek, groq,
  cohere_chat, perplexity` (configurable via `RecommenderConfig.model_swap_providers`).
  Deliberately excludes gateway/reseller re-hosts of the same underlying model
  (`bedrock`, `azure`, `vertex_ai-*`, `openrouter`, ...) — swapping to those is
  an infra decision, not a genuine model swap. Falls back to the small bundled
  static pricing table when live pricing is disabled or unreachable.
- **Context-window safety check**: candidates whose `max_input_tokens` (from
  the live feed) is smaller than the step's `prompt_tokens` are skipped, so a
  swap is never recommended if it would flat out fail.
- **Threshold**: only recommends when savings clear
  `RecommenderConfig.model_swap_min_savings_pct` (default 15%).
- Sets `Recommendation.cost_savings` (a dollar amount) rather than
  `tokens_saved`/`estimated_savings`, since token counts don't change on a
  model swap — only cost does.

### Estimated Savings Formula

```
estimated_savings_pct = min(100, (sum(tokens_saved for all triggered rules) / workflow.total_tokens) * 100)
```

Each `Recommendation` carries its own `estimated_savings` (per-rule token %), and the workflow summary reports the aggregate using the formula above. Cost-based recommendations (the model-swap simulator) carry `cost_savings` (a dollar amount) instead, aggregated separately via `RecommendationEngine.estimated_cost_savings()` and rendered as a parallel "Estimated Cost Savings" line — the two aggregates use different units and are not combined into one number.

**Example output:**

```
Optimization Suggestions
────────────────────────
  ✓ Planner repeated system prompt
  ✓ Retrieved 12 chunks
    └─ Only 4 appear to be useful

Estimated Savings: 31%
```

---

## Architecture

The project is modular, with each package having a single responsibility.

```
src/agenticlens/
├── profiler/       # Workflow and step profiling logic
├── metrics/        # Token, cost, and performance collection
├── providers/      # LLM provider integrations
├── analyzers/      # Workflow analysis and pattern detection
├── recommenders/   # Rule-based optimization recommendations
├── exporters/      # JSON and CSV export
├── cli/            # Typer-based CLI
├── config/         # Configuration loading
├── models/         # Pydantic data models
└── utils/          # Shared utilities
```

---

## Core Data Models

All models are implemented with **Pydantic v2**.

### `Workflow`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier |
| `name` | `str` | Workflow name |
| `start_time` | `datetime` | Execution start |
| `end_time` | `datetime` | Execution end |
| `total_tokens` | `int` | Aggregate token count |
| `total_cost` | `float` | Aggregate cost |
| `latency` | `float` | Wall-clock duration |
| `steps` | `list[Step]` | All profiled steps |

---

### `Step`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier |
| `name` | `str` | Step label |
| `type` | `StepType` | Enum (planner, retriever, tool, etc.) |
| `provider` | `str` | LLM provider name |
| `model` | `str` | Model identifier |
| `metrics` | `Metrics` | Step-level metrics |

---

### `Metrics`

| Field | Type | Description |
|---|---|---|
| `prompt_tokens` | `int` | Input token count |
| `completion_tokens` | `int` | Output token count |
| `total_tokens` | `int` | Combined count |
| `latency` | `float` | Duration in seconds |
| `ttft` | `float \| None` | Time To First Token |
| `cost` | `float` | Calculated cost |

---

### `Recommendation`

| Field | Type | Description |
|---|---|---|
| `title` | `str` | Short recommendation title |
| `description` | `str` | Detailed explanation |
| `severity` | `Severity` | Enum: `info`, `warning`, `critical` |
| `tokens_saved` | `int` | Token count the rule expects to save |
| `estimated_savings` | `float \| None` | Projected % token reduction |
| `cost_savings` | `float \| None` | Projected dollar savings (cost-aware rules, e.g. model swap); a different unit from `estimated_savings` and not combined with it |

---

## Provider Architecture

Providers are independent modules behind an **abstract interface**, so additional providers can be added without modifying the profiler.

### Initial providers

| Provider | Status |
|---|---|
| OpenAI | ✅ MVP |
| Anthropic | ✅ MVP |

### Future providers

| Provider | Status |
|---|---|
| Gemini | 🔜 Roadmap |
| Ollama | 🔜 Roadmap |
| vLLM | 🔜 Roadmap |
| LiteLLM | 🔜 Roadmap |
| Azure OpenAI | 🔜 Roadmap |

---

## CLI

Built with **Typer** and **Rich** for terminal output.

```bash
# Profile a script
agenticlens profile app.py

# Display a saved report
agenticlens report report.json

# Analyze a saved workflow
agenticlens analyze workflow.json
```

---

## Exporters

| Format | Status |
|---|---|
| JSON | ✅ MVP |
| CSV | ✅ MVP |

---

## Configuration

Configuration is supported through any of:

- `pyproject.toml`
- YAML file
- Environment variables

---

## Technology Stack

| Concern | Choice |
|---|---|
| Language | Python 3.10+ |
| Package Manager | `uv` |
| Packaging | `pyproject.toml` |
| Testing | `pytest` |
| Linting | `ruff` |
| Formatting | `ruff format` |
| Type Checking | `mypy` |
| Documentation | MkDocs Material |
| CLI | Typer |
| Terminal Output | Rich |
| Data Models | Pydantic v2 |

---

## Coding Standards

- Full **type hints** throughout
- **Async-friendly** architecture
- **Modular design** — single responsibility per module
- No global mutable state
- Unit tests for every module
- Comprehensive docstrings
- Clean separation between providers, metrics, and analyzers

---

## Repository Structure

```
agenticlens/
├── README.md
├── LICENSE
├── ROADMAP.md
├── pyproject.toml
├── src/
│   └── agenticlens/
├── tests/
├── examples/
├── docs/
└── .github/
    └── workflows/
```

---

## MVP Deliverables

The initial implementation includes:

- [ ] Repository scaffold
- [ ] Project configuration (`pyproject.toml`, `ruff`, `mypy`)
- [ ] Complete package structure
- [ ] Data models (Pydantic v2)
- [ ] Provider abstraction (abstract base class)
- [ ] Profiler skeleton
- [ ] Metrics engine skeleton
- [ ] CLI skeleton (Typer)
- [ ] Unit test setup (pytest)
- [ ] GitHub Actions CI pipeline
- [ ] Documentation structure (MkDocs)

> Business logic is implemented incrementally after the scaffold is complete.

---

## Scaffold-First Instructions

> **The first task is NOT to implement the complete library.**

In order:

1. Scaffold the complete repository
2. Create all directories
3. Configure tooling (ruff, mypy, pytest)
4. Configure CI (GitHub Actions)
5. Configure packaging (pyproject.toml, uv)
6. Create all base classes and interfaces
7. Create placeholder implementations where appropriate
8. Ensure the project installs successfully
9. Ensure linting, formatting, typing, and tests pass
10. **Do not implement optimization algorithms until project structure is complete**

> **Objective:** Create a production-quality open-source project foundation that can be incrementally expanded.

---

## Future Roadmap

| Feature | Notes |
|---|---|
| LangGraph integration | Native graph-step profiling |
| CrewAI integration | Multi-agent workflow support |
| OpenAI Agents SDK integration | Tool call + handoff tracing |
| MCP profiling | Server-level token attribution |
| RAG analysis | Chunk utility scoring |
| Prompt optimization | Automated prompt compression |
| Context utilization metrics | Effective context window usage |
| Evaluation framework | Quality vs. cost tradeoffs |
| Dashboard | Visual workflow explorer |
| Enterprise reporting | Team-level aggregation and export |

> All items above are **out of scope for MVP**.
