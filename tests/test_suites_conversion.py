"""Trace and feedback conversion into reviewable test cases."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from agentic_evals import EvalTrace, EvaluationSample, evaluate_suite

from agenticlens.models.trace import Run, RunStatus, Span, SpanType
from agenticlens.suites import (
    FeedbackRecord,
    case_from_feedback,
    case_from_run,
    cases_from_feedback,
    cases_from_runs,
    load_feedback,
    new_suite,
)

START = datetime(2026, 10, 1, tzinfo=timezone.utc)


def _run(
    run_id: str = "run-1",
    *,
    status: RunStatus = RunStatus.SUCCEEDED,
    task_success: bool | None = True,
    with_input: bool = True,
    tools: tuple[str, ...] = ("lookup", "lookup", "refund"),
) -> Run:
    spans = [
        Span(
            span_id="plan",
            name="plan",
            span_type=SpanType.PLANNING,
            input_data={"question": "Refund order 7"} if with_input else None,
            status=RunStatus.SUCCEEDED,
            estimated_cost_usd=0.001,
        )
    ]
    for index, tool in enumerate(tools):
        spans.append(
            Span(
                span_id=f"tool-{index}",
                parent_span_id="plan",
                name=tool,
                span_type=SpanType.TOOL_CALL,
                tool_name=tool,
                status=RunStatus.SUCCEEDED,
                estimated_cost_usd=0.0005,
            )
        )
    spans.append(
        Span(
            span_id="failed-tool",
            parent_span_id="plan",
            name="notify",
            span_type=SpanType.TOOL_CALL,
            tool_name="notify",
            status=RunStatus.FAILED,
            estimated_cost_usd=0.0,
        )
    )
    spans.append(
        Span(
            span_id="final",
            parent_span_id="plan",
            name="answer",
            span_type=SpanType.FINAL_RESPONSE,
            output_data="Refund issued for order 7.",
            status=RunStatus.SUCCEEDED,
            estimated_cost_usd=0.002,
        )
    )
    return Run(
        run_id=run_id,
        trace_id=f"trace-of-{run_id}",
        application_name="support-bot",
        task_type="billing",
        started_at=START,
        completed_at=START + timedelta(milliseconds=800),
        status=status,
        task_success=task_success,
        spans=spans,
        metadata={"tags": ["prod"]},
    )


def test_case_from_run_expects_observed_trajectory_and_limits() -> None:
    case = case_from_run(_run())
    assert case.id == "trace-run-1"
    assert case.input == {"question": "Refund order 7"}
    assert case.required_tools == ["lookup", "refund"]
    assert case.required_tool_order == ["lookup", "refund"]
    assert case.max_latency_ms == pytest.approx(1200.0)
    assert case.max_cost_usd == pytest.approx(0.0045 * 1.5)
    assert case.expected_output is None
    assert case.tags == ["from-trace", "prod"]
    assert case.metadata["review_status"] == "needs_review"
    assert case.metadata["domain"] == "billing"
    assert case.metadata["source"] == {
        "kind": "trace",
        "trace_id": "trace-of-run-1",
        "run_id": "run-1",
    }


def test_case_from_run_can_expect_recorded_output_and_skip_limits() -> None:
    case = case_from_run(_run(), include_output=True, latency_margin=None, cost_margin=None)
    assert case.expected_output == "Refund issued for order 7."
    assert case.max_latency_ms is None and case.max_cost_usd is None


def test_case_from_run_prefers_metadata_input() -> None:
    run = _run()
    run.metadata["input"] = "from metadata"
    assert case_from_run(run).input == "from metadata"


def test_converted_case_passes_against_its_own_trace() -> None:
    run = _run()
    case = case_from_run(run, include_output=True)
    trace = EvalTrace(
        trace_id=run.trace_id,
        spans=[{"tool_name": s.tool_name} for s in run.spans if s.span_type == SpanType.TOOL_CALL],
        total_latency_ms=run.total_latency_ms,
        estimated_cost_usd=run.estimated_cost_usd,
    )
    report = evaluate_suite(
        new_suite(name="s", version="1", cases=[case]),
        [EvaluationSample(case_id=case.id, output="Refund issued for order 7.", trace=trace)],
    )
    assert report.summary.passed_cases == 1


@pytest.mark.parametrize(
    ("run", "reason"),
    [
        (_run(task_success=False), "did not succeed"),
        (_run(status=RunStatus.FAILED, task_success=None), "did not succeed"),
        (_run(with_input=False), "no recorded input"),
    ],
)
def test_case_from_run_rejects_unusable_runs(run: Run, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        case_from_run(run)


def test_case_from_run_without_any_expectation() -> None:
    run = Run(
        run_id="bare",
        application_name="app",
        status=RunStatus.SUCCEEDED,
        metadata={"input": "hi"},
    )
    with pytest.raises(ValueError, match="no tool calls"):
        case_from_run(run)


def test_cases_from_runs_reports_skips_and_duplicates() -> None:
    result = cases_from_runs([_run("a"), _run("a"), _run("b", task_success=False)])
    assert [case.id for case in result.cases] == ["trace-a"]
    assert [(item.source_id, item.reason) for item in result.skipped] == [
        ("a", "duplicate run_id"),
        ("b", "run did not succeed; convert corrected feedback instead"),
    ]


def test_feedback_conversion_rules() -> None:
    positive = FeedbackRecord(feedback_id="f1", input="q", output="good", rating="positive")
    corrected = FeedbackRecord(
        feedback_id="f2",
        input="q2",
        output="bad",
        rating="negative",
        corrected_output="right",
        comment="wrong policy",
        tags=["escalation"],
        domain="billing",
    )
    by_score = FeedbackRecord(feedback_id="f3", input="q3", output="ok", score=0.9)
    first = case_from_feedback(positive)
    assert first.expected_output == "good"
    assert first.metadata["feedback_rating"] == "positive"
    second = case_from_feedback(corrected)
    assert second.expected_output == "right"
    assert second.metadata["rejected_output"] == "bad"
    assert second.metadata["feedback_comment"] == "wrong policy"
    assert second.metadata["domain"] == "billing"
    assert second.tags == ["from-feedback", "escalation"]
    assert case_from_feedback(by_score).expected_output == "ok"


def test_feedback_without_signal_is_invalid() -> None:
    with pytest.raises(ValueError, match="rating, score, or corrected_output"):
        FeedbackRecord(feedback_id="x", input="q")


def test_cases_from_feedback_fills_input_from_runs_and_skips() -> None:
    records = [
        FeedbackRecord(feedback_id="ok", run_id="run-1", output="fine", rating="positive"),
        FeedbackRecord(feedback_id="by-trace", trace_id="trace-of-run-1", output="y", score=0.7),
        FeedbackRecord(feedback_id="neg", input="q", output="bad", rating="negative"),
        FeedbackRecord(feedback_id="orphan", output="x", rating="positive"),
        FeedbackRecord(feedback_id="empty", input="q", rating="positive"),
        FeedbackRecord(feedback_id="low", input="q", output="x", score=0.2),
    ]
    result = cases_from_feedback(records, runs=[_run()])
    assert [case.id for case in result.cases] == ["feedback-ok", "feedback-by-trace"]
    assert result.cases[0].input == {"question": "Refund order 7"}
    assert result.cases[0].metadata["source"]["trace_id"] == "trace-of-run-1"
    assert result.cases[0].metadata["domain"] == "billing"
    reasons = {item.source_id: item.reason for item in result.skipped}
    assert "corrected_output" in reasons["neg"]
    assert "no input" in reasons["orphan"]
    assert "no output" in reasons["empty"]
    assert "corrected_output" in reasons["low"]


def test_load_feedback_formats(tmp_path: Path) -> None:
    record = {"feedback_id": "a", "input": "q", "output": "x", "rating": "positive"}
    (tmp_path / "f.json").write_text(json.dumps({"feedback": [record]}), "utf-8")
    (tmp_path / "f.jsonl").write_text(json.dumps(record) + "\n", "utf-8")
    (tmp_path / "f.yaml").write_text("- feedback_id: a\n  input: q\n  rating: positive\n", "utf-8")
    for name in ("f.json", "f.jsonl", "f.yaml"):
        assert load_feedback(tmp_path / name)[0].feedback_id == "a"
    (tmp_path / "dup.json").write_text(json.dumps([record, record]), "utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_feedback(tmp_path / "dup.json")
