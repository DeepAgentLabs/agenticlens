"""Quality-cost trade-offs between experiment variants, from measured runs only."""

import math
import statistics
from collections import defaultdict
from collections.abc import Sequence

from agenticlens.experiments.stats import two_proportion_p_value, wilson_interval
from agenticlens.models.trace import Run
from agenticlens.optimization.models import (
    Opportunity,
    OpportunityEvidence,
    OptimizationConfig,
    QualityRisk,
    TradeoffAnalysis,
    VariantTradeoff,
)
from agenticlens.optimization.rules import Savings, build_opportunity, run_cost


def _variant(variant_id: str, runs: list[Run], config: OptimizationConfig) -> VariantTradeoff:
    successes = sum(bool(run.task_success) for run in runs)
    costs = [run_cost(run) for run in runs]
    known = [cost for cost in costs if cost is not None]
    mean_cost = statistics.fmean(known) if known and len(known) == len(costs) else None
    per_success = math.fsum(known) / successes if mean_cost is not None and successes else None
    return VariantTradeoff(
        variant_id=variant_id,
        runs=len(runs),
        successes=successes,
        success_rate=successes / len(runs),
        success_interval=wilson_interval(successes, len(runs), config.confidence_level),
        mean_cost_usd=mean_cost,
        cost_per_success_usd=per_success,
        mean_latency_ms=statistics.fmean(run.total_latency_ms for run in runs),
        mean_tokens=statistics.fmean(run.total_tokens for run in runs),
    )


def _dominated(item: VariantTradeoff, others: list[VariantTradeoff]) -> bool:
    assert item.mean_cost_usd is not None
    return any(
        other.mean_cost_usd is not None
        and other.success_rate >= item.success_rate
        and other.mean_cost_usd <= item.mean_cost_usd
        and (other.success_rate > item.success_rate or other.mean_cost_usd < item.mean_cost_usd)
        for other in others
    )


def analyze_tradeoffs(
    runs: Sequence[Run],
    config: OptimizationConfig,
    *,
    baseline_variant_id: str | None = None,
) -> TradeoffAnalysis:
    """Compare variants whose runs record `task_success`.

    Without an explicit baseline, the variant with the highest success rate is
    the baseline (ties broken by variant ID), so every comparison asks what is
    lost by moving away from the best measured quality.
    """
    grouped: dict[str, list[Run]] = defaultdict(list)
    excluded: dict[str, str] = {}
    for run in runs:
        if run.variant_id is None:
            continue
        if run.task_success is None:
            excluded[run.variant_id] = "a run does not record task_success"
            continue
        grouped[run.variant_id].append(run)
    variants: list[VariantTradeoff] = []
    for variant_id, items in sorted(grouped.items()):
        if variant_id in excluded:
            continue
        if len(items) < config.tradeoff_min_runs:
            excluded[variant_id] = f"{len(items)} runs, fewer than {config.tradeoff_min_runs}"
            continue
        variants.append(_variant(variant_id, items, config))
    if baseline_variant_id is not None and baseline_variant_id not in {
        v.variant_id for v in variants
    }:
        raise ValueError(f"baseline variant {baseline_variant_id!r} has no comparable runs")
    if not variants:
        return TradeoffAnalysis(excluded=dict(sorted(excluded.items())))
    baseline = (
        next(v for v in variants if v.variant_id == baseline_variant_id)
        if baseline_variant_id is not None
        else sorted(variants, key=lambda v: (-v.success_rate, v.variant_id))[0]
    )
    priced = [v for v in variants if v.mean_cost_usd is not None]
    for item in variants:
        item.pareto_optimal = item.mean_cost_usd is not None and not _dominated(item, priced)
        if item is baseline:
            continue
        item.success_rate_delta = item.success_rate - baseline.success_rate
        if item.mean_cost_usd is not None and baseline.mean_cost_usd is not None:
            item.cost_delta_usd = item.mean_cost_usd - baseline.mean_cost_usd
        item.p_value = two_proportion_p_value(
            item.successes, item.runs, baseline.successes, baseline.runs
        )
    return TradeoffAnalysis(
        baseline_variant_id=baseline.variant_id,
        variants=variants,
        excluded=dict(sorted(excluded.items())),
    )


