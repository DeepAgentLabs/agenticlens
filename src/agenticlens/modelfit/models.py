"""Data models for ModelFit: task-level model recommendations.

A `ModelFitConfig` names the task categories to recommend for, the hard
constraints each recommendation must satisfy, and how feasible candidates are
scored. Candidates are the variants of one or more recorded experiment
reports (`agenticlens experiment run --save`), so every number in a
`ModelFitReport` is computed from repeated-trial experiment evidence rather
than from list prices or benchmarks.
"""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from agenticlens.evaluation import ConfidenceInterval

MODELFIT_SCHEMA_VERSION = "1.0"

#: Category ID used for the optional category that covers every case.
OVERALL_CATEGORY_ID = "all"

Confidence = Literal["high", "medium", "low"]
RecommendationStatus = Literal["recommended", "no_feasible_model", "no_evidence"]
RiskKind = Literal[
    "quality_regression",
    "regressed_cases",
    "flaky_cases",
    "safety_failures",
    "low_evidence",
    "cost_unavailable",
    "failed_trials",
    "no_fallback",
]
RiskSeverity = Literal["high", "medium", "low"]


class ModelConstraints(BaseModel):
    """Hard constraints a candidate must satisfy to be recommended.

    Every limit is optional. A limit that cannot be checked because the
    evidence is missing (for example an unpriced trial under a cost limit, or
    an unknown provider under a provider allow-list) is a violation: ModelFit
    never assumes a candidate passes a constraint it has no evidence for.
    """

    min_pass_rate: float | None = Field(default=None, ge=0, le=1)
    min_pass_rate_lower_bound: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Minimum lower bound of the pass rate's Wilson confidence interval.",
    )
    max_cost_per_case_usd: float | None = Field(default=None, ge=0)
    max_cost_per_success_usd: float | None = Field(default=None, ge=0)
    max_mean_latency_ms: float | None = Field(default=None, gt=0)
    max_p95_latency_ms: float | None = Field(default=None, gt=0)
    min_consistency: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Minimum share of cases with the same outcome on every attempt.",
    )
    min_safety_pass_rate: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Minimum pass rate over every safety-tagged case in the suite.",
    )
    allowed_providers: list[str] | None = None
    blocked_providers: list[str] = Field(default_factory=list)
    allowed_deployments: list[str] | None = None
    required_capabilities: list[str] = Field(default_factory=list)

    def merged(self, override: "ModelConstraints | None") -> "ModelConstraints":
        """Return these constraints with every field `override` sets replaced."""
        if override is None:
            return self.model_copy()
        updates = {name: getattr(override, name) for name in override.model_fields_set}
        return self.model_copy(update=updates)


class ScoringWeights(BaseModel):
    """Relative weights of the four normalised components of a candidate's score.

    Components are each in [0, 1]: `quality` is the pass rate; `cost` and
    `latency` are the cheapest (fastest) feasible candidate's cost per success
    (mean latency) divided by this candidate's; `reliability` is the share of
    cases with a consistent outcome across attempts.
    """

    quality: float = Field(default=0.5, ge=0)
    cost: float = Field(default=0.3, ge=0)
    latency: float = Field(default=0.1, ge=0)
    reliability: float = Field(default=0.1, ge=0)

    @model_validator(mode="after")
    def check_total(self) -> "ScoringWeights":
        if self.quality + self.cost + self.latency + self.reliability <= 0:
            raise ValueError("at least one scoring weight must be positive")
        return self

    def as_dict(self) -> dict[str, float]:
        return {
            "quality": self.quality,
            "cost": self.cost,
            "latency": self.latency,
            "reliability": self.reliability,
        }


class TaskCategory(BaseModel):
    """A task category and the suite cases that belong to it.

    A case belongs to the category when its ID is listed in `case_ids`, it
    carries any of `tags`, or its `metadata["domain"]` is in `domains`. A
    case can belong to several categories.
    """

    id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
    name: str = ""
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    case_ids: list[str] = Field(default_factory=list)
    constraints: ModelConstraints | None = Field(
        default=None, description="Overrides for the config's default constraints."
    )
    weights: ScoringWeights | None = Field(
        default=None, description="Replaces the config's default weights for this category."
    )
    monthly_volume: int | None = Field(
        default=None, ge=0, description="Expected requests per month, for savings projections."
    )

    @model_validator(mode="after")
    def check_selector(self) -> "TaskCategory":
        if self.id != OVERALL_CATEGORY_ID and not (self.tags or self.domains or self.case_ids):
            raise ValueError(
                f"task category {self.id!r} needs at least one of tags, domains, or case_ids"
            )
        return self

    @property
    def display_name(self) -> str:
        return self.name or self.id


