from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

from agenticlens.comparison.models import MetricDelta
from agenticlens.evaluation import ConfidenceInterval, EvaluationReport


class ExperimentVariant(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    target_kind: str = Field(pattern="^(python|http)$")
    target: str = Field(min_length=1)
    timeout_seconds: float = Field(default=30.0, gt=0)
    description: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)


class ExperimentManifest(BaseModel):
    schema_version: str = "1.0"
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    baseline_variant_id: str = Field(min_length=1)
    trial_count: int = Field(default=5, ge=1)
    random_seed: int | None = None
    variants: list[ExperimentVariant]
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_variants(self) -> "ExperimentManifest":
        variant_ids = [variant.id for variant in self.variants]
        if len(self.variants) < 3:
            raise ValueError("experiment manifests require at least three variants")
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("experiment variant IDs must be unique")
        if self.baseline_variant_id not in set(variant_ids):
            raise ValueError("baseline_variant_id must reference a defined variant")
        return self


class ExperimentMetricSummary(BaseModel):
    count: int = Field(ge=0)
    mean: float
    median: float
    p95: float
    standard_deviation: float
    coefficient_of_variation: float | None = None
    confidence_interval: ConfidenceInterval | None = None


class ExperimentVariantSummary(BaseModel):
    attempted_trials: int = Field(ge=0)
    completed_trials: int = Field(ge=0)
    failed_trials: int = Field(ge=0)
    successful_trials: int = Field(ge=0)
    trial_success_rate: float = Field(ge=0, le=1)
    pass_rate: ExperimentMetricSummary | None = None
    average_score: ExperimentMetricSummary | None = None
    average_latency_ms: ExperimentMetricSummary | None = None
    total_cost_usd: ExperimentMetricSummary | None = None


class ExperimentTrialResult(BaseModel):
    trial_index: int = Field(ge=1)
    status: str = Field(pattern="^(succeeded|failed)$")
    report: EvaluationReport | None = None
    error_message: str | None = None


class ExperimentVariantResult(BaseModel):
    variant_id: str
    variant_name: str
    target_kind: str
    pareto_optimal: bool = False
    trials: list[ExperimentTrialResult]
    summary: ExperimentVariantSummary


class ExperimentComparison(BaseModel):
    baseline_variant_id: str
    candidate_variant_id: str
    pass_rate_delta: MetricDelta
    average_score_delta: MetricDelta
    average_latency_ms_delta: MetricDelta
    total_cost_usd_delta: MetricDelta | None = None


class ExperimentReport(BaseModel):
    schema_version: str = "1.0"
    experiment_name: str
    experiment_version: str
    suite_name: str
    suite_version: str
    baseline_variant_id: str
    trial_count: int = Field(ge=1)
    random_seed: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    variants: list[ExperimentVariantResult]
    comparisons: list[ExperimentComparison]
    pareto_frontier_variant_ids: list[str] = Field(default_factory=list)
