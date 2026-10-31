"""Run every optimization rule over a set of traces."""

import math
from collections.abc import Sequence

from agenticlens.models.trace import Run
from agenticlens.optimization.models import (
    Opportunity,
    OptimizationConfig,
    OptimizationReport,
    RunSource,
)
from agenticlens.optimization.rules import DEFAULT_RULES, OptimizationRule, run_cost
from agenticlens.optimization.tradeoffs import QualityCostTradeoffRule, analyze_tradeoffs


def _sort_key(opportunity: Opportunity) -> tuple[float, float, str]:
    cost = opportunity.benefit.cost_usd_per_run
    priced = cost if cost is not None else -1.0
    return (-priced, -opportunity.benefit.tokens_per_run, opportunity.opportunity_id)


def analyze_optimizations(
    runs: Sequence[Run],
    config: OptimizationConfig | None = None,
    *,
    rules: Sequence[OptimizationRule] | None = None,
    baseline_variant_id: str | None = None,
) -> OptimizationReport:
    """Return opportunities ranked by projected cost, then token saving.

    Opportunities with unknown cost rank after every priced one. The report has
    no wall-clock values, so the same traces and config reproduce it exactly.
    """
    if not runs:
        raise ValueError("at least one trace is required")
    ids = [run.run_id for run in runs]
    if len(ids) != len(set(ids)):
        raise ValueError("run_id values must be unique across traces")
    config = config or OptimizationConfig()
    active = (
        list(rules)
        if rules is not None
        else [*DEFAULT_RULES, QualityCostTradeoffRule(baseline_variant_id)]
    )
    opportunities: list[Opportunity] = []
    for rule in active:
        opportunities.extend(rule.analyze(runs, config))
    found = [o.opportunity_id for o in opportunities]
    if len(found) != len(set(found)):
        raise ValueError("rules produced duplicate opportunity IDs")
    costs = [run_cost(run) for run in runs]
    return OptimizationReport(
        runs=[
            RunSource(
                run_id=run.run_id,
                variant_id=run.variant_id,
                spans=len(run.spans),
                tokens=run.total_tokens,
                cost_usd=run_cost(run),
                task_success=run.task_success,
            )
            for run in runs
        ],
        total_tokens=sum(run.total_tokens for run in runs),
        total_cost_usd=math.fsum(c for c in costs if c is not None) if None not in costs else None,
        config=config,
        opportunities=sorted(opportunities, key=_sort_key),
        tradeoffs=analyze_tradeoffs(runs, config, baseline_variant_id=baseline_variant_id),
    )
