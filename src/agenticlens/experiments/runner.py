import json
import random
import statistics
from pathlib import Path
from statistics import NormalDist

import yaml

from agenticlens.comparison.stats import metric_delta, percentile
from agenticlens.evaluation import (
    ConfidenceInterval,
    EvaluatorRegistry,
    HTTPTarget,
    PythonTarget,
    TestSuite,
    load_suite,
    run_live_suite,
)
from agenticlens.experiments.models import (
    ExperimentComparison,
    ExperimentManifest,
    ExperimentMetricSummary,
    ExperimentReport,
    ExperimentTrialResult,
    ExperimentVariant,
    ExperimentVariantResult,
    ExperimentVariantSummary,
)


def _load_data(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def load_manifest(path: Path) -> ExperimentManifest:
    return ExperimentManifest.model_validate(_load_data(path))


def _z_value(confidence_level: float) -> float:
    return NormalDist().inv_cdf(0.5 + confidence_level / 2)


def _mean_confidence_interval(
    values: list[float],
    *,
    confidence_level: float,
) -> tuple[float, float] | None:
    if not values:
        return None
    mean = statistics.fmean(values)
    if len(values) == 1:
        return (mean, mean)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    margin = _z_value(confidence_level) * (variance / len(values)) ** 0.5
    return (mean - margin, mean + margin)


def _metric_summary(
    values: list[float],
    *,
    confidence_level: float,
    bounded: bool = False,
) -> ExperimentMetricSummary:
    mean = statistics.fmean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    interval = _mean_confidence_interval(values, confidence_level=confidence_level)
    confidence_interval = None
    if interval is not None:
        lower, upper = interval
        if bounded:
            lower = max(0.0, lower)
            upper = min(1.0, upper)
        confidence_interval = ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence_level=confidence_level,
            method="normal_approximation",
        )
    return ExperimentMetricSummary(
        count=len(values),
        mean=mean,
        median=statistics.median(values),
        p95=percentile(values, 0.95),
        standard_deviation=deviation,
        coefficient_of_variation=deviation / mean if mean else None,
        confidence_interval=confidence_interval,
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


def run_experiment(
    manifest: ExperimentManifest,
    suite: TestSuite,
    *,
    registry: EvaluatorRegistry | None = None,
    confidence_level: float = 0.95,
    regression_threshold: float = 0.05,
) -> ExperimentReport:
    trial_results_by_variant: dict[str, list[ExperimentTrialResult]] = {
        variant.id: [] for variant in manifest.variants
    }
    targets_by_variant = {variant.id: _target_for_variant(variant) for variant in manifest.variants}
    for trial_index, variant in _work_items(manifest):
        try:
            report = run_live_suite(suite, targets_by_variant[variant.id], registry=registry)
        except Exception as exc:
            trial_results_by_variant[variant.id].append(
                ExperimentTrialResult(
                    trial_index=trial_index,
                    status="failed",
                    error_message=str(exc),
                )
            )
            continue
        trial_results_by_variant[variant.id].append(
            ExperimentTrialResult(
                trial_index=trial_index,
                status="succeeded",
                report=report,
            )
        )

    variant_results: list[ExperimentVariantResult] = []
    for variant in manifest.variants:
        trials = sorted(
            trial_results_by_variant[variant.id],
            key=lambda trial_result: trial_result.trial_index,
        )
        completed_reports = [
            trial.report
            for trial in trials
            if trial.report is not None and trial.status == "succeeded"
        ]
        pass_rates = [trial.summary.pass_rate for trial in completed_reports]
        average_scores = [trial.summary.average_score for trial in completed_reports]
        average_latencies = [trial.summary.average_latency_ms for trial in completed_reports]
        total_costs = [
            trial.summary.total_cost_usd
            for trial in completed_reports
            if trial.summary.total_cost_usd is not None
        ]
        completed_trials = len(completed_reports)
        failed_trials = len(trials) - completed_trials
        successful_trials = sum(1 for trial in completed_reports if trial.summary.failed_cases == 0)
        variant_results.append(
            ExperimentVariantResult(
                variant_id=variant.id,
                variant_name=variant.name,
                target_kind=variant.target_kind,
                trials=trials,
                summary=ExperimentVariantSummary(
                    attempted_trials=len(trials),
                    completed_trials=completed_trials,
                    failed_trials=failed_trials,
                    successful_trials=successful_trials,
                    trial_success_rate=successful_trials / len(trials) if trials else 0.0,
                    pass_rate=(
                        _metric_summary(
                            pass_rates,
                            confidence_level=confidence_level,
                            bounded=True,
                        )
                        if pass_rates
                        else None
                    ),
                    average_score=(
                        _metric_summary(
                            average_scores,
                            confidence_level=confidence_level,
                            bounded=True,
                        )
                        if average_scores
                        else None
                    ),
                    average_latency_ms=(
                        _metric_summary(
                            average_latencies,
                            confidence_level=confidence_level,
                        )
                        if average_latencies
                        else None
                    ),
                    total_cost_usd=(
                        _metric_summary(total_costs, confidence_level=confidence_level)
                        if total_costs
                        else None
                    ),
                ),
            )
        )

    baseline = next(
        result for result in variant_results if result.variant_id == manifest.baseline_variant_id
    )
    baseline_pass_rate = baseline.summary.pass_rate
    baseline_average_score = baseline.summary.average_score
    baseline_average_latency = baseline.summary.average_latency_ms
    comparisons = [
        ExperimentComparison(
            baseline_variant_id=baseline.variant_id,
            candidate_variant_id=result.variant_id,
            pass_rate_delta=metric_delta(
                baseline_pass_rate.mean,
                result.summary.pass_rate.mean,
                regression_threshold,
                lower_is_better=False,
            ),
            average_score_delta=metric_delta(
                baseline_average_score.mean,
                result.summary.average_score.mean,
                regression_threshold,
                lower_is_better=False,
            ),
            average_latency_ms_delta=metric_delta(
                baseline_average_latency.mean,
                result.summary.average_latency_ms.mean,
                regression_threshold,
                lower_is_better=True,
            ),
            total_cost_usd_delta=(
                metric_delta(
                    baseline.summary.total_cost_usd.mean,
                    result.summary.total_cost_usd.mean,
                    regression_threshold,
                    lower_is_better=True,
                )
                if baseline.summary.total_cost_usd is not None
                and result.summary.total_cost_usd is not None
                else None
            ),
        )
        for result in variant_results
        if result.variant_id != baseline.variant_id
        and baseline_pass_rate is not None
        and baseline_average_score is not None
        and baseline_average_latency is not None
        and result.summary.pass_rate is not None
        and result.summary.average_score is not None
        and result.summary.average_latency_ms is not None
    ]
    frontier = _pareto_frontier(variant_results)
    updated_results = [
        result.model_copy(update={"pareto_optimal": result.variant_id in frontier})
        for result in variant_results
    ]
    return ExperimentReport(
        experiment_name=manifest.name,
        experiment_version=manifest.version,
        suite_name=suite.name,
        suite_version=suite.version,
        baseline_variant_id=manifest.baseline_variant_id,
        trial_count=manifest.trial_count,
        random_seed=manifest.random_seed,
        variants=updated_results,
        comparisons=comparisons,
        pareto_frontier_variant_ids=frontier,
    )


def load_experiment_suite(path: Path) -> TestSuite:
    return load_suite(path)
