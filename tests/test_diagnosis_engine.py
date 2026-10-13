"""Attribution, timelines, anomalies, guardrails, narratives, and report contracts."""

import itertools
import json
import time
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agenticlens.diagnosis import (
    AnalysisBudget,
    AnalysisGuard,
    DiagnosisReport,
    FailureCategory,
    detect_anomalies,
    diagnose_run,
    explain_recommendations,
    explain_run,
)
from agenticlens.models.trace import Run
from diagnosis_support import run, span

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "diagnosis"


def _cause_and_consequence() -> Run:
    return run(
        [
            span(
                "root",
                "ticket",
                "delegation",
                0,
                500,
                agent_name="router",
                attributes={"to_agent": "billing"},
            ),
            span(
                "t",
                "fetch_invoice",
                "tool_call",
                10,
                status="failed",
                parent_span_id="root",
                agent_name="billing",
                error_type="TimeoutError",
            ),
            span("r", "retry", "retry", 30, status="failed", parent_span_id="t"),
            span(
                "f",
                "answer",
                "final_response",
                60,
                status="failed",
                parent_span_id="root",
                agent_name="writer",
                error_type="MissingData",
            ),
        ],
        failed=True,
        task_success=False,
    )


# -- attribution ---------------------------------------------------------------


def test_attribution_prefers_the_earliest_unrecovered_cause() -> None:
    attribution = diagnose_run(_cause_and_consequence()).attribution
    assert attribution.status == "attributed"
    assert attribution.faulty_span_id == "t"
    assert attribution.faulty_agent == "billing"
    assert attribution.category is FailureCategory.TIMEOUT
    assert [c.span_id for c in attribution.candidates] == ["t", "f"]
    assert sum(c.score for c in attribution.candidates) == pytest.approx(1.0, abs=1e-5)
    assert sum(attribution.agent_scores.values()) == pytest.approx(1.0, abs=1e-5)
    assert 0 < attribution.confidence < 1
    assert "Next candidate: 'answer'" in attribution.explanation


def test_agent_is_inherited_from_ancestor() -> None:
    trace = run(
        [
            span("a", "agent", "custom", 0, 100, agent_name="worker"),
            span("t", "tool", "tool_call", 10, status="failed", parent_span_id="a"),
        ],
        failed=True,
    )
    assert diagnose_run(trace).attribution.faulty_agent == "worker"


def test_recovered_failures_give_recovered_status() -> None:
    trace = run(
        [
            span("a", "fetch", "tool_call", 0, status="failed"),
            span("r", "retry", "retry", 20, parent_span_id="a"),
        ],
        task_success=True,
    )
    attribution = diagnose_run(trace).attribution
    assert attribution.status == "recovered"
    assert attribution.faulty_span_id == "a"


def test_no_failure_and_unattributed_statuses() -> None:
    assert diagnose_run(run([span("a", "ok", "model_call", 0)])).attribution.status == (
        "no_failure"
    )
    empty_failed = diagnose_run(run([], failed=True))
    assert empty_failed.attribution.status == "unattributed"
    assert empty_failed.diagnoses[0].category is FailureCategory.INCOMPLETE_TASK


# -- timeline ------------------------------------------------------------------


def test_timeline_orders_events_and_marks_root_cause() -> None:
    timeline = diagnose_run(_cause_and_consequence()).timeline
    kinds = [event.kind for event in timeline.events]
    assert kinds[0] == "run_started" and kinds[-1] == "run_completed"
    offsets = [event.offset_ms for event in timeline.events]
    assert offsets == sorted(offsets)
    roots = [event for event in timeline.events if event.is_root_cause]
    assert [event.span_id for event in roots] == ["t"]
    assert roots[0].kind == "span_failed"
    assert timeline.first_failure_offset_ms == 20.0
    assert "retry" in kinds and "handoff" in kinds


def test_timeline_records_recovery_and_fault_injection() -> None:
    trace = run(
        [
            span(
                "k",
                "kb",
                "retrieval",
                0,
                attributes={"chaos.injected": True, "chaos.fault_type": "latency"},
            ),
            span("a", "fetch", "tool_call", 20, status="failed"),
            span("b", "fetch", "tool_call", 40),
        ]
    )
    timeline = diagnose_run(trace).timeline
    kinds = [event.kind for event in timeline.events]
    assert "fault_injected" in kinds and "recovered" in kinds
    assert timeline.recovered_span_ids == ["b"]


