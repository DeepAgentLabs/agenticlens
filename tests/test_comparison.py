from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.comparison import compare_runs, render_comparison_markdown
from agenticlens.comparison.runner import summarize_runs
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def _run(
    *,
    success: bool,
    tokens: int,
    latency_ms: float,
    cost: float | None = None,
) -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        application_name="benchmark",
        started_at=started,
        completed_at=started + timedelta(milliseconds=latency_ms),
        status=RunStatus.SUCCEEDED if success else RunStatus.FAILED,
        task_success=success,
        spans=[
            Span(
                name="model",
                span_type=SpanType.MODEL_CALL,
                status=RunStatus.SUCCEEDED if success else RunStatus.FAILED,
                input_tokens=tokens,
                estimated_cost_usd=cost,
            )
        ],
    )


def test_summarize_repeated_runs():
    summary = summarize_runs(
        "baseline",
        [
            _run(success=True, tokens=100, latency_ms=100, cost=0.1),
            _run(success=False, tokens=200, latency_ms=300, cost=0.2),
        ],
    )
    assert summary.run_count == 2
    assert summary.success_rate == 0.5
    assert summary.tokens.mean == 150
    assert summary.tokens.median == 150
    assert summary.tokens.p95 == pytest.approx(195)
    assert summary.cost_per_successful_task == pytest.approx(0.3)


def test_compare_detects_quality_and_efficiency_regressions():
    baseline = [_run(success=True, tokens=100, latency_ms=100) for _ in range(2)]
    candidate = [
        _run(success=True, tokens=120, latency_ms=130),
        _run(success=False, tokens=120, latency_ms=130),
    ]
    report = compare_runs(baseline, candidate, regression_threshold=0.1)
    assert set(report.regressions) == {
        "success_rate",
        "mean_tokens",
        "mean_latency_ms",
    }
    assert report.success_rate_delta.absolute == -0.5


def test_comparison_requires_runs():
    with pytest.raises(ValueError, match="At least one run"):
        summarize_runs("empty", [])


def test_comparison_adds_minimum_sample_guidance_and_markdown():
    baseline = [_run(success=True, tokens=100, latency_ms=100)]
    candidate = [_run(success=True, tokens=90, latency_ms=90)]
    report = compare_runs(baseline, candidate)

    assert report.sample_size_guidance is not None
    markdown = render_comparison_markdown(report)
    assert "Sample Size Guidance" in markdown
