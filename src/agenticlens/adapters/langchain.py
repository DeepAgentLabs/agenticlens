"""Auto-instrumentation adapter for LangChain / LangGraph via its callback system.

Requires the optional `langchain-core` dependency:

    pip install "agenticlens[langchain]"

Usage:

    from agenticlens import profile
    from agenticlens.adapters.langchain import AgenticLensCallbackHandler

    with profile("My LangChain App"):
        chain.invoke(inputs, config={"callbacks": [AgenticLensCallbackHandler()]})

The handler creates one AgenticLens step per LLM call, tool call, and retriever
call, using the run lifecycle to time each one and, for LLM calls, extracting
token usage the way the rest of AgenticLens does from `s.record(...)`.
"""

from __future__ import annotations

import threading
import time
from typing import Any
from uuid import UUID

try:
    from langchain_core.callbacks.base import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
except ImportError as exc:  # pragma: no cover - exercised only without the extra installed
    raise ImportError(
        "agenticlens.adapters.langchain requires the 'langchain-core' package. "
        'Install it with: pip install "agenticlens[langchain]"'
    ) from exc

from agenticlens.models.enums import StepType
from agenticlens.models.step import Step
from agenticlens.profiler.context import get_active_workflow

CHARS_PER_TOKEN_ESTIMATE = 4
"""Rough chars-to-tokens heuristic used only for retrieved-chunk size estimates.

LangChain retrievers return `Document` text, not a token count, and the
excessive-chunks recommender needs `avg_tokens_per_chunk` to estimate savings.
This is intentionally approximate.
"""


def _extract_llm_usage(response: LLMResult) -> tuple[int, int] | None:
    """Best-effort prompt/completion token extraction from an `LLMResult`.

    Tries the modern per-message `usage_metadata` first (populated by most
    current LangChain chat model integrations), then falls back to the
    provider-specific `llm_output` dict used by older integrations.
    """
    for generations in response.generations:
        for generation in generations:
            message = getattr(generation, "message", None)
            usage = getattr(message, "usage_metadata", None) if message is not None else None
            if usage:
                return usage.get("input_tokens", 0), usage.get("output_tokens", 0)

    llm_output = response.llm_output or {}
    token_usage = llm_output.get("token_usage") or llm_output.get("usage")
    if token_usage:
        prompt = token_usage.get("prompt_tokens", token_usage.get("input_tokens"))
        completion = token_usage.get("completion_tokens", token_usage.get("output_tokens"))
        if prompt is not None and completion is not None:
            return int(prompt), int(completion)

    return None


class AgenticLensCallbackHandler(BaseCallbackHandler):  # type: ignore[misc]
    """Turns LangChain callback events into AgenticLens steps automatically.

    Must be used inside a `with profile(...):` block -- each tracked run is
    attached to whichever workflow is active in the current context when that
    run starts.

    Chain-level (`on_chain_*`) events are intentionally not tracked: LCEL
    chains fire one per internal runnable, which would flood the workflow
    with steps that don't correspond to a real LLM/tool/retrieval cost.
    """

    def __init__(self, provider: str | None = None) -> None:
        super().__init__()
        self._provider = provider
        self._lock = threading.Lock()
        self._runs: dict[UUID, tuple[Step, float]] = {}

    def _start(self, run_id: UUID, step_type: StepType, name: str, **metadata: Any) -> None:
        step_model = Step(
            name=name,
            type=step_type,
            provider=self._provider,
            metadata={k: v for k, v in metadata.items() if v is not None},
        )
        get_active_workflow().steps.append(step_model)
        with self._lock:
            self._runs[run_id] = (step_model, time.perf_counter())

    def _finish(self, run_id: UUID) -> Step | None:
        with self._lock:
            entry = self._runs.pop(run_id, None)
        if entry is None:
            return None
        step_model, start = entry
        step_model.metrics.latency = time.perf_counter() - start
        return step_model

    # LLM / chat model events

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        name = (serialized or {}).get("name") or "LLM Call"
        self._start(run_id, StepType.LLM_CALL, name, prompt=prompts[0] if prompts else None)

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        name = (serialized or {}).get("name") or "Chat Model Call"
        prompt = None
        if messages and messages[0]:
            prompt = "\n".join(str(getattr(m, "content", m)) for m in messages[0])
        self._start(run_id, StepType.LLM_CALL, name, prompt=prompt)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        step_model = self._finish(run_id)
        if step_model is None:
            return

        usage = _extract_llm_usage(response)
        if usage is not None:
            prompt_tokens, completion_tokens = usage
            step_model.metrics.prompt_tokens = prompt_tokens
            step_model.metrics.completion_tokens = completion_tokens
            step_model.metrics.total_tokens = prompt_tokens + completion_tokens

        if step_model.model is None and response.llm_output:
            step_model.model = response.llm_output.get("model_name")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self._finish(run_id)

    # Tool events

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        tool_name = (serialized or {}).get("name") or "Tool Call"
        tool_args = inputs if inputs is not None else {"input": input_str}
        self._start(run_id, StepType.TOOL_CALL, tool_name, tool_name=tool_name, tool_args=tool_args)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        self._finish(run_id)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        self._finish(run_id)

    # Retriever events

    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        name = (serialized or {}).get("name") or "Retriever"
        self._start(run_id, StepType.RETRIEVER, name, query=query)

    def on_retriever_end(
        self,
        documents: list[Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        step_model = self._finish(run_id)
        if step_model is None:
            return

        step_model.metadata["chunk_count"] = len(documents)
        if documents:
            avg_chars = sum(len(getattr(d, "page_content", "")) for d in documents) / len(documents)
            step_model.metadata["avg_tokens_per_chunk"] = round(
                avg_chars / CHARS_PER_TOKEN_ESTIMATE
            )

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        self._finish(run_id)
