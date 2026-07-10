import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from agenticlens.models.step import Step


class Workflow(BaseModel):
    """A complete profiled workflow, composed of one or more steps."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime
    end_time: datetime | None = None
    steps: list[Step] = Field(default_factory=list)
    chaos_events: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Additive workflow.json extension (schema v1.1, see "
            "docs/workflow-schema-spec.md). Populated by fault-injection tools such as "
            "agentic-chaos; each entry is expected to carry at least 'fault_type', "
            "'outcome', and (when correlated to a step) 'step_id'/'step_name'. Left "
            "loosely typed here so AgenticLens has no hard dependency on the producer."
        ),
    )

    @property
    def total_tokens(self) -> int:
        return sum(step.metrics.total_tokens for step in self.steps)

    @property
    def total_cost(self) -> float | None:
        costs = [step.metrics.cost for step in self.steps if step.metrics.cost is not None]
        if not costs:
            return None
        return sum(costs)

    @property
    def latency(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
