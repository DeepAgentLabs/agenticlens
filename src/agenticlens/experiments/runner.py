import json
import random
import statistics
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from agenticlens.comparison.stats import metric_delta, percentile
from agenticlens.evaluation import (
    ConfidenceInterval,
    EvaluationReport,
    EvaluationSample,
    EvaluatorRegistry,
    HTTPTarget,
    PythonTarget,
    TestSuite,
    evaluate_suite,
    load_suite,
    run_live_suite,
)
from agenticlens.evaluation._trace_adapter import to_eval_trace_dict
from agenticlens.experiments.models import (
    ExperimentCaseResult,
    ExperimentComparison,
    ExperimentManifest,
    ExperimentMetricSummary,
    ExperimentRandomization,
    ExperimentReport,
    ExperimentTrialResult,
    ExperimentVariant,
    ExperimentVariantResult,
    ExperimentVariantSummary,
    FactorLevelSummary,
)
from agenticlens.experiments.stats import (
    mean_interval,
    pass_at_k,
    pass_hat_k,
    two_proportion_p_value,
    wilson_interval,
)

UNSET_FACTOR = "(unset)"


def _load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def load_manifest(path: Path) -> ExperimentManifest:
    """Load a manifest; relative `recorded` targets resolve against its directory."""
    manifest = ExperimentManifest.model_validate(_load_data(path))
    variants = [
        variant.model_copy(update={"target": str(path.parent / variant.target)})
        if variant.target_kind == "recorded" and not Path(variant.target).is_absolute()
        else variant
        for variant in manifest.variants
    ]
    return manifest.model_copy(update={"variants": variants})


def load_recorded_trials(path: Path) -> list[list[EvaluationSample]]:
    """Load saved per-trial samples for a `recorded` variant.

    Accepts `{"trials": [{"samples": [...]}, ...]}` or `{"trials": [[...], ...]}`.
    Each sample's trace may be `EvalTrace`-shaped or AgenticLens `Run`-shaped.
    """
    data = _load_data(path)
    trials = data.get("trials") if isinstance(data, dict) else None
    if not isinstance(trials, list) or not trials:
        raise ValueError(f"recorded trials file {path} must define a non-empty 'trials' list")
    loaded: list[list[EvaluationSample]] = []
    for index, trial in enumerate(trials, start=1):
        items = trial.get("samples") if isinstance(trial, dict) else trial
        if not isinstance(items, list):
            raise ValueError(f"recorded trial {index} in {path} must be a list of samples")
        loaded.append(
            [
                EvaluationSample.model_validate(
                    {**item, "trace": to_eval_trace_dict(item.get("trace", {}))}
                )
                for item in items
            ]
        )
    return loaded


def _metric_summary(
    values: list[float],
    *,
    confidence_level: float,
    bounded: bool = False,
) -> ExperimentMetricSummary:
    mean = statistics.fmean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    lower, upper = mean_interval(values, confidence_level)
    if bounded:
        lower = max(0.0, lower)
        upper = min(1.0, upper)
    return ExperimentMetricSummary(
        count=len(values),
        mean=mean,
        median=statistics.median(values),
        p95=percentile(values, 0.95),
        standard_deviation=deviation,
        coefficient_of_variation=deviation / mean if mean else None,
        confidence_interval=ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence_level=confidence_level,
            method="normal_approximation",
        ),
    )


def _target_for_variant(variant: ExperimentVariant) -> PythonTarget | HTTPTarget:
    if variant.target_kind == "python":
        return PythonTarget(callable_path=variant.target, timeout_seconds=variant.timeout_seconds)
    return HTTPTarget(url=variant.target, timeout_seconds=variant.timeout_seconds)