class QualityCostTradeoffRule:
    """A cheaper variant whose measured quality stays within the allowed drop."""

    rule_id = "quality_cost_tradeoff"
    version = "1"

    def __init__(self, baseline_variant_id: str | None = None) -> None:
        self.baseline_variant_id = baseline_variant_id

    def analyze(self, runs: Sequence[Run], config: OptimizationConfig) -> list[Opportunity]:
        try:
            analysis = analyze_tradeoffs(runs, config, baseline_variant_id=self.baseline_variant_id)
        except ValueError:
            # The baseline is absent, e.g. when re-checking traces recorded after a
            # switch. analyze_optimizations still reports a bad explicit baseline.
            return []
        baseline = next(
            (v for v in analysis.variants if v.variant_id == analysis.baseline_variant_id), None
        )
        if baseline is None or not baseline.mean_cost_usd:
            return []
        by_variant: dict[str, list[Run]] = defaultdict(list)
        for run in runs:
            if run.variant_id is not None:
                by_variant[run.variant_id].append(run)

        found: list[Opportunity] = []
        for item in analysis.variants:
            if item is baseline or item.cost_delta_usd is None or item.success_rate_delta is None:
                continue
            reduction = -item.cost_delta_usd / baseline.mean_cost_usd
            if (
                reduction < config.tradeoff_min_cost_reduction
                or item.success_rate_delta < -config.tradeoff_max_success_rate_drop
            ):
                continue
            compared = by_variant[item.variant_id] + by_variant[baseline.variant_id]
            savings = Savings()
            savings.add(
                max(0.0, baseline.mean_tokens - item.mean_tokens) * len(compared),
                -item.cost_delta_usd * len(compared),
                max(0.0, baseline.mean_latency_ms - item.mean_latency_ms) * len(compared),
            )
            savings.evidence = [
                OpportunityEvidence(
                    run_id=run.run_id,
                    # Every span contributes to the run's measured cost and tokens.
                    span_ids=[span.span_id for span in run.spans],
                    measurements={
                        "variant_id": run.variant_id,
                        "task_success": run.task_success,
                        "cost_usd": run_cost(run),
                        "tokens": run.total_tokens,
                    },
                    reasoning="Measured run in the compared variants.",
                )
                for run in compared
            ]
            risks = [
                QualityRisk(
                    kind="sample_size",
                    severity="medium" if min(item.runs, baseline.runs) < 30 else "low",
                    description=(
                        f"{item.runs} and {baseline.runs} runs; small samples cannot rule out "
                        "a quality drop larger than the allowed threshold."
                    ),
                )
            ]
            if item.success_rate_delta < 0:
                significant = item.p_value is not None and item.p_value < 0.05
                risks.insert(
                    0,
                    QualityRisk(
                        kind="quality_regression",
                        severity="high" if significant else "medium",
                        description=(
                            f"Success rate {item.success_rate:.0%} vs {baseline.success_rate:.0%}"
                            f" (p={item.p_value:.3f})."
                            if item.p_value is not None
                            else f"Success rate {item.success_rate:.0%} vs "
                            f"{baseline.success_rate:.0%}."
                        ),
                    ),
                )
            found.append(
                build_opportunity(
                    self,
                    area="model",
                    kind="quality_cost_tradeoff",
                    title=f"Switch from '{baseline.variant_id}' to '{item.variant_id}'",
                    summary=(
                        f"'{item.variant_id}' cost {reduction:.0%} less per run with success "
                        f"{item.success_rate:.0%} vs {baseline.success_rate:.0%}."
                    ),
                    action=(
                        f"Trial '{item.variant_id}' behind advisory routing or a canary before "
                        "replacing the baseline."
                    ),
                    subject={
                        "baseline_variant_id": baseline.variant_id,
                        "variant_id": item.variant_id,
                    },
                    thresholds={
                        "tradeoff_min_runs": config.tradeoff_min_runs,
                        "tradeoff_min_cost_reduction": config.tradeoff_min_cost_reduction,
                        "tradeoff_max_success_rate_drop": config.tradeoff_max_success_rate_drop,
                    },
                    runs=compared,
                    savings=savings,
                    basis="Difference between the variants' measured mean per-run cost.",
                    config=config,
                    risks=risks,
                    confidence_cap="medium" if min(item.runs, baseline.runs) < 30 else None,
                    confidence_reasons=(
                        ["Fewer than 30 runs per variant."]
                        if min(item.runs, baseline.runs) < 30
                        else []
                    ),
                )
            )
        return found
