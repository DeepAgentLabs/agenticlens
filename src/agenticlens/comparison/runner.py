import statistics
from pathlib import Path

from agenticlens.comparison.models import (
    ComparisonReport,
    MetricSummary,
    RunGroupSummary,
)
from agenticlens.comparison.stats import metric_delta, percentile
from agenticlens.models.trace import Run, RunStatus


def load_runs(path: Path) -> list[Run]:
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    if not files:
        raise ValueError(f"No JSON traces found at {path}")
    return [Run.model_validate_json(file.read_text(encoding="utf-8")) for file in files]

def _metrics(values: list[float]) -> MetricSummary:
    mean = statistics.fmean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    return MetricSummary(
        count=len(values),
        mean=mean,
        median=statistics.median(values),
        p95=percentile(values, 0.95),
        standard_deviation=deviation,
        coefficient_of_variation=deviation / mean if mean else None,
    )


def summarize_runs(label: str, runs: list[Run]) -> RunGroupSummary:
    if not runs:
        raise ValueError("At least one run is required")
    successes = sum(run.task_success is True or run.status is RunStatus.SUCCEEDED for run in runs)
    costs = [run.estimated_cost_usd for run in runs if run.estimated_cost_usd is not None]
    total_cost = sum(costs) if costs else None
    return RunGroupSummary(
        label=label,
        run_count=len(runs),
        success_rate=successes / len(runs),
        tokens=_metrics([float(run.total_tokens) for run in runs]),
        latency_ms=_metrics([run.total_latency_ms for run in runs]),
        cost_usd=_metrics(costs) if costs else None,
        cost_per_successful_task=total_cost / successes
        if total_cost is not None and successes
        else None,
    )

def compare_runs(
    baseline_runs: list[Run],
    candidate_runs: list[Run],
    *,
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
    regression_threshold: float = 0.05,
) -> ComparisonReport:
    baseline = summarize_runs(baseline_label, baseline_runs)
    candidate = summarize_runs(candidate_label, candidate_runs)
    success_delta = metric_delta(
        baseline.success_rate,
        candidate.success_rate,
        regression_threshold,
        lower_is_better=False,
    )
    token_delta = metric_delta(
        baseline.tokens.mean,
        candidate.tokens.mean,
        regression_threshold,
        lower_is_better=True,
    )
    latency_delta = metric_delta(
        baseline.latency_ms.mean,
        candidate.latency_ms.mean,
        regression_threshold,
        lower_is_better=True,
    )
    cost_delta = None
    if baseline.cost_usd is not None and candidate.cost_usd is not None:
        cost_delta = metric_delta(
            baseline.cost_usd.mean,
            candidate.cost_usd.mean,
            regression_threshold,
            lower_is_better=True,
        )
    deltas = {
        "success_rate": success_delta,
        "mean_tokens": token_delta,
        "mean_latency_ms": latency_delta,
        "mean_cost_usd": cost_delta,
    }
    observed_min = min(len(baseline_runs), len(candidate_runs))
    minimum_sample_size = 5
    guidance = None
    if observed_min < minimum_sample_size:
        guidance = (
            f"Only {observed_min} run(s) were provided for the smaller cohort; "
            f"collect at least {minimum_sample_size} runs per cohort for more stable comparisons."
        )
    return ComparisonReport(
        baseline=baseline,
        candidate=candidate,
        success_rate_delta=success_delta,
        mean_tokens_delta=token_delta,
        mean_latency_ms_delta=latency_delta,
        mean_cost_usd_delta=cost_delta,
        regression_threshold=regression_threshold,
        regressions=[name for name, delta in deltas.items() if delta and delta.regressed],
        minimum_sample_size=minimum_sample_size,
        sample_size_guidance=guidance,
    )
