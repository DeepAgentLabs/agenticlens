"""Anomaly detection against baseline runs.

Uses the robust z-score (Iglewicz and Hoaglin): ``0.6745 * (x - median) / MAD``.
Median and MAD resist the outliers a baseline of real runs usually contains,
unlike mean and standard deviation. A value is anomalous when its robust z
exceeds the threshold (3.5 by default). When the MAD is zero (every
baseline value identical), any different value is reported with
``robust_z=None`` so the reader sees it was not scored on a scale.
"""

from collections import defaultdict
from collections.abc import Callable, Sequence
from statistics import median
from typing import Literal

from agenticlens.diagnosis.models import Anomaly, AnomalyReport
from agenticlens.models.trace import Run, Span

DEFAULT_THRESHOLD = 3.5
DEFAULT_MIN_BASELINE = 5
_CONSISTENCY = 0.6745

Metric = Literal["latency_ms", "total_tokens", "cost_usd"]

_SPAN_METRICS: dict[Metric, Callable[[Span], float | None]] = {
    "latency_ms": lambda span: span.latency_ms,
    "total_tokens": lambda span: float(span.total_tokens),
    "cost_usd": lambda span: span.estimated_cost_usd,
}
_RUN_METRICS: dict[Metric, Callable[[Run], float | None]] = {
    "latency_ms": lambda run: run.total_latency_ms if run.completed_at else None,
    "total_tokens": lambda run: float(run.total_tokens),
    "cost_usd": lambda run: run.estimated_cost_usd,
}


def span_key(span: Span) -> str:
    return f"{span.span_type.value}:{span.name}"


def _score(
    observed: float, baseline: list[float], threshold: float
) -> tuple[bool, float, float, float | None]:
    center = median(baseline)
    mad = median(abs(value - center) for value in baseline)
    if mad == 0:
        return observed != center, center, mad, None
    robust_z = _CONSISTENCY * (observed - center) / mad
    return abs(robust_z) > threshold, center, mad, round(robust_z, 4)


def detect_anomalies(
    run: Run,
    baseline: Sequence[Run],
    *,
    threshold: float = DEFAULT_THRESHOLD,
    min_baseline_samples: int = DEFAULT_MIN_BASELINE,
) -> AnomalyReport:
    """Compare `run`'s run-level and per-span metrics with `baseline` runs.

    Spans are matched across runs by ``<span_type>:<name>``. Repeated spans
    with the same key are summed per run, so a step that suddenly runs three
    times shows up as a token or latency anomaly. Keys with fewer than
    `min_baseline_samples` baseline values are skipped with a warning.
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if min_baseline_samples < 2:
        raise ValueError("min_baseline_samples must be at least 2")
    report = AnomalyReport(
        threshold=threshold,
        min_baseline_samples=min_baseline_samples,
        baseline_runs=len(baseline),
    )
    if len(baseline) < min_baseline_samples:
        report.warnings.append(
            f"Only {len(baseline)} baseline run(s); at least {min_baseline_samples} are needed "
            "for anomaly detection."
        )
        return report

    for metric, measure_run in _RUN_METRICS.items():
        observed = measure_run(run)
        values = [v for v in (measure_run(b) for b in baseline) if v is not None]
        if observed is None or len(values) < min_baseline_samples:
            continue
        flagged, center, mad, robust_z = _score(observed, values, threshold)
        if flagged:
            report.anomalies.append(
                Anomaly(
                    scope="run",
                    key="run",
                    metric=metric,
                    observed=observed,
                    baseline_median=center,
                    baseline_mad=mad,
                    robust_z=robust_z,
                    direction="high" if observed > center else "low",
                    baseline_samples=len(values),
                )
            )

    def totals(target: Run) -> dict[str, dict[Metric, float | None]]:
        sums: dict[str, dict[Metric, float | None]] = defaultdict(dict)
        for span in target.spans:
            bucket = sums[span_key(span)]
            for metric, measure in _SPAN_METRICS.items():
                value = measure(span)
                previous = bucket.get(metric, 0.0)
                bucket[metric] = None if value is None or previous is None else previous + value
        return sums

    observed_spans = totals(run)
    baseline_spans = [totals(b) for b in baseline]
    skipped: list[str] = []
    for key in sorted(observed_spans):
        for metric in _SPAN_METRICS:
            observed = observed_spans[key].get(metric)
            values = [
                value
                for sums in baseline_spans
                if key in sums and (value := sums[key].get(metric)) is not None
            ]
            if observed is None:
                continue
            if len(values) < min_baseline_samples:
                if key not in skipped:
                    skipped.append(key)
                continue
            flagged, center, mad, robust_z = _score(observed, values, threshold)
            if flagged:
                report.anomalies.append(
                    Anomaly(
                        scope="span",
                        key=key,
                        metric=metric,
                        observed=observed,
                        baseline_median=center,
                        baseline_mad=mad,
                        robust_z=robust_z,
                        direction="high" if observed > center else "low",
                        baseline_samples=len(values),
                        span_ids=[s.span_id for s in run.spans if span_key(s) == key],
                    )
                )
    if skipped:
        report.warnings.append(
            "Too few baseline samples to score: "
            + ", ".join(skipped[:10])
            + (f" (+{len(skipped) - 10} more)" if len(skipped) > 10 else "")
        )
    return report
