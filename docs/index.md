# AgenticLens

![AgenticLens logo](assets/agenticlens-logo.jpeg){ width="420" }

**Step-level token optimization for production-ready agentic AI systems.**

[![CI](https://github.com/DeepAgentLabs/agenticlens/actions/workflows/ci.yml/badge.svg)](https://github.com/DeepAgentLabs/agenticlens/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/agenticlens.svg)](https://pypi.org/project/agenticlens/)
[![GitHub stars](https://img.shields.io/github/stars/DeepAgentLabs/agenticlens?style=social)](https://github.com/DeepAgentLabs/agenticlens/stargazers)
[![PyPI downloads](https://static.pepy.tech/badge/agenticlens/month)](https://pepy.tech/project/agenticlens)

AgenticLens helps teams profile LLM applications, measure token use at each step,
and turn traces into practical optimization recommendations for production agent
systems.

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
- [Technical specification](https://github.com/DeepAgentLabs/agenticlens/blob/main/AgenticLens_Spec.md)

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

AgenticLens is early-stage open-source software. The core profiler, CLI, export
formats, pricing model, and recommendation engine are implemented. Integrations
for agent frameworks, trace formats, and workflow explorers are active roadmap
priorities.