def test_timeline_truncates_routine_events_first() -> None:
    from agenticlens.diagnosis.guardrails import AnalysisGuard as Guard
    from agenticlens.diagnosis.timeline import build_timeline
    from agenticlens.diagnosis.view import TraceView

    trace = run(
        [span(f"s{i}", "step", "model_call", i) for i in range(10)]
        + [span("bad", "x", "tool_call", 20, status="failed")],
        failed=True,
    )
    report = diagnose_run(trace)
    timeline = build_timeline(TraceView(trace, Guard()), report.attribution, max_events=5)
    assert timeline.truncated
    assert all(event.kind != "span_started" for event in timeline.events)
    assert any(event.kind == "span_failed" for event in timeline.events)


# -- anomalies -----------------------------------------------------------------


def _latency_run(run_id: str, latency: float, tokens: int = 100) -> Run:
    return run(
        [span(f"{run_id}-t", "fetch", "tool_call", 0, latency, input_tokens=tokens)],
        run_id=run_id,
        duration=latency + 10,
    )


def test_anomaly_detection_flags_latency_spikes() -> None:
    baseline = [_latency_run(f"b{i}", 100 + i * 3) for i in range(6)]
    report = detect_anomalies(_latency_run("x", 900), baseline)
    keys = {(a.scope, a.key, a.metric) for a in report.anomalies}
    assert ("span", "tool_call:fetch", "latency_ms") in keys
    assert ("run", "run", "latency_ms") in keys
    spike = next(a for a in report.anomalies if a.key == "tool_call:fetch")
    assert spike.direction == "high" and spike.robust_z and spike.robust_z > 3.5
    assert spike.span_ids == ["x-t"]
    # constant tokens: a small change stays within tolerance
    assert not any(a.metric == "total_tokens" for a in report.anomalies)


def test_anomaly_constant_baseline_uses_tolerance() -> None:
    baseline = [_latency_run(f"b{i}", 100) for i in range(5)]
    within = detect_anomalies(_latency_run("x", 120), baseline)
    beyond = detect_anomalies(_latency_run("y", 200), baseline)
    assert not [a for a in within.anomalies if a.key == "tool_call:fetch"]
    flagged = [a for a in beyond.anomalies if a.key == "tool_call:fetch"]
    assert flagged and flagged[0].robust_z is None


def test_anomaly_mean_absolute_deviation_fallback() -> None:
    # More than half identical -> MAD 0, but MeanAD > 0.
    baseline = [_latency_run(f"b{i}", v) for i, v in enumerate([100, 100, 100, 100, 160])]
    report = detect_anomalies(_latency_run("x", 400), baseline)
    spike = next(a for a in report.anomalies if a.key == "tool_call:fetch")
    assert spike.baseline_mad == 0 and spike.robust_z is not None


def test_anomaly_requires_enough_baseline_runs() -> None:
    report = detect_anomalies(_latency_run("x", 900), [_latency_run("b", 100)])
    assert report.anomalies == [] and report.warnings
    with pytest.raises(ValueError):
        detect_anomalies(_latency_run("x", 1), [], threshold=0)
    with pytest.raises(ValueError):
        detect_anomalies(_latency_run("x", 1), [], min_baseline_samples=1)
    with pytest.raises(ValueError):
        detect_anomalies(_latency_run("x", 1), [], constant_tolerance=-1)


def test_diagnose_run_attaches_anomalies_only_with_baseline() -> None:
    baseline = [_latency_run(f"b{i}", 100 + i) for i in range(5)]
    assert diagnose_run(_latency_run("x", 900)).anomalies is None
    assert diagnose_run(_latency_run("x", 900), baseline=baseline).anomalies is not None


# -- guardrails ----------------------------------------------------------------


def test_span_and_depth_limits_truncate_analysis() -> None:
    spans = [span("s0", "root", "custom", 0, 100)]
    for i in range(1, 5):
        spans.append(span(f"s{i}", "child", "custom", i, 50, parent_span_id=f"s{i - 1}"))
    spans.append(span("deep", "fail", "tool_call", 10, status="failed", parent_span_id="s4"))
    report = diagnose_run(run(spans, failed=True), budget=AnalysisBudget(max_depth=2))
    assert report.guardrails.truncated
    assert report.guardrails.max_depth_seen == 5
    assert all("deep" not in d.span_ids for d in report.diagnoses)

    capped = diagnose_run(run(spans), budget=AnalysisBudget(max_spans=2))
    assert capped.guardrails.spans_analyzed == 2 and capped.guardrails.spans_total == 6


