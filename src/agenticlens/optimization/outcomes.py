"""Evaluate an adopted recommendation against traces recorded after adoption."""

import statistics
from collections.abc import Sequence
from typing import Literal

from agenticlens.experiments.stats import two_proportion_p_value
from agenticlens.models.trace import Run
from agenticlens.optimization.models import (
    MetricChange,
    ObservedOutcome,
    Opportunity,
    OptimizationReport,
    OutcomeEvaluation,
    OutcomeStatus,
)
from agenticlens.optimization.rules import DEFAULT_RULES, OptimizationRule
from agenticlens.optimization.tracking import RecommendationLedger, report_sha256
from agenticlens.optimization.tradeoffs import QualityCostTradeoffRule

# Kinds whose saving shows up in cost but not in recorded token counts.
_COST_KINDS = {"prompt_caching", "quality_cost_tradeoff"}
REALIZED_RATIO = 0.8


def _mean(values: list[float | None]) -> float | None:
    if not values or any(value is None for value in values):
        return None
    return statistics.fmean(value for value in values if value is not None)


def _change(before: float | None, after: float | None) -> MetricChange:
    delta = after - before if before is not None and after is not None else None
    return MetricChange(before=before, after=after, delta=delta)


def _rule_for(opportunity: Opportunity) -> OptimizationRule:
    if opportunity.rule_id == QualityCostTradeoffRule.rule_id:
        return QualityCostTradeoffRule(opportunity.subject.get("baseline_variant_id"))
    for rule in DEFAULT_RULES:
        if rule.rule_id == opportunity.rule_id:
            return rule
    raise ValueError(f"no rule {opportunity.rule_id!r} to re-check the opportunity")


def _success(runs: Sequence[Run]) -> tuple[int, int]:
    known = [run.task_success for run in runs if run.task_success is not None]
    return sum(known), len(known)


def evaluate_outcome(
    report: OptimizationReport,
    opportunity_id: str,
    before: Sequence[Run],
    after: Sequence[Run],
    *,
    ledger: RecommendationLedger | None = None,
    min_runs: int = 3,
) -> OutcomeEvaluation:
    """Measure what changed after adoption; the projection is copied, never adjusted.

    `before` should be the traces the report analysed (or a comparable window)
    and `after` traces of the same workload recorded after the change shipped.
    """
    opportunity = report.opportunity(opportunity_id)
    config = report.config
    reasons: list[str] = []
    decision = ledger.status(opportunity_id) if ledger is not None else None
    if decision is not None and decision != "adopted":
        reasons.append(f"The ledger status is {decision!r}, not 'adopted'.")

    rechecked = _rule_for(opportunity).analyze(after, config) if after else []
    still_detected = any(o.opportunity_id == opportunity_id for o in rechecked)
    successes_before, known_before = _success(before)
    successes_after, known_after = _success(after)
    observed = ObservedOutcome(
        before_runs=len(before),
        after_runs=len(after),
        tokens_per_run=_change(
            _mean([float(r.total_tokens) for r in before]),
            _mean([float(r.total_tokens) for r in after]),
        ),
        cost_usd_per_run=_change(
            _mean([r.estimated_cost_usd for r in before]),
            _mean([r.estimated_cost_usd for r in after]),
        ),
        latency_ms_per_run=_change(
            _mean([r.total_latency_ms for r in before]),
            _mean([r.total_latency_ms for r in after]),
        ),
        success_rate=_change(
            successes_before / known_before if known_before else None,
            successes_after / known_after if known_after else None,
        ),
        success_p_value=two_proportion_p_value(
            successes_after, known_after, successes_before, known_before
        ),
        still_detected=still_detected,
    )

    basis: Literal["tokens", "cost_usd"] = (
        "cost_usd" if opportunity.kind in _COST_KINDS else "tokens"
    )
    projected = (
        opportunity.benefit.cost_usd_per_run
        if basis == "cost_usd"
        else opportunity.benefit.tokens_per_run
    )
    delta = (
        observed.cost_usd_per_run.delta if basis == "cost_usd" else observed.tokens_per_run.delta
    )
    ratio = -delta / projected if delta is not None and projected else None

    status: OutcomeStatus
    quality = observed.success_rate.delta
    if len(before) < min_runs or len(after) < min_runs:
        status = "insufficient_evidence"
        reasons.append(f"Need at least {min_runs} runs on each side.")
    elif quality is not None and quality < -config.tradeoff_max_success_rate_drop:
        status = "quality_regressed"
        reasons.append(
            f"Success rate moved {quality:+.0%}, beyond the allowed "
            f"{config.tradeoff_max_success_rate_drop:.0%} drop."
        )
    elif ratio is None:
        status = "not_realized" if still_detected else "insufficient_evidence"
        reasons.append(f"The observed {basis} saving could not be measured.")
    elif ratio >= REALIZED_RATIO and not still_detected:
        status = "realized"
    elif ratio > 0:
        status = "partially_realized"
    else:
        status = "not_realized"
    if still_detected:
        reasons.append("The rule still detects this opportunity after adoption.")
    if quality is None:
        reasons.append("Runs do not record task_success, so quality change is unknown.")

    return OutcomeEvaluation(
        opportunity_id=opportunity_id,
        report_sha256=report_sha256(report),
        decision_status=decision,
        projected=opportunity.benefit,
        observed=observed,
        realized_basis=basis if ratio is not None else None,
        realized_ratio=ratio,
        status=status,
        reasons=reasons,
    )