class ModelCandidate(BaseModel):
    """Deployment facts about one experiment variant.

    Values here take precedence over the variant's `metadata` keys of the same
    name (`model`, `provider`, `deployment`, comma-separated `capabilities`).
    """

    variant_id: str = Field(min_length=1)
    model: str | None = None
    provider: str | None = None
    deployment: str | None = None
    capabilities: list[str] = Field(default_factory=list)


class ModelFitConfig(BaseModel):
    schema_version: str = MODELFIT_SCHEMA_VERSION
    name: str = Field(default="modelfit", min_length=1)
    model_factor: str = Field(
        default="model", min_length=1, description="Experiment factor that names the model."
    )
    reference_variant_id: str | None = Field(
        default=None,
        description="Variant that savings and quality risks are measured against; "
        "defaults to the experiment baseline.",
    )
    categories: list[TaskCategory] = Field(
        default_factory=list,
        description="Task taxonomy. When empty, one category is derived per case tag.",
    )
    include_overall: bool = Field(
        default=True, description="Add an `all` category covering every case."
    )
    defaults: ModelConstraints = Field(default_factory=ModelConstraints)
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    candidates: list[ModelCandidate] = Field(default_factory=list)
    exclude_variant_ids: list[str] = Field(default_factory=list)
    safety_tags: list[str] = Field(default_factory=lambda: ["safety"])
    minimum_attempts: int = Field(
        default=10,
        ge=1,
        description="Case attempts per category below which a recommendation is low confidence.",
    )
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    significance_level: float = Field(default=0.05, gt=0, lt=1)
    max_alternatives: int = Field(default=2, ge=0)
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_unique(self) -> "ModelFitConfig":
        category_ids = [category.id for category in self.categories]
        if len(category_ids) != len(set(category_ids)):
            raise ValueError("task category IDs must be unique")
        if self.include_overall and OVERALL_CATEGORY_ID in category_ids:
            raise ValueError(
                f"category ID {OVERALL_CATEGORY_ID!r} is reserved while include_overall is true"
            )
        variant_ids = [candidate.variant_id for candidate in self.candidates]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("candidate variant IDs must be unique")
        return self


class EvidenceSource(BaseModel):
    """One experiment report the recommendations were computed from."""

    experiment_name: str
    experiment_version: str
    suite_name: str
    suite_version: str
    baseline_variant_id: str
    trial_count: int = Field(ge=1)
    created_at: datetime
    variant_ids: list[str]
    file: str | None = Field(default=None, description="Report file name, without directories.")
    sha256: str | None = Field(
        default=None, description="SHA-256 of the report file bytes, when loaded from a file."
    )


class Violation(BaseModel):
    constraint: str
    limit: Any = None
    observed: Any = None
    message: str


class CandidateMetrics(BaseModel):
    """One candidate's measured evidence on one task category."""

    variant_id: str
    variant_name: str
    model: str
    provider: str | None = None
    deployment: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    factors: dict[str, str] = Field(default_factory=dict)
    source_index: int = Field(ge=0, description="Index into the report's `sources`.")
    case_ids: list[str]
    attempts: int = Field(ge=0)
    passes: int = Field(ge=0)
    pass_rate: float | None = Field(default=None, ge=0, le=1)
    pass_rate_interval: ConfidenceInterval | None = None
    failed_trial_attempts: int = Field(
        default=0, ge=0, description="Attempts lost because the whole trial failed."
    )
    mean_latency_ms: float | None = None
    p95_latency_ms: float | None = None
    cost_complete: bool = Field(
        description="Every completed attempt reported a cost; otherwise costs are unavailable."
    )
    total_cost_usd: float | None = None
    cost_per_case_usd: float | None = None
    cost_per_success_usd: float | None = None
    consistency_rate: float | None = Field(default=None, ge=0, le=1)
    flaky_case_ids: list[str] = Field(default_factory=list)
    safety_attempts: int = Field(default=0, ge=0)
    safety_pass_rate: float | None = Field(default=None, ge=0, le=1)
    failed_safety_case_ids: list[str] = Field(default_factory=list)
    feasible: bool = False
    violations: list[Violation] = Field(default_factory=list)
    component_scores: dict[str, float] = Field(default_factory=dict)
    weighted_score: float | None = Field(
        default=None, description="Only feasible candidates are scored."
    )
    rank: int | None = Field(default=None, ge=1, description="Rank among feasible candidates.")
    pareto_optimal: bool = False
    cost_per_success_rank: int | None = Field(default=None, ge=1)


