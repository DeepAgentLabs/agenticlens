"""Quality-cost trade-offs come from measured variant runs, with risks kept apart."""

import pytest

from agenticlens.models.trace import SpanType
from agenticlens.optimization import (
    OptimizationConfig,
    QualityCostTradeoffRule,
    analyze_tradeoffs,
)
from optimization_support import run, span

CONFIG = OptimizationConfig(tradeoff_max_success_rate_drop=0.25)


def _variant(variant: str, cost: float, outcomes: list[bool]):
    return [
        run(
            f"{variant}-{i}",
            [span(f"{variant}-{i}", 1, SpanType.MODEL_CALL, cost=cost)],
            variant_id=variant,
            task_success=ok,
        )
        for i, ok in enumerate(outcomes)
    ]


def test_default_baseline_is_the_highest_success_variant():
    runs = _variant("big", 0.10, [True] * 4) + _variant("small", 0.02, [True] * 3 + [False])
    analysis = analyze_tradeoffs(runs, CONFIG)
    assert analysis.baseline_variant_id == "big"
    small = next(v for v in analysis.variants if v.variant_id == "small")
    assert small.success_rate_delta == pytest.approx(-0.25)
    assert small.cost_delta_usd == pytest.approx(-0.08)
    assert small.cost_per_success_usd == pytest.approx(0.08 / 3)
    assert small.p_value is not None
    assert all(v.pareto_optimal for v in analysis.variants)


def test_dominated_variant_is_not_pareto_optimal():
    runs = _variant("good", 0.01, [True] * 3) + _variant("bad", 0.05, [True, False, False])
    bad = next(v for v in analyze_tradeoffs(runs, CONFIG).variants if v.variant_id == "bad")
    assert bad.pareto_optimal is False


def test_variants_with_too_few_or_unlabelled_runs_are_excluded():
    runs = _variant("a", 0.01, [True] * 3) + _variant("b", 0.01, [True])
    runs += [run("c-0", [span("c-0", 1, SpanType.MODEL_CALL)], variant_id="c")]
    analysis = analyze_tradeoffs(runs, CONFIG)
    assert set(analysis.excluded) == {"b", "c"}
    with pytest.raises(ValueError, match="no comparable runs"):
        analyze_tradeoffs(runs, CONFIG, baseline_variant_id="b")


def test_rule_separates_saving_from_quality_risk():
    runs = _variant("big", 0.10, [True] * 4) + _variant("small", 0.02, [True] * 3 + [False])
    [found] = QualityCostTradeoffRule("big").analyze(runs, CONFIG)
    assert found.benefit.cost_usd_per_run == pytest.approx(0.08)
    assert found.risks[0].kind == "quality_regression"
    # Fewer than 30 runs per variant caps confidence.
    assert found.confidence == "medium"


def test_rule_respects_the_allowed_drop_and_minimum_reduction():
    worse = _variant("big", 0.10, [True] * 4) + _variant("small", 0.02, [False] * 4)
    assert QualityCostTradeoffRule("big").analyze(worse, CONFIG) == []
    similar = _variant("big", 0.10, [True] * 4) + _variant("small", 0.095, [True] * 4)
    assert QualityCostTradeoffRule("big").analyze(similar, CONFIG) == []


def test_unpriced_variants_produce_no_tradeoff_opportunity():
    runs = _variant("big", 0.10, [True] * 3)
    runs += [
        run(
            f"x-{i}",
            [span(f"x-{i}", 1, SpanType.MODEL_CALL, cost=None)],
            variant_id="x",
            task_success=True,
        )
        for i in range(3)
    ]
    assert QualityCostTradeoffRule("big").analyze(runs, CONFIG) == []
    x = next(v for v in analyze_tradeoffs(runs, CONFIG).variants if v.variant_id == "x")
    assert x.mean_cost_usd is None and x.pareto_optimal is False


def test_rule_finds_nothing_when_the_baseline_is_absent():
    runs = _variant("small", 0.02, [True] * 4)
    assert QualityCostTradeoffRule("big").analyze(runs, CONFIG) == []
