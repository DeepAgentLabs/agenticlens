# Multi-Agent Reference Workflow

AgenticLens includes a verified offline LangGraph supervisor workflow based on
the orchestration patterns published by the official LangGraph repositories.

## LangGraph Supervisor

The workflow uses a compiled LangGraph `StateGraph`. A supervisor delegates work
to research, calculation, and review agents. AgenticLens records delegation,
retrieval, tool, and final-response spans during the actual graph execution.

```bash
uv sync --extra langgraph
uv run python examples/reference_workflows/langgraph_supervisor.py
uv run agenticlens inspect examples/reference_workflows/artifacts/langgraph-supervisor.json
```

The workflow is deterministic and does not require a provider account or API
key. Its saved reference artifact is maintained at:

```text
examples/reference_workflows/artifacts/langgraph-supervisor.json
```

## Optional Dependency

LangGraph remains optional. Installing the AgenticLens core package does not
install it.

```bash
uv sync --extra multi-agent
```

The `multi-agent` extra currently contains the verified LangGraph dependency.

## Instrumentation Coverage

Current instrumentation is explicit:

- `trace()` records the workflow boundary
- delegation spans record supervisor transfers
- retrieval and tool spans record specialist work
- the final-response span records completion
- framework identity is stored on the run

Automatic conversion of every framework-native event into AgenticLens spans
remains roadmap work.

## Official Sources

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangGraph supervisor](https://github.com/langchain-ai/langgraph-supervisor-py)
