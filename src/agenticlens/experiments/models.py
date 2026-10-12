from datetime import datetime, timezone

from pydantic import BaseModel, Field, model_validator

from agenticlens.comparison.models import MetricDelta
from agenticlens.evaluation import ConfidenceInterval, EvaluationReport

#: Factor names with a documented meaning. Other names are allowed; these are
#: the dimensions the roadmap calls out for comparison.
KNOWN_FACTORS = ("model", "prompt", "retrieval", "memory", "retry_policy")


class ExperimentVariant(BaseModel):
    """One configuration under test.

    `target_kind` is `python` (a trusted `module:function` or `path.py:function`),
    `http` (a URL), or `recorded` (a JSON/YAML file of saved per-trial samples,
    replayed without calling any agent). `factors` names what this variant
    sets for each compared dimension, such as `{"model": "gpt-4o-mini",
    "prompt": "v2"}`.
    """

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    target_kind: str = Field(pattern="^(python|http|recorded)$")
    target: str = Field(min_length=1)
    timeout_seconds: float = Field(default=30.0, gt=0)
    description: str = ""
    factors: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


class ExperimentManifest(BaseModel):
    schema_version: str = "1.1"
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    baseline_variant_id: str = Field(min_length=1)
    trial_count: int = Field(default=5, ge=1)
    random_seed: int | None = None
    pass_k: list[int] = Field(
        default_factory=list,
        description="k values for pass@k and pass^k; defaults to 1 and trial_count.",
    )
    minimum_trials: int = Field(
        default=5,
        ge=1,
        description="Completed trials per variant below which deltas are flagged exploratory.",
    )
    max_workers: int = Field(
        default=1, ge=1, description="Cases run concurrently within one live trial."
    )
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
        if any(not 1 <= k <= self.trial_count for k in self.pass_k):
            raise ValueError("pass_k values must be between 1 and trial_count")
        return self

    def resolved_pass_k(self) -> list[int]:
        return sorted(set(self.pass_k or [1, self.trial_count]))


class ExperimentMetricSummary(BaseModel):
    count: int = Field(ge=0)
    mean: float
    median: float
    p95: float
    standard_deviation: float
    coefficient_of_variation: float | None = None
    confidence_interval: ConfidenceInterval | None = None


class ExperimentCaseResult(BaseModel):
    """One variant's results on one test case across all trials.

    A trial whose target call failed counts as a failed attempt on every
    case: the agent did not deliver an output.
    """

    case_id: str
    case_name: str
    attempts: int = Field(ge=0)
    passes: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=1)
    pass_at_k: dict[str, float] = Field(default_factory=dict)
    pass_hat_k: dict[str, float] = Field(default_factory=dict)
    mean_score: float | None = None
    score_standard_deviation: float | None = None
    consistent: bool = Field(description="Every attempt had the same pass/fail outcome.")


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
    case_attempts: int = Field(default=0, ge=0)
    case_passes: int = Field(default=0, ge=0)
    case_pass_rate: float | None = Field(default=None, ge=0, le=1)
    case_pass_rate_interval: ConfidenceInterval | None = None
    pass_at_k: dict[str, float] = Field(default_factory=dict)
    pass_hat_k: dict[str, float] = Field(default_factory=dict)
    consistency_rate: float | None = Field(default=None, ge=0, le=1)
    flaky_case_ids: list[str] = Field(default_factory=list)
    priced_trials: int = Field(default=0, ge=0)


class ExperimentTrialResult(BaseModel):
    trial_index: int = Field(ge=1)
    status: str = Field(pattern="^(succeeded|failed)$")
    report: EvaluationReport | None = None
    error_message: str | None = None


class ExperimentVariantResult(BaseModel):
    variant_id: str
    variant_name: str
    target_kind: str
    factors: dict[str, str] = Field(default_factory=dict)
    pareto_optimal: bool = False
    trials: list[ExperimentTrialResult]
    summary: ExperimentVariantSummary
    cases: list[ExperimentCaseResult] = Field(default_factory=list)


class ExperimentComparison(BaseModel):
    baseline_variant_id: str
    candidate_variant_id: str
    pass_rate_delta: MetricDelta
    average_score_delta: MetricDelta
    average_latency_ms_delta: MetricDelta
    total_cost_usd_delta: MetricDelta | None = None
    changed_factors: dict[str, list[str | None]] = Field(
        default_factory=dict,
        description="Factor -> [baseline value, candidate value] for factors that differ.",
    )
    case_pass_rate_delta: float | None = None
    case_pass_rate_p_value: float | None = None
    statistically_significant: bool | None = None
    regressed_case_ids: list[str] = Field(default_factory=list)
    improved_case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FactorLevelSummary(BaseModel):
    """Variants that share one value of one factor, averaged together."""

    factor: str
    value: str
    variant_ids: list[str]
    mean_pass_rate: float | None = None
    mean_average_score: float | None = None
    mean_latency_ms: float | None = None
    mean_cost_usd: float | None = None
    mean_trial_success_rate: float


class ExperimentRandomization(BaseModel):
    random_seed: int | None = None
    shuffled: bool
    execution_order: list[tuple[str, int]] = Field(
        default_factory=list, description="(variant_id, trial_index) in the order run."
    )


class ExperimentReport(BaseModel):
    schema_version: str = "1.1"
    experiment_name: str
    experiment_version: str
    suite_name: str
    suite_version: str
    baseline_variant_id: str
    trial_count: int = Field(ge=1)
    random_seed: int | None = None
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    regression_threshold: float = Field(default=0.05, ge=0)
    pass_k: list[int] = Field(default_factory=list)
    minimum_trials: int = Field(default=5, ge=1)
    randomization: ExperimentRandomization | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    variants: list[ExperimentVariantResult]
    comparisons: list[ExperimentComparison]
    pareto_frontier_variant_ids: list[str] = Field(default_factory=list)
    factor_levels: list[FactorLevelSummary] = Field(default_factory=list)
    case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