class Alternative(BaseModel):
    variant_id: str
    model: str
    provider: str | None = None
    role: Literal["alternative", "fallback"]
    weighted_score: float | None = None
    pass_rate: float | None = None
    cost_per_success_usd: float | None = None
    reason: str


class SavingsEstimate(BaseModel):
    """Cost of the recommendation relative to the reference, from the same evidence.

    Positive `cost_per_case_savings_usd` means the recommendation is cheaper.
    Savings are only stated when both candidates' costs are complete.
    """

    reference_variant_id: str
    recommended_variant_id: str
    available: bool
    reason: str = ""
    reference_cost_per_case_usd: float | None = None
    recommended_cost_per_case_usd: float | None = None
    cost_per_case_savings_usd: float | None = None
    cost_per_case_savings_ratio: float | None = None
    reference_cost_per_success_usd: float | None = None
    recommended_cost_per_success_usd: float | None = None
    cost_per_success_savings_usd: float | None = None
    monthly_volume: int | None = None
    projected_monthly_savings_usd: float | None = None
    reference_pass_rate: float | None = None
    recommended_pass_rate: float | None = None
    pass_rate_delta: float | None = None
    pass_rate_p_value: float | None = None
    reference_attempts: int = Field(default=0, ge=0)
    recommended_attempts: int = Field(default=0, ge=0)
    case_ids: list[str] = Field(default_factory=list)
    source_indexes: list[int] = Field(
        default_factory=list, description="Indexes into the report's `sources`."
    )


class QualityRisk(BaseModel):
    kind: RiskKind
    severity: RiskSeverity
    message: str
    case_ids: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    category_id: str
    status: RecommendationStatus
    variant_id: str | None = None
    model: str | None = None
    provider: str | None = None
    weighted_score: float | None = None
    confidence: Confidence | None = None
    confidence_reasons: list[str] = Field(default_factory=list)
    explanation: list[str] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list)
    fallback: Alternative | None = None
    savings: SavingsEstimate | None = None
    quality_risks: list[QualityRisk] = Field(default_factory=list)
    rejected_variant_ids: list[str] = Field(default_factory=list)


class CategoryResult(BaseModel):
    category: TaskCategory
    case_ids: list[str]
    constraints: ModelConstraints = Field(description="Effective constraints after overrides.")
    weights: ScoringWeights = Field(description="Effective scoring weights.")
    candidates: list[CandidateMetrics] = Field(
        description="Feasible candidates by rank, then infeasible ones."
    )
    pareto_frontier_variant_ids: list[str] = Field(default_factory=list)
    cost_per_success_ranking: list[str] = Field(
        default_factory=list, description="Candidates with known cost per success, cheapest first."
    )
    recommendation: Recommendation


class MatrixRow(BaseModel):
    """One cell of the task-level model matrix: a category x candidate pair."""

    category_id: str
    variant_id: str
    model: str
    provider: str | None = None
    role: Literal["recommended", "alternative", "fallback", "feasible", "infeasible"]
    feasible: bool
    attempts: int
    pass_rate: float | None = None
    cost_per_success_usd: float | None = None
    mean_latency_ms: float | None = None
    weighted_score: float | None = None
    violations: list[str] = Field(default_factory=list)


class ModelFitSummary(BaseModel):
    categories: int = Field(ge=0)
    recommended: int = Field(ge=0)
    unfit_category_ids: list[str] = Field(
        default_factory=list, description="Categories with no feasible candidate or no evidence."
    )
    low_confidence_category_ids: list[str] = Field(default_factory=list)
    candidates: int = Field(ge=0)


class ModelFitReport(BaseModel):
    schema_version: str = MODELFIT_SCHEMA_VERSION
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_factor: str
    reference_variant_id: str
    safety_tags: list[str] = Field(default_factory=list)
    minimum_attempts: int = Field(ge=1)
    confidence_level: float = Field(gt=0, lt=1)
    sources: list[EvidenceSource]
    summary: ModelFitSummary
    categories: list[CategoryResult]
    matrix: list[MatrixRow] = Field(default_factory=list)
    uncategorized_case_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
