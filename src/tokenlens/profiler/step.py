import time
from types import TracebackType
from typing import Any, Literal

from tokenlens.models.enums import StepType
from tokenlens.models.step import Step
from tokenlens.profiler.context import get_active_workflow
from tokenlens.providers.registry import detect_provider


class StepHandle:
    """Handle yielded by `step()`. Call `.record(response)` to attach token usage."""

    def __init__(self, step: Step) -> None:
        self.step = step

    def record(self, response: Any) -> None:
        """Extract token usage from a provider response and attach it to this step."""
        provider = detect_provider(response)
        if provider is None:
            return
        usage = provider.extract_usage(response)
        self.step.metrics.prompt_tokens = usage.prompt_tokens
        self.step.metrics.completion_tokens = usage.completion_tokens
        self.step.metrics.total_tokens = usage.prompt_tokens + usage.completion_tokens


class step:  # noqa: N801 -- lowercase to read as a context manager, like contextlib.suppress
    """Context manager that profiles a single step within the active workflow."""

    def __init__(
        self,
        name: str,
        type: StepType | str,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        self.name = name
        self.type = StepType(type)
        self.provider = provider
        self.model = model
        self._handle: StepHandle | None = None
        self._start: float = 0.0

    def __enter__(self) -> StepHandle:
        workflow = get_active_workflow()
        step_model = Step(
            name=self.name,
            type=self.type,
            provider=self.provider,
            model=self.model,
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
