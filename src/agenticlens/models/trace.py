import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


def _uuid() -> str:
    return str(uuid.uuid4())


class SpanType(str, Enum):
    MODEL_CALL = "model_call"
    PLANNING = "planning"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    RETRIEVAL = "retrieval"
    TOOL_CALL = "tool_call"
    VALIDATION = "validation"
    RETRY = "retry"
    DELEGATION = "delegation"
    FINAL_RESPONSE = "final_response"
    CUSTOM = "custom"


class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Span(BaseModel):
    span_id: str = Field(default_factory=_uuid)
    parent_span_id: str | None = None
    name: str
    span_type: SpanType
    agent_name: str | None = None
    model_name: str | None = None
    provider: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    latency_ms: float = Field(default=0.0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    tool_name: str | None = None
    retry_number: int | None = Field(default=None, ge=0)
    status: RunStatus = RunStatus.RUNNING
    error_type: str | None = None
    error_message: str | None = None
    input_reference: str | None = None
    output_reference: str | None = None
    input_data: Any | None = Field(
        default=None,
        description="Optional captured input after configured redaction.",
    )
    output_data: Any | None = Field(
        default=None,
        description="Optional captured output after configured redaction.",
    )
    attributes: dict[str, Any] = Field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class Run(BaseModel):
    schema_version: str = "1.0"
    run_id: str = Field(default_factory=_uuid)
    trace_id: str = Field(default_factory=_uuid)
    application_name: str
    framework: str | None = None
    framework_version: str | None = None
    task_id: str | None = None
    task_type: str | None = None
    experiment_id: str | None = None
    variant_id: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    status: RunStatus = RunStatus.RUNNING
    spans: list[Span] = Field(default_factory=list)
    task_success: bool | None = None
    error_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_span_tree(self) -> "Run":
        ids = [span.span_id for span in self.spans]
        if len(ids) != len(set(ids)):
            raise ValueError("span_id values must be unique within a run")
        known = set(ids)
        for span in self.spans:
            if span.parent_span_id is not None and span.parent_span_id not in known:
                raise ValueError(
                    f"span {span.span_id} references unknown parent {span.parent_span_id}"
                )
            if span.parent_span_id == span.span_id:
                raise ValueError(f"span {span.span_id} cannot be its own parent")
        return self

    @property
    def total_input_tokens(self) -> int:
        return sum(span.input_tokens for span in self.spans)

    @property
    def total_output_tokens(self) -> int:
        return sum(span.output_tokens for span in self.spans)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_latency_ms(self) -> float:
        if self.completed_at is None:
            return 0.0
        return max(0.0, (self.completed_at - self.started_at).total_seconds() * 1000)

    @property
    def estimated_cost_usd(self) -> float | None:
        costs = [
            span.estimated_cost_usd for span in self.spans if span.estimated_cost_usd is not None
        ]
        return sum(costs) if costs else None


class MetricValue(BaseModel):
    name: str
    value: float
    unit: str
    estimated: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    finding_id: str = Field(default_factory=_uuid)
    category: str
    title: str
    description: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    span_ids: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