def _pareto_frontier(variants: list[ExperimentVariantResult]) -> list[str]:
    frontier: list[str] = []
    for candidate in variants:
        if (
            candidate.summary.average_score is None
            or candidate.summary.average_latency_ms is None
            or candidate.summary.pass_rate is None
        ):
            continue
        dominated = False
        for other in variants:
            if other.variant_id == candidate.variant_id:
                continue
            if (
                other.summary.average_score is None
                or other.summary.average_latency_ms is None
                or other.summary.pass_rate is None
            ):
                continue
            candidate_cost = candidate.summary.total_cost_usd
            other_cost = other.summary.total_cost_usd
            if candidate_cost is None or other_cost is None:
                cost_not_worse = True
                cost_strictly_better = False
            else:
                cost_not_worse = other_cost.mean <= candidate_cost.mean
                cost_strictly_better = other_cost.mean < candidate_cost.mean
            not_worse = (
                other.summary.trial_success_rate >= candidate.summary.trial_success_rate
                and other.summary.pass_rate.mean >= candidate.summary.pass_rate.mean
                and other.summary.average_score.mean >= candidate.summary.average_score.mean
                and (
                    other.summary.average_latency_ms.mean
                    <= candidate.summary.average_latency_ms.mean
                )
                and cost_not_worse
            )
            strictly_better = (
                other.summary.trial_success_rate > candidate.summary.trial_success_rate
                or other.summary.pass_rate.mean > candidate.summary.pass_rate.mean
                or other.summary.average_score.mean > candidate.summary.average_score.mean
                or other.summary.average_latency_ms.mean < candidate.summary.average_latency_ms.mean
                or cost_strictly_better
            )
            if not_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate.variant_id)
    return frontier


def _work_items(manifest: ExperimentManifest) -> list[tuple[int, ExperimentVariant]]:
    items = [
        (trial_index, variant)
        for variant in manifest.variants
        for trial_index in range(1, manifest.trial_count + 1)
    ]
    if manifest.random_seed is not None:
        random.Random(manifest.random_seed).shuffle(items)
    return items


def _case_score(scores: list[float]) -> float | None:
    return statistics.fmean(scores) if scores else None


def _case_results(
    suite: TestSuite,
    trials: list[ExperimentTrialResult],
    pass_k: list[int],
) -> list[ExperimentCaseResult]:
    results: list[ExperimentCaseResult] = []
    for case in suite.cases:
        outcomes: list[bool] = []
        case_scores: list[float] = []
        for trial in trials:
            evaluation = (
                next((item for item in trial.report.cases if item.case_id == case.id), None)
                if trial.report is not None
                else None
            )
            if evaluation is None:
                outcomes.append(False)
                continue
            outcomes.append(evaluation.passed)
            score = _case_score([score.value for score in evaluation.scores if not score.skipped])
            if score is not None:
                case_scores.append(score)
        attempts = len(outcomes)
        passes = sum(outcomes)
        results.append(
            ExperimentCaseResult(
                case_id=case.id,
                case_name=case.name,
                attempts=attempts,
                passes=passes,
                pass_rate=passes / attempts if attempts else 0.0,
                pass_at_k={str(k): pass_at_k(attempts, passes, k) for k in pass_k if k <= attempts},
                pass_hat_k={
                    str(k): pass_hat_k(attempts, passes, k) for k in pass_k if k <= attempts
                },
                mean_score=statistics.fmean(case_scores) if case_scores else None,
                score_standard_deviation=(
                    statistics.stdev(case_scores) if len(case_scores) > 1 else None
                ),
                consistent=len(set(outcomes)) <= 1,
            )
        )
    return results


def _optional_summary(
    values: list[float], *, confidence_level: float, bounded: bool = False
) -> ExperimentMetricSummary | None:
    if not values:
        return None
    return _metric_summary(values, confidence_level=confidence_level, bounded=bounded)


