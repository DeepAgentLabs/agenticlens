import uuid

from pydantic import BaseModel, Field

from tokenlens.models.enums import StepType
from tokenlens.models.metrics import Metrics


class Step(BaseModel):
    """A single profiled step within a workflow (e.g. a Planner or LLM call)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: StepType
    provider: str | None = None
    model: str | None = None
    metrics: Metrics = Field(default_factory=Metrics)
