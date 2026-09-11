import math

from agenticlens.comparison.models import MetricDelta


def percentile(values: list[float], percentile_value: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percentile_value
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def metric_delta(
    baseline: float,
    candidate: float,
    threshold: float,
    *,
    lower_is_better: bool,
) -> MetricDelta:
    absolute = candidate - baseline
    if baseline == 0:
        relative = 0.0 if candidate == 0 else math.copysign(math.inf, absolute)
    else:
        relative = absolute / abs(baseline)
    degradation = -relative if not lower_is_better else relative
    return MetricDelta(
        absolute=absolute,
        relative=relative,
        regressed=degradation > threshold,
    )
