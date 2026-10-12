import math

import pytest

from agenticlens.experiments import (
    pass_at_k,
    pass_hat_k,
    two_proportion_p_value,
    wilson_interval,
)


@pytest.mark.parametrize(
    ("n", "c", "k", "expected"),
    [
        (5, 0, 1, 0.0),
        (5, 5, 5, 1.0),
        (5, 2, 1, 0.4),
        (5, 2, 2, 1 - math.comb(3, 2) / math.comb(5, 2)),  # 0.7
        (5, 4, 2, 1.0),  # only one failure, so any 2 draws include a pass
    ],
)
def test_pass_at_k_unbiased_estimator(n: int, c: int, k: int, expected: float) -> None:
    assert pass_at_k(n, c, k) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("n", "c", "k", "expected"),
    [
        (5, 5, 5, 1.0),
        (5, 4, 5, 0.0),
        (5, 2, 1, 0.4),
        (5, 3, 2, math.comb(3, 2) / math.comb(5, 2)),  # 0.3
    ],
)
def test_pass_hat_k(n: int, c: int, k: int, expected: float) -> None:
    assert pass_hat_k(n, c, k) == pytest.approx(expected)


def test_pass_hat_k_never_exceeds_pass_at_k() -> None:
    for n in range(1, 7):
        for c in range(n + 1):
            for k in range(1, n + 1):
                assert pass_hat_k(n, c, k) <= pass_at_k(n, c, k) + 1e-12


@pytest.mark.parametrize(("n", "c", "k"), [(3, 4, 1), (3, 1, 0), (3, 1, 4)])
def test_invalid_arguments(n: int, c: int, k: int) -> None:
    with pytest.raises(ValueError):
        pass_at_k(n, c, k)


def test_wilson_interval_matches_reference_values() -> None:
    # 8/10 at 95%: Wilson interval (0.490, 0.943).
    lower, upper = wilson_interval(8, 10, 0.95)
    assert lower == pytest.approx(0.4902, abs=1e-3)
    assert upper == pytest.approx(0.9433, abs=1e-3)
    assert wilson_interval(0, 5, 0.95)[0] == 0.0
    assert wilson_interval(5, 5, 0.95)[1] == 1.0
    with pytest.raises(ValueError):
        wilson_interval(0, 0, 0.95)


def test_two_proportion_p_value() -> None:
    assert two_proportion_p_value(50, 100, 50, 100) == pytest.approx(1.0)
    # 90/100 vs 70/100: z ~ 3.54, p ~ 0.0004.
    assert two_proportion_p_value(90, 100, 70, 100) == pytest.approx(0.0004, abs=1e-4)
    assert two_proportion_p_value(10, 10, 10, 10) == 1.0
    assert two_proportion_p_value(1, 0, 1, 2) is None


@pytest.mark.parametrize("level", [0.0, 1.0, -0.5, 1.5])
def test_interval_helpers_reject_invalid_confidence_levels(level: float) -> None:
    with pytest.raises(ValueError, match="confidence_level"):
        wilson_interval(3, 5, level)
