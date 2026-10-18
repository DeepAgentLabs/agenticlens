"""Category metrics, hard constraints, weighted scores, Pareto and cost-per-success ranking."""

from pathlib import Path

import pytest

from agenticlens.modelfit import (
    CandidateMetrics,
    ModelConstraints,
    ModelFitConfig,
    ScoringWeights,
    check_constraints,
    collect_candidates,
    cost_per_success_ranking,
    pareto_frontier,
)
from agenticlens.modelfit.evidence import ExperimentEvidence
from agenticlens.modelfit.scoring import measure, percentile, score
from modelfit_support import DEFAULT_CASES, Spec, build_report, fail_trial, passes, uniform


def _candidates(tmp_path: Path, report=None):
    report = report or build_report(
        tmp_path,
        {
            "a": Spec(
                {"p1": passes(4), "p2": passes(3, 1), "o1": passes(4), "s1": passes(2, 2)},
                cost=0.002,
                latency=500,
            ),
            "b": Spec(uniform(DEFAULT_CASES, passes(4)), cost=None, latency=900),
            "c": Spec(uniform(DEFAULT_CASES, passes(0, 4)), cost=0.001),
        },
    )
    candidates, _ = collect_candidates([ExperimentEvidence(report)], ModelFitConfig())
    return candidates


def test_percentile_interpolates_linearly() -> None:
    assert percentile([5.0], 0.95) == 5.0
    assert percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5) == 3.0
    assert percentile([0.0, 10.0], 0.95) == pytest.approx(9.5)


def test_measure_counts_passes_costs_consistency_and_safety(tmp_path: Path) -> None:
    a = _candidates(tmp_path)[0]
    metrics = measure(a, ["p1", "p2"], ["s1"], 0.95)

    assert (metrics.attempts, metrics.passes) == (8, 7)
    assert metrics.pass_rate == pytest.approx(7 / 8)
    assert metrics.pass_rate_interval is not None
    assert metrics.pass_rate_interval.method == "wilson"
    assert metrics.pass_rate_interval.lower < 7 / 8 < metrics.pass_rate_interval.upper
    assert metrics.cost_complete is True
    assert metrics.total_cost_usd == pytest.approx(0.016)
    assert metrics.cost_per_case_usd == pytest.approx(0.002)
    assert metrics.cost_per_success_usd == pytest.approx(0.016 / 7)
    assert metrics.mean_latency_ms == pytest.approx(501.5)
    assert metrics.consistency_rate == 0.5
    assert metrics.flaky_case_ids == ["p2"]
    assert (metrics.safety_attempts, metrics.safety_pass_rate) == (4, 0.5)
    assert metrics.failed_safety_case_ids == ["s1"]


def test_unpriced_attempts_make_costs_unavailable(tmp_path: Path) -> None:
    b = _candidates(tmp_path)[1]
    metrics = measure(b, list(DEFAULT_CASES), [], 0.95)

    assert metrics.cost_complete is False
    assert (
        metrics.total_cost_usd is metrics.cost_per_case_usd is metrics.cost_per_success_usd is None
    )


def test_no_passes_means_no_cost_per_success(tmp_path: Path) -> None:
    c = _candidates(tmp_path)[2]
    metrics = measure(c, list(DEFAULT_CASES), [], 0.95)
    assert metrics.cost_per_case_usd == pytest.approx(0.001)
    assert metrics.cost_per_success_usd is None


def test_failed_trials_are_lost_attempts_excluded_from_cost(tmp_path: Path) -> None:
    report = build_report(
        tmp_path,
        {
            "a": Spec(uniform(DEFAULT_CASES, passes(3)), cost=0.003),
            "b": Spec(uniform(DEFAULT_CASES, passes(3))),
            "c": Spec(uniform(DEFAULT_CASES, passes(3))),
        },
    )
    candidates = _candidates(tmp_path, fail_trial(report, "a", 1))
    metrics = measure(candidates[0], ["p1"], [], 0.95)

    assert (metrics.attempts, metrics.passes, metrics.failed_trial_attempts) == (3, 2, 1)
    assert metrics.cost_complete is True
    assert metrics.cost_per_case_usd == pytest.approx(0.003)


