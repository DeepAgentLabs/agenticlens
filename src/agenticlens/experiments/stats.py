"""Statistics for repeated-trial experiments.

- pass@k: probability that at least one of k trials passes, using the
  unbiased estimator from Chen et al. (2021), "Evaluating Large Language
  Models Trained on Code": 1 - C(n - c, k) / C(n, k).
- pass^k: probability that all k trials pass, the reliability measure from
  Yao et al. (2024), "tau-bench": C(c, k) / C(n, k).

n is the number of trials attempted on a case and c the number that passed.
Both need k <= n.
"""

import math
import statistics
from statistics import NormalDist


def pass_at_k(trials: int, passes: int, k: int) -> float:
    _check(trials, passes, k)
    if trials - passes < k:
        return 1.0
    return 1.0 - math.comb(trials - passes, k) / math.comb(trials, k)


def pass_hat_k(trials: int, passes: int, k: int) -> float:
    _check(trials, passes, k)
    return math.comb(passes, k) / math.comb(trials, k)


def _check(trials: int, passes: int, k: int) -> None:
    if not 0 <= passes <= trials:
        raise ValueError("passes must be between 0 and trials")
    if not 1 <= k <= trials:
        raise ValueError("k must be between 1 and the number of trials")


def z_value(confidence_level: float) -> float:
    return NormalDist().inv_cdf(0.5 + confidence_level / 2)


def wilson_interval(successes: int, total: int, confidence_level: float) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if total <= 0:
        raise ValueError("total must be positive")
    z = z_value(confidence_level)
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    lower = 0.0 if successes == 0 else max(0.0, center - radius)
    upper = 1.0 if successes == total else min(1.0, center + radius)
    return lower, upper


def mean_interval(values: list[float], confidence_level: float) -> tuple[float, float]:
    """Normal-approximation interval for a mean; degenerate for one value."""
    if not values:
        raise ValueError("values must not be empty")
    mean = statistics.fmean(values)
    if len(values) == 1:
        return mean, mean
    margin = z_value(confidence_level) * statistics.stdev(values) / math.sqrt(len(values))
    return mean - margin, mean + margin


def two_proportion_p_value(
    successes_a: int, total_a: int, successes_b: int, total_b: int
) -> float | None:
    """Two-sided p-value of a pooled two-proportion z-test.

    Returns None when either group is empty, and 1.0 when the pooled
    proportion is 0 or 1 (both groups identical at the boundary).
    """
    if total_a <= 0 or total_b <= 0:
        return None
    pooled = (successes_a + successes_b) / (total_a + total_b)
    if pooled in (0.0, 1.0):
        return 1.0
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / total_a + 1 / total_b))
    z = (successes_a / total_a - successes_b / total_b) / standard_error
    return 2 * (1 - NormalDist().cdf(abs(z)))
