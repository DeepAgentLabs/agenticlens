import time
from types import TracebackType
from typing import Any, Literal

from agenticlens.models.enums import StepType
from agenticlens.models.step import Step
from agenticlens.profiler.context import get_active_workflow
from agenticlens.providers.registry import detect_provider


class StepHandle:
    """Handle yielded by `step()`. Call `.record(response)` to attach token usage."""

    def __init__(self, step: Step) -> None:
        self.step = step

    def record(self, response: Any, ttft: float | None = None) -> None:
        """Extract token usage from a provider response and attach it to this step.

        `ttft` is only meaningful for streaming calls; pass it explicitly when the
        caller measured time-to-first-token itself (AgenticLens cannot infer streaming
        generically across provider SDKs).
        """
        provider = detect_provider(response)
        if provider is None:
            return
        usage = provider.extract_usage(response)
        self.step.metrics.prompt_tokens = usage.prompt_tokens
        self.step.metrics.completion_tokens = usage.completion_tokens
        self.step.metrics.total_tokens = usage.prompt_tokens + usage.completion_tokens
        if ttft is not None:
            self.step.metrics.ttft = ttft


class step:  # noqa: N801 -- lowercase to read as a context manager, like contextlib.suppress
    """Context manager that profiles a single step within the active workflow."""

    def __init__(
        self,
        name: str,
        type: StepType | str,
        provider: str | None = None,
        model: str | None = None,
        agent_name: str | None = None,
        agent_role: str | None = None,
        parent_step_id: str | None = None,
        handoff_from: str | None = None,
        handoff_to: str | None = None,
        **metadata: Any,
    ) -> None:
        self.name = name
        self.type = StepType(type)
        self.provider = provider
        self.model = model
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.parent_step_id = parent_step_id
        self.handoff_from = handoff_from
        self.handoff_to = handoff_to
        self.metadata = metadata
        self._handle: StepHandle | None = None
        self._start: float = 0.0

    def __enter__(self) -> StepHandle:
        workflow = get_active_workflow()
        step_model = Step(
            name=self.name,
            type=self.type,
            agent_name=self.agent_name,
            agent_role=self.agent_role,
            parent_step_id=self.parent_step_id,
            handoff_from=self.handoff_from,
            handoff_to=self.handoff_to,
            provider=self.provider,
            model=self.model,
            metadata=self.metadata,
        )
        self._handle = StepHandle(step_model)
        workflow.steps.append(step_model)
        self._start = time.perf_counter()
        return self._handle

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        assert self._handle is not None
        self._handle.step.metrics.latency = time.perf_counter() - self._start
        return False
