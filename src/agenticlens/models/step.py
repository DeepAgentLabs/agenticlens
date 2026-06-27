import uuid
from typing import Any

from pydantic import BaseModel, Field

from agenticlens.models.enums import StepType
from agenticlens.models.metrics import Metrics


class Step(BaseModel):
    """A single profiled step within a workflow (e.g. a Planner or LLM call)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: StepType
    provider: str | None = None
    model: str | None = None
    metrics: Metrics = Field(default_factory=Metrics)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Free-form signals supplied by the developer for recommender rules "
            "(e.g. 'prompt', 'chunk_count', 'history_tokens', 'tool_name', 'tool_args')."
        ),
    )
