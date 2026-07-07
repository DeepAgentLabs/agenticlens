import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from agenticlens.models.step import Step


class Workflow(BaseModel):
    """A complete profiled workflow, composed of one or more steps."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    start_time: datetime
    end_time: datetime | None = None
    steps: list[Step] = Field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return sum(step.metrics.total_tokens for step in self.steps)

    @property
    def total_cost(self) -> float | None:
        if not self.steps:
            return None
        costs = []
        for step in self.steps:
            if step.metrics.cost is None:
                return None
            costs.append(step.metrics.cost)
        return sum(costs)

    @property
    def latency(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