def test_diagnosis_limit() -> None:
    spans = [
        span(f"t{i}", f"tool{i}", "tool_call", i, status="failed", tool_name=f"x{i}")
        for i in range(5)
    ]
    report = diagnose_run(run(spans, failed=True), budget=AnalysisBudget(max_diagnoses=2))
    assert len(report.diagnoses) == 2
    assert any("diagnosis limit" in reason for reason in report.guardrails.stop_reasons)


def test_guard_detects_stagnation_iterations_and_cost() -> None:
    guard = AnalysisGuard(AnalysisBudget(stagnation_limit=2))
    assert guard.record(["a"]) is True
    assert guard.record(["a"]) is False
    assert not guard.exhausted
    guard.record([])
    assert guard.exhausted and "stagnation" in guard.stop_reasons[0]

    iterations = AnalysisGuard(AnalysisBudget(max_iterations=2, stagnation_limit=None))
    iterations.record(["x"])
    iterations.record(["y"])
    assert iterations.exhausted

    spend = AnalysisGuard(AnalysisBudget(max_cost_usd=0.5))
    spend.charge(cost_usd=0.2)
    assert not spend.exhausted
    spend.charge(cost_usd=0.3)
    assert spend.exhausted and spend.status().cost_usd == pytest.approx(0.5)


def test_guard_time_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = itertools.chain([0.0], itertools.repeat(10.0))
    monkeypatch.setattr(time, "perf_counter", lambda: next(clock))
    guard = AnalysisGuard(AnalysisBudget(max_seconds=1))
    assert guard.exhausted and guard.out_of_time
    assert "time limit" in guard.stop_reasons[0]


# -- report contract and narratives --------------------------------------------


def test_reports_are_reproducible() -> None:
    first = diagnose_run(_cause_and_consequence()).model_dump_json()
    second = diagnose_run(_cause_and_consequence()).model_dump_json()
    assert first == second


def test_published_schema_matches_model_and_validates_report() -> None:
    published = json.loads((SCHEMAS / "diagnosis-report.schema.json").read_text("utf-8"))
    generated = DiagnosisReport.model_json_schema()
    Draft202012Validator.check_schema(published)
    assert published["$defs"] == generated["$defs"]
    assert published["properties"] == generated["properties"]
    report = json.loads(diagnose_run(_cause_and_consequence()).model_dump_json())
    Draft202012Validator(published).validate(report)


def test_summary_counts_wasted_spend() -> None:
    summary = diagnose_run(_cause_and_consequence()).summary
    assert summary.failed_spans == 3
    assert summary.unrecovered == 3
    assert summary.highest_severity == "high"
    assert summary.categories == {"timeout": 1, "retry_exhausted": 1, "model_error": 1}
    assert summary.wasted_cost_usd is None  # spans carry no cost


def test_explain_run_narrative_sections() -> None:
    narrative = explain_run(diagnose_run(_cause_and_consequence()))
    for heading in (
        "## Verdict",
        "## Root cause",
        "## Contributing factors",
        "## What happened",
        "## Next steps",
        "## Limitations",
    ):
        assert heading in narrative
    assert "fetch_invoice" in narrative and "**(root cause)**" in narrative
    assert "No failures" in explain_run(diagnose_run(run([span("a", "ok", "model_call", 0)])))


def test_explain_recommendations_gives_root_causes() -> None:
    from datetime import datetime, timezone

    from agenticlens.models.recommendation import Recommendation
    from agenticlens.models.workflow import Workflow

    workflow = Workflow(name="wf", start_time=datetime(2026, 1, 1, tzinfo=timezone.utc))
    rec = Recommendation(
        title="Cache tool results",
        description="search called twice with identical arguments",
        optimization_type="tool_result_caching",
        step_name="search",
        tokens_saved=120,
        quality_risk="Stale results if the source changes.",
    )
    narrative = explain_recommendations(workflow, [rec])
    assert "**Why:** The same tool was called" in narrative
    assert "step 'search'" in narrative and "120 tokens" in narrative
    assert "No optimization recommendations" in explain_recommendations(workflow, [])
