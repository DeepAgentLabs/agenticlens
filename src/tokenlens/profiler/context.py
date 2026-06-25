from contextvars import ContextVar

from tokenlens.models.workflow import Workflow

current_workflow: ContextVar[Workflow | None] = ContextVar("current_workflow", default=None)


def get_active_workflow() -> Workflow:
    """Return the workflow active in the current context, or raise if none."""
    workflow = current_workflow.get()
    if workflow is None:
        raise RuntimeError(
            "No active workflow. `step()` must be used inside a `with profile(...):` block."
        )
    return workflow
