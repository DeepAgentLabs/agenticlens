# AgenticLens

![AgenticLens logo](assets/agenticlens-logo.jpeg){ width="420" }

**Open-source observability, evaluation, and operational intelligence for
production AI systems.**

[![CI](https://github.com/DeepAgentLabs/agenticlens/actions/workflows/ci.yml/badge.svg)](https://github.com/DeepAgentLabs/agenticlens/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agenticlens.svg)](https://pypi.org/project/agenticlens/)
[![GitHub stars](https://img.shields.io/github/stars/DeepAgentLabs/agenticlens?style=social)](https://github.com/DeepAgentLabs/agenticlens/stargazers)
[![PyPI downloads](https://static.pepy.tech/badge/agenticlens/month)](https://pepy.tech/project/agenticlens)

AgenticLens helps teams profile LLM applications, capture structured agent
traces, calculate cost, diagnose memory and retry overhead, and compare
candidate configurations against reviewed baselines.

## What It Measures

| Dimension | What AgenticLens captures |
| --- | --- |
| Step token use | Prompt tokens, completion tokens, total tokens by workflow step |
| Cost | Provider pricing, dollar-per-run, monthly projections |
| Latency | Step-level runtime and tokens per second |
| Workflow shape | Planner, retriever, tool, memory, and final-response steps |
| Waste patterns | Repeated prompts, excessive chunks, duplicate tool calls, long history |
| Quality risk | Confidence and risk notes for optimization recommendations |
| Resilience | Fault-injection outcomes through the `chaos_events` schema extension |
| Tracing | Hierarchical runs and spans with status and error evidence |
| Comparison | Success, tokens, latency, cost, variability, and regression deltas |

## Token Optimization Focus

AgenticLens reports token savings at the step where the waste occurs:

| Area | Optimization signal |
| --- | --- |
| Prompting | Repeated prompt prefixes that should be cached or deduplicated |
| RAG | Excessive top-k retrieval and low-utility retrieved chunks |
| Memory | Conversation history that should be summarized or truncated |
| Tools | Duplicate tool calls that should be cached |
| Multi-agent handoffs | Oversized context passed between agents |
| Workflow | Estimated reducible tokens, cost per run, and monthly savings |

Multi-agent workflows can attach `agent_name`, `agent_role`, and handoff metadata
to each step. AgenticLens then reports token usage by agent and flags oversized
handoffs that should be summarized before passing context to the next agent.

## Why It Matters

Production agent systems fail in ways that ordinary request logs rarely explain.
Token cost can drift across memory, retrieval, planning, and tool use. Reliability
can degrade silently when an upstream tool fails. AgenticLens keeps these signals
local, inspectable, and exportable so teams can compare workflows across versions.

## Documentation

- [Workflow schema specification](workflow-schema-spec.md)
- [Export formats](export-formats.md)
- [RAG chunk utility](rag-chunk-utility.md)
- [Trace and comparison](trace-and-comparison.md)
- [Evaluation and release gates](evaluation-and-release-gates.md)
- [Multi-agent reference workflows](multi-agent-reference-workflows.md)
- [Product roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/agenticlens-roadmap.md)
- [Research roadmap](https://github.com/DeepAgentLabs/agenticlens/blob/main/AgenticLens_Research_and_Development_Roadmap.md)

## Quickstart

```python
from agenticlens import profile, step

with profile("Customer Support"):
    with step("Planner", type="planner") as s:
        response = planner_llm.invoke(prompt)
        s.record(response)
```

```bash
uv run agenticlens profile examples/recommendations_demo.py --save workflow.json
uv run agenticlens analyze workflow.json
```

## Current Status

AgenticLens is early-stage open-source software. Workflow profiling, live and
offline pricing, optimization recommendations, structured tracing, deterministic
memory and retry findings, repeated-run comparison, evaluation suites, release
gates, CLI commands, and export formats are implemented. The trace,
comparison, and evaluation APIs remain experimental. Framework adapters,
OpenTelemetry export, and the optional dashboard remain roadmap work.
