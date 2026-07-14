# LangChain Integration

AgenticLens can auto-instrument a LangChain (or LangGraph) run through its
callback system, instead of requiring a manual `with step(...)` block around
every LLM call, tool call, and retrieval.

## Installation

```bash
pip install "agenticlens[langchain]"
```

## Usage

```python
from agenticlens import profile
from agenticlens.adapters.langchain import AgenticLensCallbackHandler

handler = AgenticLensCallbackHandler()

with profile("My LangChain App") as workflow:
    chain.invoke(inputs, config={"callbacks": [handler]})

print(workflow.total_tokens)
print(workflow.total_cost)
```

The handler must be used inside a `with profile(...):` block -- it attaches
each step to whichever workflow is active in the current context.

## What gets tracked

| LangChain event | AgenticLens step type | Metadata captured |
| --- | --- | --- |
| `on_llm_start` / `on_chat_model_start` → `on_llm_end` | `llm_call` | `prompt`, token usage, `model` (when reported) |
| `on_tool_start` → `on_tool_end` | `tool_call` | `tool_name`, `tool_args` |
| `on_retriever_start` → `on_retriever_end` | `retriever` | `query`, `chunk_count`, `avg_tokens_per_chunk` |

Token usage is extracted in priority order:

1. Per-message `usage_metadata` (populated by most current LangChain chat
   model integrations)
2. `llm_output["token_usage"]` / `llm_output["usage"]` (older, provider-specific
   integrations)
3. If neither is present, token fields stay `0` for that step -- the step
   itself, its latency, and its metadata are still recorded.

`avg_tokens_per_chunk` for retriever steps is estimated from
`len(document.page_content) / 4` -- LangChain retrievers return text, not a
token count, and this is only an approximation used to feed the
excessive-chunks recommender's savings estimate.

Because the adapter produces the same `Step` shape as the manual `step()` API,
every recommender, exporter, and the CLI work against LangChain-sourced
workflows without any changes.

## What doesn't get tracked

Chain-level (`on_chain_*`) events are intentionally ignored. LCEL chains fire
one such event per internal runnable, which would flood the workflow with
steps that don't correspond to a real LLM/tool/retrieval cost.
