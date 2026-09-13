from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.comparison.models import (
    ComparisonReport,
    MetricDelta,
    MetricSummary,
    RunGroupSummary,
)
from agenticlens.evaluation import EvaluationReport, GateConfig, evaluate_gate
from agenticlens.evaluation.models import CaseEvaluation, EvaluationSummary, Score
from agenticlens.models import Metrics, Step, StepType, Workflow
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.trace import Run, RunStatus, Span, SpanType
from agenticlens.reports import render_dashboard_html, render_history_html, save_dashboard_html


def _run() -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        application_name="support-triage-v3",
        started_at=started,
        completed_at=started + timedelta(milliseconds=500),
        status=RunStatus.SUCCEEDED,
        task_success=True,
        spans=[
            Span(
                span_id="planner",
                name="Classify intent",
                span_type=SpanType.PLANNING,
                agent_name="planner",
                started_at=started,
                latency_ms=200,
                input_tokens=400,
                output_tokens=100,
                estimated_cost_usd=0.002,
                status=RunStatus.SUCCEEDED,
            ),
            Span(
                span_id="draft",
                name="Draft answer",
                span_type=SpanType.MODEL_CALL,
                agent_name="drafter",
                started_at=started + timedelta(milliseconds=200),
                latency_ms=300,
                input_tokens=1800,
                output_tokens=300,
                estimated_cost_usd=0.009,
                status=RunStatus.SUCCEEDED,
            ),
        ],
    )


def _workflow() -> Workflow:
    workflow = Workflow(name="Support Workflow", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="Draft answer",
            type=StepType.LLM_CALL,
            metrics=Metrics(
                prompt_tokens=1800, completion_tokens=300, total_tokens=2100, cost=0.009
            ),
        )
    )
    return workflow


def _recommendations() -> list[Recommendation]:
    return [
        Recommendation(
            title="Repeated system prompt",
            description="The same system prompt is sent on every call.",
            severity=Severity.WARNING,
            tokens_saved=680,
            estimated_usd_savings=0.0029,
        ),
        Recommendation(
            title="Model-tier mismatch",
            description="A cheaper model matches recorded quality.",
            severity=Severity.INFO,
            cost_savings=0.0116,
        ),
    ]


def _evaluation(*, failed: bool = False) -> EvaluationReport:
    return EvaluationReport(
        suite_name="support-suite",
        suite_version="1",
        summary=EvaluationSummary(
            total_cases=2,
            passed_cases=1 if failed else 2,
            failed_cases=1 if failed else 0,
            pass_rate=0.5 if failed else 1.0,
            average_score=0.7 if failed else 0.95,
            total_cost_usd=0.018,
            average_latency_ms=4820,
        ),
        cases=[
            CaseEvaluation(
                case_id="case-1",
                case_name="Case one",
                passed=True,
                scores=[Score(name="answer_quality", value=0.95, passed=True, explanation="Good.")],
                output="ok",
                trace_id="trace-1",
                latency_ms=4820,
                cost_usd=0.018,
            )
        ],
    )


def _comparison() -> ComparisonReport:
    metric = MetricSummary(count=25, mean=10.0, median=10.0, p95=12.0, standard_deviation=1.0)
    baseline = RunGroupSummary(
        label="baseline", run_count=25, success_rate=0.94, tokens=metric, latency_ms=metric
    )
    candidate = RunGroupSummary(
        label="candidate", run_count=25, success_rate=0.93, tokens=metric, latency_ms=metric
    )
    return ComparisonReport(
        baseline=baseline,
        candidate=candidate,
        success_rate_delta=MetricDelta(absolute=-0.01, relative=-0.011, regressed=False),
        mean_tokens_delta=MetricDelta(absolute=-370.0, relative=-0.11, regressed=False),
        mean_latency_ms_delta=MetricDelta(absolute=-1060.0, relative=-0.22, regressed=True),
        regression_threshold=0.05,
        regressions=["mean_latency_ms"],
    )


