from pydantic import BaseModel, Field


class MetricSummary(BaseModel):
    count: int = Field(ge=0)
    mean: float
    median: float
    p95: float
    standard_deviation: float
    coefficient_of_variation: float | None = None


class RunGroupSummary(BaseModel):
    label: str
    run_count: int
    success_rate: float
    tokens: MetricSummary
    latency_ms: MetricSummary
    cost_usd: MetricSummary | None = None
    cost_per_successful_task: float | None = None


class MetricDelta(BaseModel):
    absolute: float
    relative: float | None = None
    regressed: bool


class ComparisonReport(BaseModel):
    schema_version: str = "1.0"
    baseline: RunGroupSummary
    candidate: RunGroupSummary
    success_rate_delta: MetricDelta
    mean_tokens_delta: MetricDelta
    mean_latency_ms_delta: MetricDelta
    mean_cost_usd_delta: MetricDelta | None = None
    regression_threshold: float
    regressions: list[str] = Field(default_factory=list)