def _metrics(**values) -> CandidateMetrics:
    base = {
        "variant_id": "v",
        "variant_name": "v",
        "model": "m",
        "source_index": 0,
        "case_ids": ["c"],
        "attempts": 10,
        "passes": 9,
        "pass_rate": 0.9,
        "cost_complete": True,
        "cost_per_case_usd": 0.002,
        "cost_per_success_usd": 0.0022,
        "mean_latency_ms": 800.0,
        "p95_latency_ms": 1200.0,
        "consistency_rate": 0.8,
        "safety_attempts": 4,
        "safety_pass_rate": 1.0,
    }
    return CandidateMetrics(**{**base, **values})


def test_each_hard_constraint_is_enforced() -> None:
    constraints = ModelConstraints(
        min_pass_rate=0.95,
        max_cost_per_case_usd=0.001,
        max_cost_per_success_usd=0.002,
        max_mean_latency_ms=500,
        max_p95_latency_ms=1000,
        min_consistency=0.9,
        min_safety_pass_rate=1.0,
        allowed_providers=["p"],
        blocked_providers=["bad"],
        allowed_deployments=["on_prem"],
        required_capabilities=["pii_ok"],
    )
    violations = check_constraints(
        _metrics(provider="bad", deployment="cloud", safety_pass_rate=0.5), constraints
    )

    assert [v.constraint for v in violations] == [
        "min_pass_rate",
        "max_cost_per_case_usd",
        "max_cost_per_success_usd",
        "max_mean_latency_ms",
        "max_p95_latency_ms",
        "min_consistency",
        "min_safety_pass_rate",
        "allowed_providers",
        "blocked_providers",
        "allowed_deployments",
        "required_capabilities",
    ]
    assert violations[0].observed == 0.9 and violations[0].limit == 0.95
    assert "below the 95% minimum" in violations[0].message


def test_constraints_that_cannot_be_verified_are_violations() -> None:
    constraints = ModelConstraints(
        max_cost_per_case_usd=0.01,
        min_safety_pass_rate=1.0,
        allowed_providers=["p"],
        allowed_deployments=["cloud"],
        min_pass_rate_lower_bound=0.5,
    )
    violations = check_constraints(
        _metrics(cost_complete=False, cost_per_case_usd=None, safety_pass_rate=None), constraints
    )

    by_name = {v.constraint: v.message for v in violations}
    assert "cannot be verified" in by_name["max_cost_per_case_usd"]
    assert "cannot be verified" in by_name["min_safety_pass_rate"]
    assert "Provider is unknown" in by_name["allowed_providers"]
    assert "Deployment is unknown" in by_name["allowed_deployments"]
    assert "cannot be verified" in by_name["min_pass_rate_lower_bound"]


def test_satisfied_constraints_and_no_attempts() -> None:
    constraints = ModelConstraints(
        min_pass_rate=0.9, max_p95_latency_ms=1200, allowed_providers=["p"]
    )
    assert check_constraints(_metrics(provider="p"), constraints) == []
    empty = check_constraints(_metrics(attempts=0, passes=0, pass_rate=None), ModelConstraints())
    assert [v.constraint for v in empty] == ["evidence"]


