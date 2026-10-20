# Getting Started

AgenticLens is a local-first observability, evaluation, and operational
intelligence toolkit for production agentic AI systems. No hosted backend,
no mandatory account, no data egress required.

**Version:** 0.5.0 · **Status:** Alpha

---

## Requirements

- Python 3.10 or later
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

---

## Installation

```bash
pip install agenticlens
```

Or with uv:

```bash
uv add agenticlens
```

### Optional extras

| Extra | Installs | When to use |
|-------|----------|-------------|
| `langgraph` | LangGraph ≥ 1.0 | Running the reference LangGraph supervisor workflow |
| `multi-agent` | LangGraph ≥ 1.0 | Same as `langgraph` |
| `docs` | MkDocs Material ≥ 9.5 | Building this documentation site locally |
| `api` | FastAPI + uvicorn | Running the live OTLP receiver and real-time dashboard |

```bash
pip install "agenticlens[langgraph]"
pip install "agenticlens[api]"
```

---

## Quickstart — profiling a workflow

The fastest way to start is the `profile()` / `step()` API:

```python
from agenticlens import profile, step

with profile("Customer Support"):
    with step("Planner", type="planner") as s:
        response = planner_llm.invoke(prompt)
        s.record(response)          # captures token usage from provider response

    with step("Retriever", type="retriever", chunk_count=6, avg_tokens_per_chunk=80):
        chunks = retriever.retrieve(query)

    with step("Final Answer", type="final_response") as s:
        answer = answer_llm.invoke(context)
        s.record(answer)
```

Save and analyze the workflow artifact:

```bash
uv run agenticlens profile examples/recommendations_demo.py --save workflow.json
uv run agenticlens analyze workflow.json
```

---

## Quickstart — structured tracing

For hierarchical multi-agent runs, use the `trace()` API:

```python
from agenticlens import SpanType, trace

with trace("support-agent", environment="production") as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)

    with recording.span("memory", SpanType.MEMORY_READ) as memory:
        memory.record_tokens(input_tokens=80)

recording.save("run.json")
```

Inspect the saved run:

```bash
agenticlens inspect run.json
```

---

## CLI overview

| Command | Purpose |
|---------|---------|
| `agenticlens profile <script>` | Run and profile a Python workflow script |
| `agenticlens analyze <workflow.json>` | Analyze token use, cost, and waste |
| `agenticlens inspect <run.json>` | Inspect a structured trace run |
| `agenticlens compare <baseline/> <candidate/>` | Compare repeated runs |
| `agenticlens evaluate <suite.yaml> <samples.json>` | Run an evaluation suite |
| `agenticlens gate <evaluation.json>` | Apply a release gate |
| `agenticlens validate <artifact.json>` | Validate against AIOS schema |
| `agenticlens conformance <run.json>` | Run full AIOS conformance checks |
| `agenticlens dashboard` | Render a combined HTML dashboard |
| `agenticlens serve-otlp` | Start the live OTLP receiver (requires `[api]`) |
| `agenticlens history` | View cross-trace history from a DB or directory |
| `agenticlens import-otlp <otlp.json>` | Import an OTLP trace into AgenticLens format |
| `agenticlens dataset summary <dataset.json>` | Summarize a versioned evaluation dataset |
| `agenticlens dataset split <dataset.json>` | Assign train/validation/test splits |
| `agenticlens dataset export-samples <dataset.json>` | Export a split for evaluation |
| `agenticlens calibrate <evaluation.json> <labels.json>` | Run judge calibration |

---

## Next steps

- [Architecture](architecture.md) — how the layers fit together
- [Features](features.md) — every implemented capability with status labels
- [Configuration](configuration.md) — pricing, thresholds, and settings
- [CLI reference](cli-reference.md) — full flag reference for every command
- [API reference](api-reference.md) — Python API documentation
- [Examples](examples.md) — runnable end-to-end examples