def _variant_summary(
    trials: list[ExperimentTrialResult],
    cases: list[ExperimentCaseResult],
    *,
    pass_k: list[int],
    confidence_level: float,
) -> ExperimentVariantSummary:
    completed = [
        trial.report for trial in trials if trial.report is not None and trial.status == "succeeded"
    ]
    successful = sum(1 for report in completed if report.summary.failed_cases == 0)
    costs = [
        report.summary.total_cost_usd
        for report in completed
        if report.summary.total_cost_usd is not None
    ]
    case_attempts = sum(case.attempts for case in cases)
    case_passes = sum(case.passes for case in cases)
    interval = None
    if case_attempts:
        lower, upper = wilson_interval(case_passes, case_attempts, confidence_level)
        interval = ConfidenceInterval(
            lower=lower, upper=upper, confidence_level=confidence_level, method="wilson"
        )

    def mean_over_cases(field: str, k: int) -> float | None:
        values = [getattr(case, field).get(str(k)) for case in cases]
        present = [value for value in values if value is not None]
        return statistics.fmean(present) if present and len(present) == len(values) else None

    pass_at = {
        str(k): value for k in pass_k if (value := mean_over_cases("pass_at_k", k)) is not None
    }
    pass_hat = {
        str(k): value for k in pass_k if (value := mean_over_cases("pass_hat_k", k)) is not None
    }
    return ExperimentVariantSummary(
        attempted_trials=len(trials),
        completed_trials=len(completed),
        failed_trials=len(trials) - len(completed),
        successful_trials=successful,
        trial_success_rate=successful / len(trials) if trials else 0.0,
        pass_rate=_optional_summary(
            [report.summary.pass_rate for report in completed],
            confidence_level=confidence_level,
            bounded=True,
        ),
        average_score=_optional_summary(
            [report.summary.average_score for report in completed],
            confidence_level=confidence_level,
            bounded=True,
        ),
        average_latency_ms=_optional_summary(
            [report.summary.average_latency_ms for report in completed],
            confidence_level=confidence_level,
        ),
        total_cost_usd=_optional_summary(costs, confidence_level=confidence_level),
        case_attempts=case_attempts,
        case_passes=case_passes,
        case_pass_rate=case_passes / case_attempts if case_attempts else None,
        case_pass_rate_interval=interval,
        pass_at_k=pass_at,
        pass_hat_k=pass_hat,
        consistency_rate=(sum(case.consistent for case in cases) / len(cases) if cases else None),
        flaky_case_ids=[case.case_id for case in cases if not case.consistent],
        priced_trials=len(costs),
    )


def _changed_factors(
    baseline: ExperimentVariantResult, candidate: ExperimentVariantResult
) -> dict[str, list[str | None]]:
    names = sorted(set(baseline.factors) | set(candidate.factors))
    return {
        name: [baseline.factors.get(name), candidate.factors.get(name)]
        for name in names
        if baseline.factors.get(name) != candidate.factors.get(name)
    }


def _compare(
    baseline: ExperimentVariantResult,
    candidate: ExperimentVariantResult,
    *,
    confidence_level: float,
    regression_threshold: float,
    minimum_trials: int,
) -> ExperimentComparison | None:
    base, cand = baseline.summary, candidate.summary
    if (
        base.pass_rate is None
        or base.average_score is None
        or base.average_latency_ms is None
        or cand.pass_rate is None
        or cand.average_score is None
        or cand.average_latency_ms is None
    ):
        return None
    p_value = two_proportion_p_value(
        base.case_passes, base.case_attempts, cand.case_passes, cand.case_attempts
    )
    base_cases = {case.case_id: case for case in baseline.cases}
    regressed: list[str] = []
    improved: list[str] = []
    for case in candidate.cases:
        reference = base_cases.get(case.case_id)
        if reference is None:
            continue
        change = case.pass_rate - reference.pass_rate
        if change < -regression_threshold:
            regressed.append(case.case_id)
        elif change > regression_threshold:
            improved.append(case.case_id)
    warnings = [
        f"Variant {result.variant_id!r} completed {result.summary.completed_trials} trial(s), "
        f"fewer than the minimum of {minimum_trials}; treat this delta as exploratory."
        for result in (baseline, candidate)
        if result.summary.completed_trials < minimum_trials
    ]
    changed = _changed_factors(baseline, candidate)
    if len(changed) > 1:
        warnings.append(
            f"{len(changed)} factors changed at once ({', '.join(changed)}); "
            "the delta cannot be attributed to one of them."
        )
    return ExperimentComparison(
        baseline_variant_id=baseline.variant_id,
        candidate_variant_id=candidate.variant_id,
        # Case-level rates count crashed trials as failed attempts, so the
        # regression flag agrees with the case pass-rate delta shown in reports.
        pass_rate_delta=metric_delta(
            base.case_pass_rate if base.case_pass_rate is not None else base.pass_rate.mean,
            cand.case_pass_rate if cand.case_pass_rate is not None else cand.pass_rate.mean,
            regression_threshold,
            lower_is_better=False,
        ),
        average_score_delta=metric_delta(
            base.average_score.mean,
            cand.average_score.mean,
            regression_threshold,
            lower_is_better=False,
        ),
        average_latency_ms_delta=metric_delta(
            base.average_latency_ms.mean,
            cand.average_latency_ms.mean,
            regression_threshold,
            lower_is_better=True,
        ),
        total_cost_usd_delta=(
            metric_delta(
                base.total_cost_usd.mean,
                cand.total_cost_usd.mean,
                regression_threshold,
                lower_is_better=True,
            )
            if base.total_cost_usd is not None and cand.total_cost_usd is not None
            else None
        ),
        changed_factors=changed,
        case_pass_rate_delta=(
            cand.case_pass_rate - base.case_pass_rate
            if cand.case_pass_rate is not None and base.case_pass_rate is not None
            else None
        ),
        case_pass_rate_p_value=p_value,
        statistically_significant=(p_value < 1 - confidence_level if p_value is not None else None),
        regressed_case_ids=regressed,
        improved_case_ids=improved,
        warnings=warnings,
    )


