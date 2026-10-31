"""Lens-local optimization artifacts; these are not a shared AIOS contract.

Projected benefit, quality risk, and observed outcome are separate models on
purpose: a projection never becomes a measurement, and a saving never offsets
a risk.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from agenticlens.modelfit.models import Confidence

OptimizationArea = Literal["prompt", "retrieval", "memory", "tool", "workflow", "model"]
RiskSeverity = Literal["low", "medium", "high"]
DecisionStatus = Literal["proposed", "accepted", "rejected", "adopted", "reverted"]
OutcomeStatus = Literal[
    "realized",
    "partially_realized",
    "not_realized",
    "quality_regressed",
    "insufficient_evidence",
]


class OptimizationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class OptimizationConfig(OptimizationModel):
    """Thresholds for every rule. Each finding records the thresholds it used."""

    # Prompt caching: a shared prefix repeated across model calls.
    prompt_cache_min_prefix_tokens: int = Field(default=512, ge=1)
    prompt_cache_min_repeats: int = Field(default=2, ge=2)
    prompt_cache_read_price_ratio: float = Field(
        default=0.1,
        ge=0,
        le=1,
        description="Cached-read price as a fraction of the uncached input price.",
    )
    # Prompt compression: large inputs that produce small outputs.
    prompt_compression_min_input_tokens: int = Field(default=4000, ge=1)
    prompt_compression_min_ratio: float = Field(default=20.0, gt=0)
    prompt_compression_target_reduction: float = Field(default=0.3, gt=0, lt=1)
    # Retrieval: retrieved chunks the answer never used.
    retrieval_min_chunks: int = Field(default=4, ge=1)
    retrieval_max_utility: float = Field(default=0.5, ge=0, le=1)
    retrieval_rerank_min_rank: int = Field(
        default=4,
        ge=2,
        description="A used chunk ranked at or below this position suggests reranking.",
    )
    # Memory: memory reads crowding out the rest of the prompt.
    memory_max_share: float = Field(default=0.4, gt=0, lt=1)
    memory_token_budget: int = Field(default=2000, ge=0)
    # Tools and retries.
    tool_cache_min_repeats: int = Field(default=2, ge=2)
    retry_min_unrecovered: int = Field(default=2, ge=1)
    # Workflow structure.
    redundant_step_min_repeats: int = Field(default=2, ge=2)
    handoff_min_occurrences: int = Field(default=1, ge=1)
    # Quality-cost trade-offs between experiment variants.
    tradeoff_min_runs: int = Field(default=3, ge=1)
    tradeoff_max_success_rate_drop: float = Field(default=0.05, ge=0, le=1)
    tradeoff_min_cost_reduction: float = Field(default=0.1, gt=0, lt=1)
    confidence_level: float = Field(default=0.95, gt=0, lt=1)
    # Confidence grading.
    high_confidence_min_runs: int = Field(default=3, ge=1)
    high_confidence_min_share: float = Field(default=0.5, gt=0, le=1)
    monthly_runs: int | None = Field(default=None, ge=1)


class OpportunityEvidence(OptimizationModel):
    """One measured observation backing an opportunity."""

    run_id: str
    span_ids: list[str] = Field(default_factory=list)
    measurements: dict[str, Any] = Field(default_factory=dict)
    reasoning: str


class ProjectedBenefit(OptimizationModel):
    """Expected per-run savings derived from measured spans and a stated basis.

    Cost is `None` whenever any affected span lacks a recorded cost; it is never
    estimated from list prices. Values are projections, not measurements.
    """

    tokens_per_run: float = Field(ge=0)
    cost_usd_per_run: float | None = Field(default=None, ge=0)
    latency_ms_per_run: float = Field(default=0.0, ge=0)
    monthly_cost_usd: float | None = Field(default=None, ge=0)
    cost_available: bool
    basis: str


class QualityRisk(OptimizationModel):
    kind: str
    severity: RiskSeverity
    description: str


class Opportunity(OptimizationModel):
    opportunity_id: str = Field(description="Stable hash of rule and subject.")
    rule_id: str
    rule_version: str
    area: OptimizationArea
    kind: str
    title: str
    summary: str
    action: str
    subject: dict[str, Any] = Field(default_factory=dict)
    thresholds: dict[str, Any] = Field(default_factory=dict)
    runs_observed: int = Field(ge=0)
    runs_affected: int = Field(ge=0)
    evidence: list[OpportunityEvidence]
    benefit: ProjectedBenefit
    confidence: Confidence
    confidence_reasons: list[str] = Field(default_factory=list)
    risks: list[QualityRisk] = Field(default_factory=list)


class VariantTradeoff(OptimizationModel):
    """Measured quality and cost of one experiment variant across its runs."""

    variant_id: str
    runs: int
    successes: int
    success_rate: float
    success_interval: tuple[float, float]
    mean_cost_usd: float | None = None
    cost_per_success_usd: float | None = None
    mean_latency_ms: float
    mean_tokens: float
    pareto_optimal: bool = False
    success_rate_delta: float | None = Field(
        default=None, description="Versus the baseline variant; negative is worse."
    )
    cost_delta_usd: float | None = Field(
        default=None, description="Versus the baseline variant; negative is cheaper."
    )
    p_value: float | None = None


class TradeoffAnalysis(OptimizationModel):
    baseline_variant_id: str | None = None
    variants: list[VariantTradeoff] = Field(default_factory=list)
    excluded: dict[str, str] = Field(
        default_factory=dict, description="Variant ID to the reason it was not compared."
    )


class RunSource(OptimizationModel):
    run_id: str
    variant_id: str | None = None
    spans: int
    tokens: int
    cost_usd: float | None = None
    task_success: bool | None = None


class OptimizationReport(OptimizationModel):
    """Reproducible: no wall-clock values, ordered deterministically."""

    schema_version: Literal["1.0"] = "1.0"
    runs: list[RunSource]
    total_tokens: int
    total_cost_usd: float | None = None
    config: OptimizationConfig
    opportunities: list[Opportunity] = Field(default_factory=list)
    tradeoffs: TradeoffAnalysis = Field(default_factory=TradeoffAnalysis)

    def opportunity(self, opportunity_id: str) -> Opportunity:
        for opportunity in self.opportunities:
            if opportunity.opportunity_id == opportunity_id:
                return opportunity
        raise KeyError(f"unknown opportunity {opportunity_id!r}")


class RecommendationDecision(OptimizationModel):
    """One ledger entry: a person or process deciding on an opportunity."""

    schema_version: Literal["1.0"] = "1.0"
    opportunity_id: str = Field(min_length=1)
    report_sha256: str = Field(min_length=64, max_length=64)
    status: DecisionStatus
    decided_by: str = Field(min_length=1)
    decided_at: datetime
    reason: str = ""
    change_reference: str | None = Field(
        default=None, description="PR, commit, or config version that adopted the change."
    )


class MetricChange(OptimizationModel):
    """Per-run means before and after adoption; `None` when not measurable."""

    before: float | None = None
    after: float | None = None
    delta: float | None = None


class ObservedOutcome(OptimizationModel):
    before_runs: int
    after_runs: int
    tokens_per_run: MetricChange
    cost_usd_per_run: MetricChange
    latency_ms_per_run: MetricChange
    success_rate: MetricChange
    success_p_value: float | None = None
    still_detected: bool = Field(
        description="The same rule still finds this opportunity in the after runs."
    )


class OutcomeEvaluation(OptimizationModel):
    """Projected and observed values side by side, never blended."""

    schema_version: Literal["1.0"] = "1.0"
    opportunity_id: str
    report_sha256: str
    decision_status: DecisionStatus | None = None
    projected: ProjectedBenefit
    observed: ObservedOutcome
    realized_basis: Literal["tokens", "cost_usd"] | None = Field(
        default=None, description="Which per-run metric the realized ratio compares."
    )
    realized_ratio: float | None = Field(
        default=None, description="Observed per-run saving divided by the projected saving."
    )
    status: OutcomeStatus
    reasons: list[str] = Field(default_factory=list)