def test_render_requires_at_least_one_artifact() -> None:
    with pytest.raises(ValueError):
        render_dashboard_html()


def test_extra_header_html_renders_when_given_and_absent_by_default() -> None:
    without = render_dashboard_html(run=_run())
    assert "live-nav-marker" not in without

    with_header = render_dashboard_html(
        run=_run(), extra_header_html='<div id="live-nav-marker">nav</div>'
    )
    assert "live-nav-marker" in with_header


def test_timeline_renders_spans_and_escapes_names() -> None:
    run = _run()
    run.spans[0].name = "<script>alert(1)</script>"

    html = render_dashboard_html(run=run)

    assert "Agent timeline" in html
    assert "Draft answer" in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_cost_breakdown_and_findings_render_from_workflow() -> None:
    html = render_dashboard_html(workflow=_workflow(), recommendations=_recommendations())

    assert "Cost by workflow area" in html
    assert "Waste findings" in html
    assert "Repeated system prompt" in html
    assert "Model-tier mismatch" in html
    assert "680 tok/run" in html


def test_gate_panel_shows_verdict_when_gate_given() -> None:
    evaluation = _evaluation(failed=True)
    gate = evaluate_gate(evaluation, GateConfig(min_pass_rate=1.0))

    html = render_dashboard_html(evaluation=evaluation, gate=gate)

    assert "Release gate" in html
    assert "FAIL" in html
    assert "Pass rate" in html  # from GateDecision.reasons text


def test_gate_panel_notes_missing_gate_configuration() -> None:
    html = render_dashboard_html(evaluation=_evaluation())

    assert "No release gate configured" in html


def test_comparison_panel_labels_regressed_and_clean_metrics() -> None:
    html = render_dashboard_html(comparison=_comparison())

    assert "Baseline vs. candidate" in html
    assert "Regression" in html
    assert "No regression" in html


def test_save_dashboard_html_writes_file(tmp_path) -> None:
    out = tmp_path / "dashboard.html"

    save_dashboard_html(out, run=_run())

    assert out.exists()
    assert "Agent timeline" in out.read_text(encoding="utf-8")


def _priced_run(trace_id: str, application_name: str, *, cost: float | None) -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        trace_id=trace_id,
        application_name=application_name,
        started_at=started,
        completed_at=started + timedelta(milliseconds=100),
        status=RunStatus.SUCCEEDED,
        spans=[
            Span(
                name="call",
                span_type=SpanType.MODEL_CALL,
                started_at=started,
                latency_ms=100,
                input_tokens=10,
                output_tokens=5,
                estimated_cost_usd=cost,
            )
        ],
    )


def test_render_history_html_renders_placeholder_for_empty_list() -> None:
    html = render_history_html([])

    assert "No traces recorded yet" in html


def test_render_history_html_renders_aggregate_stats_and_rows() -> None:
    runs = [
        _priced_run("trace-1", "support-bot", cost=0.01),
        _priced_run("trace-2", "billing-bot", cost=0.02),
    ]

    html = render_history_html(runs)

    assert "Total traces" in html
    assert "support-bot" in html
    assert "billing-bot" in html
    assert "P95 latency" in html


def test_render_history_html_notes_partial_pricing() -> None:
    runs = [
        _priced_run("trace-1", "support-bot", cost=0.01),
        _priced_run("trace-2", "billing-bot", cost=None),
    ]

    html = render_history_html(runs)

    assert "1 of 2 traces priced" in html


def test_render_history_html_links_trace_ids_only_when_base_given() -> None:
    runs = [_priced_run("trace-1", "support-bot", cost=0.01)]

    without_link = render_history_html(runs)
    with_link = render_history_html(runs, trace_link_base="/?trace_id=")

    assert '<a href="/?trace_id=trace-1"' not in without_link
    assert '<a href="/?trace_id=trace-1"' in with_link