def _mean_or_none(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present and len(present) == len(values) else None


def _factor_levels(variants: list[ExperimentVariantResult]) -> list[FactorLevelSummary]:
    names = sorted({name for variant in variants for name in variant.factors})
    levels: list[FactorLevelSummary] = []
    for name in names:
        groups: dict[str, list[ExperimentVariantResult]] = {}
        for variant in variants:
            groups.setdefault(variant.factors.get(name, UNSET_FACTOR), []).append(variant)
        if len(groups) < 2:
            continue
        for value in sorted(groups):
            members = groups[value]
            levels.append(
                FactorLevelSummary(
                    factor=name,
                    value=value,
                    variant_ids=[member.variant_id for member in members],
                    mean_pass_rate=_mean_or_none(
                        [m.summary.pass_rate.mean if m.summary.pass_rate else None for m in members]
                    ),
                    mean_average_score=_mean_or_none(
                        [
                            m.summary.average_score.mean if m.summary.average_score else None
                            for m in members
                        ]
                    ),
                    mean_latency_ms=_mean_or_none(
                        [
                            m.summary.average_latency_ms.mean
                            if m.summary.average_latency_ms
                            else None
                            for m in members
                        ]
                    ),
                    mean_cost_usd=_mean_or_none(
                        [
                            m.summary.total_cost_usd.mean if m.summary.total_cost_usd else None
                            for m in members
                        ]
                    ),
                    mean_trial_success_rate=statistics.fmean(
                        m.summary.trial_success_rate for m in members
                    ),
                )
            )
    return levels


TrialRunner = Callable[[ExperimentVariant, int], EvaluationReport]


def _trial_runner(
    manifest: ExperimentManifest,
    suite: TestSuite,
    registry: EvaluatorRegistry | None,
) -> TrialRunner:
    recorded: dict[str, list[list[EvaluationSample]]] = {}

    def run(variant: ExperimentVariant, trial_index: int) -> EvaluationReport:
        if variant.target_kind == "recorded":
            if variant.id not in recorded:
                recorded[variant.id] = load_recorded_trials(Path(variant.target))
            trials = recorded[variant.id]
            if trial_index > len(trials):
                raise ValueError(
                    f"recorded target has {len(trials)} trial(s); trial {trial_index} is missing"
                )
            return evaluate_suite(suite, trials[trial_index - 1], registry=registry)
        return run_live_suite(
            suite,
            _target_for_variant(variant),
            registry=registry,
            max_workers=manifest.max_workers,
        )

    return run


def run_experiment(
    manifest: ExperimentManifest,
    suite: TestSuite,
    *,
    registry: EvaluatorRegistry | None = None,
    confidence_level: float = 0.95,
    regression_threshold: float = 0.05,
) -> ExperimentReport:
    pass_k = manifest.resolved_pass_k()
    run_trial = _trial_runner(manifest, suite, registry)
    trial_results_by_variant: dict[str, list[ExperimentTrialResult]] = {
        variant.id: [] for variant in manifest.variants
    }
    execution_order: list[tuple[str, int]] = []
    for trial_index, variant in _work_items(manifest):
        execution_order.append((variant.id, trial_index))
        try:
            report = run_trial(variant, trial_index)
        except Exception as exc:
            trial_results_by_variant[variant.id].append(
                ExperimentTrialResult(
                    trial_index=trial_index, status="failed", error_message=str(exc)
                )
            )
            continue
        trial_results_by_variant[variant.id].append(
            ExperimentTrialResult(trial_index=trial_index, status="succeeded", report=report)
        )

    variant_results: list[ExperimentVariantResult] = []
    for variant in manifest.variants:
        trials = sorted(trial_results_by_variant[variant.id], key=lambda trial: trial.trial_index)
        cases = _case_results(suite, trials, pass_k)
        variant_results.append(
            ExperimentVariantResult(
                variant_id=variant.id,
                variant_name=variant.name,
                target_kind=variant.target_kind,
                factors=dict(variant.factors),
                trials=trials,
                summary=_variant_summary(
                    trials, cases, pass_k=pass_k, confidence_level=confidence_level
                ),
                cases=cases,
            )
        )

    baseline = next(
        result for result in variant_results if result.variant_id == manifest.baseline_variant_id
    )
    comparisons: list[ExperimentComparison] = []
    warnings: list[str] = []
    for result in variant_results:
        if result.variant_id == baseline.variant_id:
            continue
        comparison = _compare(
            baseline,
            result,
            confidence_level=confidence_level,
            regression_threshold=regression_threshold,
            minimum_trials=manifest.minimum_trials,
        )
        if comparison is None:
            warnings.append(
                f"Variant {result.variant_id!r} was not compared with the baseline: "
                "one of them has no completed trials."
            )
        else:
            comparisons.append(comparison)
    under_sampled = [
        result.variant_id
        for result in variant_results
        if result.summary.completed_trials < manifest.minimum_trials
    ]
    if under_sampled:
        warnings.append(
            f"{len(under_sampled)} variant(s) completed fewer than {manifest.minimum_trials} "
            f"trials ({', '.join(under_sampled)}); intervals and deltas are exploratory."
        )
    if manifest.trial_count > 1:
        warnings.append(
            "Case-level pass-rate intervals and p-values treat each case attempt as "
            "independent; attempts on the same case are correlated, so read them as "
            "approximate."
        )
    frontier = _pareto_frontier(variant_results)
    return ExperimentReport(
        experiment_name=manifest.name,
        experiment_version=manifest.version,
        suite_name=suite.name,
        suite_version=suite.version,
        baseline_variant_id=manifest.baseline_variant_id,
        trial_count=manifest.trial_count,
        random_seed=manifest.random_seed,
        confidence_level=confidence_level,
        regression_threshold=regression_threshold,
        pass_k=pass_k,
        minimum_trials=manifest.minimum_trials,
        randomization=ExperimentRandomization(
            random_seed=manifest.random_seed,
            shuffled=manifest.random_seed is not None,
            execution_order=execution_order,
        ),
        variants=[
            result.model_copy(update={"pareto_optimal": result.variant_id in frontier})
            for result in variant_results
        ],
        comparisons=comparisons,
        pareto_frontier_variant_ids=frontier,
        factor_levels=_factor_levels(variant_results),
        case_ids=[case.id for case in suite.cases],
        warnings=warnings,
    )


def load_experiment_suite(path: Path) -> TestSuite:
    return load_suite(path)


def load_experiment_report(path: Path) -> ExperimentReport:
    return ExperimentReport.model_validate_json(path.read_text(encoding="utf-8"))
