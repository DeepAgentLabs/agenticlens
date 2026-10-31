"""Projected and observed outcomes are reported independently after adoption."""

from datetime import datetime, timezone

import pytest

from agenticlens.models.trace import SpanType
from agenticlens.optimization import (
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    evaluate_outcome,
    render_outcome_markdown,
    report_sha256,
)
from optimization_support import run, span


def _tool_run(run_id: str, calls: int, *, success: bool = True):
    spans = [
        span(
            run_id,
            i,
            SpanType.TOOL_CALL,
            tool_name="lookup",
            attributes={"tool_args": {"id": 1}, "idempotent": True},
        )
        for i in range(calls)
    ]
    spans.append(span(run_id, 99, SpanType.MODEL_CALL))
    return run(run_id, spans, task_success=success)


@pytest.fixture()
def before():
    return [_tool_run(f"b{i}", 3) for i in range(4)]


@pytest.fixture()
def report(before):
    return analyze_optimizations(before)


def _id(report, kind="tool_result_caching"):
    return next(o.opportunity_id for o in report.opportunities if o.kind == kind)


def test_realized_when_the_saving_appears_and_the_rule_stops_firing(report, before):
    after = [_tool_run(f"a{i}", 1) for i in range(4)]
    outcome = evaluate_outcome(report, _id(report), before, after)
    assert outcome.status == "realized"
    assert outcome.realized_basis == "tokens"
    assert outcome.realized_ratio == pytest.approx(1.0)
    assert outcome.observed.tokens_per_run.delta == pytest.approx(-220)
    assert outcome.observed.still_detected is False
    # The projection is copied verbatim, never adjusted by what was observed.
    assert outcome.projected == report.opportunity(_id(report)).benefit


def test_partially_realized_when_the_rule_still_fires(report, before):
    after = [_tool_run(f"a{i}", 2) for i in range(4)]
    outcome = evaluate_outcome(report, _id(report), before, after)
    assert outcome.status == "partially_realized"
    assert outcome.observed.still_detected is True


def test_not_realized_when_nothing_changed(report, before):
    outcome = evaluate_outcome(report, _id(report), before, before)
    assert outcome.status == "not_realized"


def test_quality_regression_takes_precedence_over_savings(report, before):
    after = [_tool_run(f"a{i}", 1, success=i == 0) for i in range(4)]
    outcome = evaluate_outcome(report, _id(report), before, after)
    assert outcome.status == "quality_regressed"
    assert outcome.observed.success_rate.delta == pytest.approx(-0.75)


def test_insufficient_evidence_with_too_few_runs(report, before):
    outcome = evaluate_outcome(report, _id(report), before, [_tool_run("a", 1)])
    assert outcome.status == "insufficient_evidence"


def test_ledger_status_is_recorded_and_unadopted_changes_are_noted(tmp_path, report, before):
    ledger = RecommendationLedger(tmp_path / "ledger.jsonl")
    ledger.record(
        report,
        RecommendationDecision(
            opportunity_id=_id(report),
            report_sha256=report_sha256(report),
            status="accepted",
            decided_by="t",
            decided_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        ),
    )
    after = [_tool_run(f"a{i}", 1) for i in range(4)]
    outcome = evaluate_outcome(report, _id(report), before, after, ledger=ledger)
    assert outcome.decision_status == "accepted"
    assert any("not 'adopted'" in reason for reason in outcome.reasons)
    assert "realized" in render_outcome_markdown(outcome)


def test_prompt_caching_is_judged_on_cost():
    attrs = {"prompt.prefix_sha256": "p", "prompt.prefix_tokens": 1000}
    before = [
        run(
            f"b{i}",
            [span(f"b{i}", 1, SpanType.MODEL_CALL, tokens=(2000, 0), cost=0.02, attributes=attrs)],
        )
        for i in range(4)
    ]
    cached = {**attrs, "prompt.cached_tokens": 1000}
    after = [
        run(
            f"a{i}",
            [
                span(
                    f"a{i}", 1, SpanType.MODEL_CALL, tokens=(2000, 0), cost=0.011, attributes=cached
                )
            ],
        )
        for i in range(4)
    ]
    report = analyze_optimizations(before)
    outcome = evaluate_outcome(report, _id(report, "prompt_caching"), before, after)
    assert outcome.realized_basis == "cost_usd"
    assert outcome.observed.still_detected is False
    assert outcome.status == "realized"
