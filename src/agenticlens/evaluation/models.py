from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator

from agenticlens.models.trace import Run


class EvaluatorConfig(BaseModel):
    name: str = Field(min_length=1)
    threshold: float = Field(default=1.0, ge=0, le=1)
    required: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    id: str
    name: str
    input: Any = None
    expected_output: str | None = None
    expected_contains: list[str] = Field(default_factory=list)
    output_json_schema: dict[str, Any] | None = None
    required_output_fields: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    required_tool_arguments: dict[str, list[str]] = Field(default_factory=dict)
    max_latency_ms: float | None = Field(default=None, gt=0)
    max_cost_usd: float | None = Field(default=None, ge=0)
    max_turns: int | None = Field(default=None, gt=0)
    evaluators: list[EvaluatorConfig] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_expectation(self) -> "TestCase":
        if not any(
            (
                self.expected_output is not None,
                self.expected_contains,
                self.output_json_schema is not None,
                self.required_output_fields,
                self.required_tools,
                self.forbidden_tools,
                self.required_tool_arguments,
                self.max_latency_ms is not None,
                self.max_cost_usd is not None,
                self.max_turns is not None,
                self.evaluators,
            )
        ):
            raise ValueError("test case must define at least one expectation")
        return self


class TestSuite(BaseModel):
    name: str
    version: str
    description: str = ""
    cases: list[TestCase]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_case_ids(self) -> "TestSuite":
        ids = [case.id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("test case IDs must be unique")
        if not ids:
            raise ValueError("test suite must contain at least one case")
        return self


class EvaluationSample(BaseModel):
    case_id: str
    output: str
    trace: Run


class Score(BaseModel):
    name: str
    value: float = Field(ge=0, le=1)
    passed: bool
    required: bool = True
    explanation: str
    evaluator_type: str = "deterministic"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaseEvaluation(BaseModel):
    case_id: str
    case_name: str
    passed: bool
    scores: list[Score]
    output: str
    trace_id: str
    latency_ms: float
    cost_usd: float | None = None


class EvaluationSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float = Field(ge=0, le=1)
    average_score: float = Field(ge=0, le=1)
    total_cost_usd: float | None = None
    average_latency_ms: float


class EvaluationReport(BaseModel):
    schema_version: str = "1.0"
    suite_name: str
    suite_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: EvaluationSummary
    cases: list[CaseEvaluation]


class LiveTarget(BaseModel):
    kind: str = Field(pattern="^(python|http)$")
    timeout_seconds: float = Field(default=30.0, gt=0)


class PythonTarget(LiveTarget):
    kind: str = "python"
    callable_path: str


class HTTPTarget(LiveTarget):
    kind: str = "http"
    url: str
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
