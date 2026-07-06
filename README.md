# AgenticLens

AgenticLens is an open-source profiler for LLM applications, RAG pipelines, and agentic workflows.

It helps developers understand where tokens, cost, and latency are being spent across each step of an AI workflow.

> **Status:** MVP. Core profiling, CLI reports, exporters, and heuristic recommendation rules are implemented.

AgenticLens tracks:

- Prompt tokens
- Completion tokens
- Total tokens
- Estimated cost
- Latency
- Workflow steps
- Tool calls
- Retrieval metadata
- Optimization opportunities

## Why AgenticLens?

LLM applications often become expensive and slow as they grow from simple prompts into RAG pipelines, tool-using agents, and multi-agent workflows.

AgenticLens gives developers a lightweight way to answer:

- Which step used the most tokens?
- Which agent was most expensive?
- Did retrieval send too many chunks?
- Is conversation history too large?
- Are we repeating the same system prompt?
- Did the workflow call the same tool twice?
- How much token usage can be reduced?

## Installation

### From PyPI

```bash
pip install agenticlens
```

### Development Install

```bash
uv sync --extra dev
```

or:

```bash
pip install -e .
```

## Quick Start

```python
from agenticlens import profile, step

with profile("Customer Support") as workflow:
    with step(
        "Planner",
        type="planner",
        provider="openai",
        model="gpt-4o-mini",
    ) as s:
        response = planner_llm.invoke(prompt)
        s.record(response)

print(workflow.total_tokens)
print(workflow.total_cost)
```

## Core Concepts

| Concept | Meaning |
|---|---|
| `profile()` | Starts profiling one workflow |
| `step()` | Tracks one operation inside the workflow |
| `s.record(response)` | Extracts token usage from an LLM response |
| `provider` | LLM provider, such as `openai` or `anthropic` |
| `model` | Model name used for cost estimation |
| `metadata` | Extra step details such as retrieved chunks, tool names, prompts, or history size |

## Supported Step Types

AgenticLens supports these step types:

```text
planner
retriever
memory
tool_call
llm_call
final_response
```

## CLI Usage

Run and profile a Python script:

```bash
agenticlens profile examples/basic_usage.py
```

Save a workflow report:

```bash
agenticlens profile examples/basic_usage.py --save report.json
```

View a saved report:

```bash
agenticlens report report.json
```

Analyze optimization opportunities:

```bash
agenticlens analyze report.json
```

## Example Output

```text
╔═ Customer Support ═╗
║ Total Tokens   160 ║
║ Total Cost     $0.00 ║
║ Latency        0.12 sec ║
╚═══════════════════╝

Step Breakdown

Planner    planner    120 prompt    40 completion
```

## RAG Example

```python
from agenticlens import profile, step

with profile("RAG Workflow") as workflow:
    with step(
        "Retrieve Chunks",
        type="retriever",
        chunk_count=5,
        avg_tokens_per_chunk=120,
    ):
        chunks = retriever.search(query)

    with step(
        "Generate Answer",
        type="llm_call",
        provider="openai",
        model="gpt-4o-mini",
    ) as s:
        response = llm.invoke(query, context=chunks)
        s.record(response)
```

## Multi-Agent Example

```python
from agenticlens import profile, step

with profile("Multi-Agent Support Workflow") as workflow:
    with step(
        "Planner Agent",
        type="planner",
        provider="openai",
        model="gpt-4o-mini",
    ) as s:
        response = planner_agent.run(user_query)
        s.record(response)

    with step(
        "Retriever Agent",
        type="retriever",
        chunk_count=8,
    ):
        chunks = retriever.search(user_query)

    with step(
        "Tool Agent - Lookup Order",
        type="tool_call",
        tool_name="lookup_order",
        tool_args={"order_id": "A123"},
    ):
        order = lookup_order("A123")

    with step(
        "Final Response Agent",
        type="final_response",
        provider="openai",
        model="gpt-4o-mini",
    ) as s:
        response = final_agent.run(user_query, chunks, order)
        s.record(response)
```

## Optimization Recommendations

AgenticLens can identify common token waste patterns:

| Recommendation | Meaning |
|---|---|
| Repeated system prompt | Same long prompt appears across multiple steps |
| Excessive retrieved chunks | Retriever sends more chunks than the configured limit |
| Long conversation history | Memory/history exceeds the configured token threshold |
| Duplicate tool call | Same tool is called again with the same arguments |

Example:

```bash
agenticlens analyze report.json
```

Output:

```text
Optimization Suggestions

* Repeated system prompt
  -- Step 'Final Response' repeats the same prompt prefix as 'Planner'. (~295 tokens)

* Excessive retrieved chunks
  -- Step 'Retriever' retrieved 12 chunks, 4 more than the configured limit of 8. (~320 tokens)

Estimated Savings: 32%
```

## Exporters

AgenticLens supports exporting workflow reports.

```python
from agenticlens.exporters import JSONExporter, CSVExporter

JSONExporter().export(workflow, "report.json")
CSVExporter().export(workflow, "steps.csv")
```

## Examples

Example scripts are available in:

```text
examples/basic_usage.py
examples/recommendations_demo.py
examples/rag_customer_support_demo.py
examples/multiagent_support_demo.py
```

## Notebooks

Beginner-friendly notebooks are available in:

```text
notebooks/agenticlens_workflow_demo_beginner.ipynb
notebooks/agenticlens_multiagent_demo_beginner.ipynb
```

The notebooks show:

- Step-by-step RAG profiling
- Step-by-step multi-agent profiling
- Token usage tables
- Latency charts
- Cost charts
- Saved AgenticLens reports
- Optimization analysis

## Development

Install development dependencies:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Format code:

```bash
uv run ruff format .
```

Run type checks:

```bash
uv run mypy
```

## Test Status

The current test suite covers:

- CLI commands
- Profiling API
- Models
- Providers
- Pricing
- Exporters
- Recommendation engine
- Recommendation rules

Example:

```bash
pytest -v
```

Expected result:

```text
42 passed
```

## Project Docs

See:

- [AgenticLens_Spec.md](AgenticLens_Spec.md)
- [ROADMAP.md](ROADMAP.md)

## Positioning

AgenticLens is a lightweight, developer-first profiler for token usage, cost, latency, and optimization suggestions.

It is not intended to replace full observability platforms such as LangSmith, Langfuse, Helicone, or Phoenix. It is designed to be simple, local-first, and easy to add to Python-based LLM workflows.

## License

MIT