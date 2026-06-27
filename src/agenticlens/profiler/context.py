from contextvars import ContextVar

from agenticlens.models.workflow import Workflow

current_workflow: ContextVar[Workflow | None] = ContextVar("current_workflow", default=None)

completed_workflows: list[Workflow] = []
"""Workflows that have finished a `profile()` block, in completion order.

Lets callers that don't hold a reference to the `Workflow` (e.g. the CLI running a
target script via `runpy`) retrieve what was profiled. Intended for short-lived
processes -- nothing here is ever evicted.
"""


def get_active_workflow() -> Workflow:
    """Return the workflow active in the current context, or raise if none."""
    workflow = current_workflow.get()
    if workflow is None:
        raise RuntimeError(
            "No active workflow. `step()` must be used inside a `with profile(...):` block."
        )
    return workflow