def test_weighted_scores_normalise_cost_and_latency_to_the_best_feasible() -> None:
    cheap = _metrics(
        variant_id="cheap", feasible=True, cost_per_success_usd=0.001, mean_latency_ms=1000
    )
    fast = _metrics(
        variant_id="fast", feasible=True, cost_per_success_usd=0.004, mean_latency_ms=250
    )
    unpriced = _metrics(variant_id="unpriced", feasible=True, cost_per_success_usd=None)
    rejected = _metrics(variant_id="rejected", feasible=False, cost_per_success_usd=0.0001)
    score([cheap, fast, unpriced, rejected], ScoringWeights())

    assert cheap.component_scores == {
        "quality": 0.9,
        "cost": 1.0,
        "latency": 0.25,
        "reliability": 0.8,
    }
    assert fast.component_scores["cost"] == 0.25 and fast.component_scores["latency"] == 1.0
    assert unpriced.component_scores["cost"] == 0.0
    assert cheap.weighted_score == pytest.approx(0.5 * 0.9 + 0.3 * 1 + 0.1 * 0.25 + 0.1 * 0.8)
    assert rejected.weighted_score is None and rejected.component_scores == {}


def test_a_free_candidate_scores_full_cost_marks() -> None:
    free = _metrics(variant_id="free", feasible=True, cost_per_success_usd=0.0)
    paid = _metrics(variant_id="paid", feasible=True, cost_per_success_usd=0.001)
    score([free, paid], ScoringWeights())
    assert free.component_scores["cost"] == 1.0
    assert paid.component_scores["cost"] == 0.0


def test_pareto_frontier_and_cost_per_success_ranking() -> None:
    best = _metrics(
        variant_id="best", pass_rate=1.0, cost_per_success_usd=0.005, mean_latency_ms=900
    )
    cheap = _metrics(
        variant_id="cheap", pass_rate=0.8, cost_per_success_usd=0.001, mean_latency_ms=900
    )
    dominated = _metrics(
        variant_id="dominated", pass_rate=0.8, cost_per_success_usd=0.002, mean_latency_ms=950
    )
    unknown = _metrics(
        variant_id="unknown", pass_rate=0.7, cost_per_success_usd=None, mean_latency_ms=100
    )
    empty = _metrics(
        variant_id="empty", attempts=0, passes=0, pass_rate=None, cost_per_success_usd=None
    )
    candidates = [best, cheap, dominated, unknown, empty]

    assert pareto_frontier(candidates) == ["best", "cheap", "unknown"]
    assert cost_per_success_ranking(candidates) == ["cheap", "dominated", "best"]


def test_partial_latency_evidence_is_unavailable(tmp_path: Path) -> None:
    report = build_report(
        tmp_path,
        {
            "a": Spec(uniform(DEFAULT_CASES, passes(2))),
            "b": Spec(uniform(DEFAULT_CASES, passes(2))),
            "c": Spec(uniform(DEFAULT_CASES, passes(2))),
        },
    )
    variant = report.variants[0]
    trial = variant.trials[0]
    assert trial.report is not None
    cases = [
        case.model_copy(update={"latency_ms": None}) if case.case_id == "p1" else case
        for case in trial.report.cases
    ]
    trials = [
        trial.model_copy(update={"report": trial.report.model_copy(update={"cases": cases})}),
        *variant.trials[1:],
    ]
    variants = [variant.model_copy(update={"trials": trials}), *report.variants[1:]]
    candidates = _candidates(tmp_path, report.model_copy(update={"variants": variants}))

    partial = measure(candidates[0], ["p1", "p2"], [], 0.95)
    assert partial.mean_latency_ms is None and partial.p95_latency_ms is None
    complete = measure(candidates[0], ["p2"], [], 0.95)
    assert complete.mean_latency_ms is not None
    violations = check_constraints(partial, ModelConstraints(max_p95_latency_ms=5000))
    assert [v.constraint for v in violations] == ["max_p95_latency_ms"]
    assert "cannot be verified" in violations[0].message


def test_unknown_provider_fails_a_block_list() -> None:
    blocked = ModelConstraints(blocked_providers=["bad"])
    violations = check_constraints(_metrics(provider=None), blocked)
    assert [v.constraint for v in violations] == ["blocked_providers"]
    assert "Provider is unknown" in violations[0].message
    assert check_constraints(_metrics(provider="good"), blocked) == []
    assert check_constraints(_metrics(provider=None), ModelConstraints()) == []
