"""Per-category recommendations: constraints, confidence, fallbacks, savings, risks, matrix."""

from pathlib import Path

import pytest

from agenticlens.modelfit import (
    ModelCandidate,
    ModelConstraints,
    ModelFitConfig,
    ScoringWeights,
    TaskCategory,
    load_experiment_evidence,
    recommend_models,
    render_markdown,
    render_matrix_csv,
)
from modelfit_support import DEFAULT_CASES, Spec, build_report, fail_trial, passes, uniform

CATEGORIES = [
    TaskCategory(id="policy", tags=["policy"], monthly_volume=1000),
    TaskCategory(id="orders", tags=["orders"]),
    TaskCategory(id="safety", tags=["safety"]),
]


def _report(tmp_path: Path, trials: int = 10):
    """frontier: perfect and expensive; mid: good, cheaper; small: cheap, weak on policy/safety."""
    return build_report(
        tmp_path,
        {
            "frontier": Spec(uniform(DEFAULT_CASES, passes(trials)), cost=0.006, latency=1800),
            "mid": Spec(
                {
                    "p1": passes(trials),
                    "p2": passes(trials - 1, 1),
                    "o1": passes(trials),
                    "s1": passes(trials),
                },
                cost=0.002,
                latency=1100,
            ),
            "small": Spec(
                {
                    "p1": passes(trials // 2, trials - trials // 2),
                    "p2": passes(trials // 2, trials - trials // 2),
                    "o1": passes(trials),
                    "s1": passes(trials - 2, 2),
                },
                cost=0.0005,
                latency=400,
            ),
        },
    )


def _config(**values) -> ModelFitConfig:
    base = {
        "categories": CATEGORIES,
        "minimum_attempts": 5,
        "candidates": [
            ModelCandidate(variant_id="frontier", provider="a"),
            ModelCandidate(variant_id="mid", provider="b"),
            ModelCandidate(variant_id="small", provider="a"),
        ],
    }
    return ModelFitConfig(**{**base, **values})


def _category(report, category_id):
    return next(r for r in report.categories if r.category.id == category_id)


def test_recommendations_are_generated_per_task_category(tmp_path: Path) -> None:
    report = recommend_models([_report(tmp_path)], _config())

    assert [r.category.id for r in report.categories] == ["all", "policy", "orders", "safety"]
    assert report.reference_variant_id == "frontier"
    assert report.summary.categories == 4 and report.summary.candidates == 3
    orders = _category(report, "orders").recommendation
    assert orders.status == "recommended" and orders.variant_id == "small"
    assert _category(report, "policy").case_ids == ["p1", "p2"]


def test_hard_constraints_are_enforced(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(min_pass_rate=0.9, min_safety_pass_rate=1.0))
    report = recommend_models([_report(tmp_path)], config)

    for result in report.categories:
        small = next(c for c in result.candidates if c.variant_id == "small")
        assert small.feasible is False
        assert "min_safety_pass_rate" in [v.constraint for v in small.violations]
        assert result.recommendation.variant_id != "small"
        assert "small" in result.recommendation.rejected_variant_ids
    policy = _category(report, "policy").recommendation
    assert policy.variant_id == "mid"
    assert any(line.startswith("Rejected small:") for line in policy.explanation)


def test_category_overrides_apply_only_to_that_category(tmp_path: Path) -> None:
    categories = [
        TaskCategory(id="policy", tags=["policy"]),
        TaskCategory(
            id="orders",
            tags=["orders"],
            constraints=ModelConstraints(allowed_providers=["b"]),
        ),
    ]
    report = recommend_models([_report(tmp_path)], _config(categories=categories))

    assert _category(report, "orders").recommendation.variant_id == "mid"
    assert _category(report, "orders").constraints.allowed_providers == ["b"]
    assert _category(report, "policy").constraints.allowed_providers is None


def test_no_feasible_model_is_reported_not_guessed(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(max_cost_per_case_usd=0.0001))
    report = recommend_models([_report(tmp_path)], config)

    for result in report.categories:
        rec = result.recommendation
        assert rec.status == "no_feasible_model"
        assert rec.variant_id is None and rec.savings is None
        assert sorted(rec.rejected_variant_ids) == ["frontier", "mid", "small"]
    assert report.summary.recommended == 0
    assert report.summary.unfit_category_ids == ["all", "policy", "orders", "safety"]


def test_categories_without_cases_have_no_evidence(tmp_path: Path) -> None:
    config = _config(categories=[TaskCategory(id="ghost", tags=["nope"])], include_overall=False)
    report = recommend_models([_report(tmp_path)], config)

    assert report.categories[0].recommendation.status == "no_evidence"
    assert report.summary.unfit_category_ids == ["ghost"]
    assert any("matches no cases" in w for w in report.warnings)


def test_savings_are_tied_to_experiment_evidence(tmp_path: Path) -> None:
    path = tmp_path / "experiment.json"
    path.write_text(_report(tmp_path).model_dump_json(), encoding="utf-8")
    config = _config(defaults=ModelConstraints(min_pass_rate=0.9))
    report = recommend_models([load_experiment_evidence(path)], config)

    savings = _category(report, "policy").recommendation.savings
    assert savings is not None and savings.available
    assert (savings.reference_variant_id, savings.recommended_variant_id) == ("frontier", "mid")
    assert savings.cost_per_case_savings_usd == pytest.approx(0.004)
    assert savings.cost_per_case_savings_ratio == pytest.approx(0.004 / 0.006)
    assert savings.projected_monthly_savings_usd == pytest.approx(4.0)
    assert savings.reference_attempts == savings.recommended_attempts == 20
    assert savings.case_ids == ["p1", "p2"]
    assert savings.source_indexes == [0]
    assert savings.pass_rate_delta == pytest.approx(-0.05)
    assert savings.pass_rate_p_value is not None
    assert report.sources[0].file == "experiment.json"
    assert report.sources[0].sha256 is not None and len(report.sources[0].sha256) == 64


def test_savings_are_unavailable_when_costs_are_incomplete(tmp_path: Path) -> None:
    report = build_report(
        tmp_path,
        {
            "ref": Spec(uniform(DEFAULT_CASES, passes(6)), cost=None),
            "x": Spec(uniform(DEFAULT_CASES, passes(6)), cost=0.001),
            "y": Spec(uniform(DEFAULT_CASES, passes(3, 3)), cost=0.001),
        },
    )
    result = recommend_models([report], ModelFitConfig(include_overall=True, minimum_attempts=1))
    rec = result.categories[0].recommendation

    assert rec.variant_id == "x"
    assert rec.savings is not None and rec.savings.available is False
    assert "Cost evidence is incomplete for ref" in rec.savings.reason


def test_recommending_the_reference_reports_zero_savings(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(min_pass_rate=1.0))
    rec = _category(recommend_models([_report(tmp_path)], config), "all").recommendation

    assert rec.variant_id == "frontier"
    assert rec.savings is not None and rec.savings.cost_per_case_savings_usd == 0
    assert rec.savings.reason == "The recommendation is the reference."
    assert not any(r.kind in {"quality_regression", "regressed_cases"} for r in rec.quality_risks)


def test_quality_risks_and_alternatives_are_reported(tmp_path: Path) -> None:
    rec = _category(recommend_models([_report(tmp_path)], _config()), "orders").recommendation

    assert rec.variant_id == "small"
    kinds = {risk.kind: risk for risk in rec.quality_risks}
    assert kinds["safety_failures"].severity == "high"
    assert kinds["safety_failures"].case_ids == ["s1"]
    assert rec.confidence == "medium"
    assert "trades away quality or safety" in rec.confidence_reasons[0]
    assert [alt.variant_id for alt in rec.alternatives] == ["mid", "frontier"]
    assert all(alt.role == "alternative" for alt in rec.alternatives)


def test_significant_quality_regression_is_high_severity(tmp_path: Path) -> None:
    cost_heavy = ScoringWeights(quality=0.2, cost=0.8, latency=0, reliability=0)
    report = recommend_models([_report(tmp_path, trials=20)], _config(weights=cost_heavy))
    rec = _category(report, "policy").recommendation

    assert rec.variant_id == "small"
    regression = next(r for r in rec.quality_risks if r.kind == "quality_regression")
    assert regression.severity == "high"
    assert "statistically significant" in regression.message
    regressed = next(r for r in rec.quality_risks if r.kind == "regressed_cases")
    assert regressed.case_ids == ["p1", "p2"]
    assert rec.confidence == "medium"


def test_fallback_prefers_a_different_provider(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(min_pass_rate=0.9))
    rec = _category(recommend_models([_report(tmp_path)], config), "orders").recommendation

    assert rec.variant_id == "small"
    assert rec.fallback is not None and rec.fallback.role == "fallback"
    assert rec.fallback.variant_id == "mid"
    assert "different provider (b)" in rec.fallback.reason


def test_fallback_without_provider_diversity_says_so(tmp_path: Path) -> None:
    config = _config(
        candidates=[
            ModelCandidate(variant_id=v, provider="a") for v in ("frontier", "mid", "small")
        ]
    )
    rec = _category(recommend_models([_report(tmp_path)], config), "orders").recommendation
    assert rec.fallback is not None
    assert "does not protect against a provider outage" in rec.fallback.reason

    unknown = _config(candidates=[])
    rec = _category(recommend_models([_report(tmp_path)], unknown), "orders").recommendation
    assert rec.fallback is not None
    assert "provider diversity cannot be checked" in rec.fallback.reason


def test_single_feasible_candidate_has_no_fallback(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(allowed_providers=["b"]))
    rec = _category(recommend_models([_report(tmp_path)], config), "orders").recommendation

    assert rec.variant_id == "mid" and rec.fallback is None and rec.alternatives == []
    assert any(r.kind == "no_fallback" for r in rec.quality_risks)
    assert "only feasible candidate" in rec.confidence_reasons[0]


def test_low_evidence_lowers_confidence(tmp_path: Path) -> None:
    report = recommend_models([_report(tmp_path, trials=4)], _config(minimum_attempts=10))

    orders = _category(report, "orders").recommendation
    assert orders.confidence == "low"
    assert any(r.kind == "low_evidence" for r in orders.quality_risks)
    assert "orders" in report.summary.low_confidence_category_ids


def test_close_scores_without_significance_lower_confidence(tmp_path: Path) -> None:
    report = build_report(
        tmp_path,
        {
            "a": Spec({**uniform(DEFAULT_CASES, passes(10)), "p1": passes(9, 1)}),
            "b": Spec(uniform(DEFAULT_CASES, passes(10))),
            "c": Spec(uniform(DEFAULT_CASES, passes(1, 9))),
        },
    )
    quality_only = ScoringWeights(quality=1, cost=0, latency=0, reliability=0)
    config = ModelFitConfig(minimum_attempts=5, weights=quality_only)
    rec = recommend_models([report], config).categories[0].recommendation

    assert rec.variant_id == "b"
    assert rec.confidence == "medium"
    assert "not statistically significant" in rec.confidence_reasons[0]


def test_failed_trials_are_reported_as_risks(tmp_path: Path) -> None:
    report = fail_trial(_report(tmp_path), "small", 1)
    rec = _category(recommend_models([report], _config()), "orders").recommendation

    assert rec.variant_id == "small"
    failed = next(r for r in rec.quality_risks if r.kind == "failed_trials")
    assert "1 attempt(s)" in failed.message


def test_matrix_covers_every_category_and_candidate(tmp_path: Path) -> None:
    config = _config(defaults=ModelConstraints(min_pass_rate=0.9))
    report = recommend_models([_report(tmp_path)], config)

    assert len(report.matrix) == 4 * 3
    orders = {row.variant_id: row for row in report.matrix if row.category_id == "orders"}
    assert orders["small"].role == "recommended"
    assert orders["mid"].role == "fallback"
    assert orders["frontier"].role == "alternative"
    policy = {row.variant_id: row for row in report.matrix if row.category_id == "policy"}
    assert policy["small"].role == "infeasible" and policy["small"].violations == ["min_pass_rate"]

    csv_text = render_matrix_csv(report)
    assert csv_text.splitlines()[0].startswith("category_id,variant_id,model,provider,role")
    assert "orders,small,small,a,recommended,true,10,1," in csv_text
    markdown = render_markdown(report)
    assert "## Task-level model matrix" in markdown and "✅" in markdown


def test_reference_variant_must_be_a_candidate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a candidate"):
        recommend_models([_report(tmp_path)], _config(reference_variant_id="nope"))


def test_excluding_the_baseline_warns_and_disables_savings(tmp_path: Path) -> None:
    report = recommend_models([_report(tmp_path)], _config(exclude_variant_ids=["frontier"]))

    assert any("excluded, so savings are unavailable" in w for w in report.warnings)
    rec = _category(report, "orders").recommendation
    assert rec.savings is not None and rec.savings.available is False


def test_needs_reports_and_candidates(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least one experiment report"):
        recommend_models([])
    with pytest.raises(ValueError, match="every experiment variant is excluded"):
        recommend_models(
            [_report(tmp_path)], _config(exclude_variant_ids=["frontier", "mid", "small"])
        )


def test_default_config_derives_categories_from_tags(tmp_path: Path) -> None:
    report = recommend_models([_report(tmp_path)])
    assert [r.category.id for r in report.categories] == ["all", "orders", "policy", "safety"]


def test_savings_need_the_same_cases_as_the_reference(tmp_path: Path) -> None:
    first = _report(tmp_path)
    second = build_report(
        tmp_path,
        {
            "other-1": Spec(uniform({"p1": [], "x1": []}, passes(10)), cost=0.0001),
            "other-2": Spec(uniform({"p1": [], "x1": []}, passes(5, 5)), cost=0.0001),
            "other-3": Spec(uniform({"p1": [], "x1": []}, passes(5, 5)), cost=0.0001),
        },
        cases={"p1": ["policy"], "x1": ["policy"]},
        name="other",
    )
    report = recommend_models([first, second], _config())
    policy = _category(report, "policy").recommendation

    assert policy.variant_id == "other-1"
    assert policy.savings is not None and policy.savings.available is False
    assert "measured on different cases" in policy.savings.reason
    assert any("different suites" in w for w in report.warnings)


def test_cases_without_a_completed_trial_are_warned(tmp_path: Path) -> None:
    report = _report(tmp_path, trials=4)
    variants = [
        variant.model_copy(
            update={
                "trials": [
                    trial.model_copy(
                        update={
                            "report": trial.report.model_copy(
                                update={
                                    "cases": [c for c in trial.report.cases if c.case_id != "s1"]
                                }
                            )
                        }
                    )
                    for trial in variant.trials
                    if trial.report is not None
                ]
            }
        )
        for variant in report.variants
    ]
    result = recommend_models([report.model_copy(update={"variants": variants})], _config())

    assert any("No experiment completed a trial on s1" in w for w in result.warnings)
    assert "s1" in result.uncategorized_case_ids
