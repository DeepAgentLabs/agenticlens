from contextvars import Token
from datetime import datetime, timezone
from types import TracebackType
from typing import Literal

from tokenlens.models.workflow import Workflow
from tokenlens.profiler.context import current_workflow


class profile:  # noqa: N801 -- lowercase to read as a context manager, like contextlib.suppress
    """Context manager that establishes the active workflow for `step()` calls.

    Nested `profile()` blocks are not supported -- a workflow is a single
    top-level unit of work.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.workflow: Workflow | None = None
        self._token: Token[Workflow | None] | None = None

    def __enter__(self) -> Workflow:
        if current_workflow.get() is not None:
            raise RuntimeError("Nested profile() blocks are not supported.")
        self.workflow = Workflow(name=self.name, start_time=datetime.now(timezone.utc))
        self._token = current_workflow.set(self.workflow)
        return self.workflow

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        assert self.workflow is not None
        assert self._token is not None
        self.workflow.end_time = datetime.now(timezone.utc)
        current_workflow.reset(self._token)
        return False
