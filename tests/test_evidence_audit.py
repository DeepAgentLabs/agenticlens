from datetime import datetime, timedelta, timezone

from agenticlens.evaluation import (
    BUILTIN_EVALUATOR,
    EvalTrace,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    Score,
    audit_report,
    evaluate_suite,
    render_html_report,
    to_eval_trace,
)
from agenticlens.evaluation import TestCase as EvalCase
from agenticlens.evaluation import TestSuite as EvalSuite
from agenticlens.evaluation._trace_adapter import to_eval_trace_dict
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def _run(*, cost: float | None = 0.002, metadata: dict[str, str] | None = None) -> Run:
    started = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return Run(
        application_name="audit-demo",
        started_at=started,
        completed_at=started + timedelta(milliseconds=50),
        status=RunStatus.SUCCEEDED,
        metadata=metadata or {},
        spans=[
            Span(
                name="answer",
                span_type=SpanType.MODEL_CALL,
                status=RunStatus.SUCCEEDED,
                estimated_cost_usd=cost,
            )
        ],
    )


def _judge_registry(version: str | None) -> EvaluatorRegistry:
    registry = EvaluatorRegistry()
    registry.register(
        LLMJudgeEvaluator(
            "judge",
            lambda context: Score(name="quality", value=0.9, passed=True, explanation="fine"),
            version=version,
        )
    )
    return registry


def _suite(*case_ids: str, judged: bool = False) -> EvalSuite:
    return EvalSuite(
        name="audit",
        version="1",
        cases=[
            EvalCase(
                id=case_id,
                name=case_id,
                expected_output="ok",
                evaluators=[EvaluatorConfig(name="judge", threshold=0.5)] if judged else [],
            )
            for case_id in case_ids
        ],
    )


def test_agenticlens_run_cost_is_estimated_unless_declared_measured() -> None:
    assert to_eval_trace(_run()).cost_source == "estimated"
    assert to_eval_trace(_run(metadata={"cost_source": "measured"})).cost_source == "measured"
    assert to_eval_trace(_run(cost=None)).cost_source is None


def test_run_shaped_payload_carries_declared_cost_source() -> None:
    payload = _run(metadata={"cost_source": "measured"}).model_dump(mode="json")
    assert to_eval_trace_dict(payload)["cost_source"] == "measured"
    payload["metadata"] = {}
    assert to_eval_trace_dict(payload)["cost_source"] == "estimated"


def test_clean_report_passes_audit() -> None:
    sample = EvaluationSample(case_id="a", output="ok", trace=to_eval_trace(_run()))
    report = evaluate_suite(_suite("a", judged=True), [sample], registry=_judge_registry("judge@1"))

    audit = audit_report(report)

    assert audit.passed
    assert audit.evaluators == {
        BUILTIN_EVALUATOR: [audit.evaluators[BUILTIN_EVALUATOR][0]],
        "judge": ["judge@1"],
    }
    assert audit.cost.complete and audit.cost.sources == {"estimated": 1}
    assert audit.issues == []


def test_unversioned_judge_blocks_by_default_but_can_be_relaxed() -> None:
    sample = EvaluationSample(case_id="a", output="ok", trace=to_eval_trace(_run()))
    report = evaluate_suite(_suite("a", judged=True), [sample], registry=_judge_registry(None))

    strict = audit_report(report)
    relaxed = audit_report(report, require_evaluator_versions=False)

    assert not strict.passed
    assert [issue.kind for issue in strict.issues] == ["unversioned_evaluator"]
    assert strict.evaluators["judge"] == ["unversioned"]
    assert relaxed.passed
    assert relaxed.issues[0].blocking is False


def test_failed_cases_without_trace_evidence_always_block() -> None:
    traced = EvaluationSample(case_id="a", output="bad", trace=to_eval_trace(_run()))
    untraced = EvaluationSample(case_id="b", output="bad", trace=EvalTrace(trace_id=""))
    report = evaluate_suite(_suite("a", "b", "c"), [traced, untraced])

    audit = audit_report(report, require_evaluator_versions=False)

    assert not audit.passed
    assert audit.failed_cases == 3
    assert audit.failed_cases_with_trace == 1
    kinds = {issue.kind: issue.case_id for issue in audit.issues if issue.blocking}
    assert kinds == {"missing_trace_id": "b", "missing_sample": "c"}


def test_cost_gaps_are_reported_and_optionally_blocking() -> None:
    samples = [
        EvaluationSample(
            case_id="a",
            output="ok",
            trace=EvalTrace(trace_id="t-a", estimated_cost_usd=0.01),
        ),
        EvaluationSample(case_id="b", output="ok", trace=EvalTrace(trace_id="t-b")),
    ]
    report = evaluate_suite(_suite("a", "b"), samples)

    lenient = audit_report(report)
    strict = audit_report(report, require_complete_cost=True, require_cost_source=True)

    assert lenient.passed
    assert {issue.kind for issue in lenient.issues} == {
        "incomplete_cost",
        "unspecified_cost_source",
    }
    assert lenient.cost.priced_cases == 1 and not lenient.cost.complete
    assert not strict.passed


def test_html_report_shows_versions_cost_source_and_missing_samples() -> None:
    sample = EvaluationSample(case_id="a", output="ok", trace=to_eval_trace(_run()))
    report = evaluate_suite(
        _suite("a", "b", judged=True), [sample], registry=_judge_registry("judge@1")
    )

    html = render_html_report(report)

    assert "judge@judge@1" in html
    assert "(estimated)" in html
    assert "no sample supplied" in html
    assert "1/2 priced" in html


def test_judge_without_registry_version_reads_as_unversioned_in_html() -> None:
    def judge(context: EvaluationContext) -> Score:
        return Score(name="quality", value=0.2, passed=False, explanation="weak")

    registry = EvaluatorRegistry()
    registry.register(LLMJudgeEvaluator("judge", judge))
    sample = EvaluationSample(case_id="a", output="ok", trace=to_eval_trace(_run()))

    html = render_html_report(evaluate_suite(_suite("a", judged=True), [sample], registry=registry))

    assert "judge@unversioned" in html


def test_eval_trace_payload_without_latency_keeps_its_cost() -> None:
    payload = {"trace_id": "t", "estimated_cost_usd": 0.01, "cost_source": "measured"}
    assert to_eval_trace_dict(payload) is payload
    run_like = {"trace_id": "t", "spans": [{"span_type": "tool_call", "estimated_cost_usd": 0.2}]}
    assert to_eval_trace_dict(run_like)["estimated_cost_usd"] == 0.2


def test_html_status_reports_case_outcome_not_a_release_decision() -> None:
    sample = EvaluationSample(case_id="a", output="bad", trace=to_eval_trace(_run()))
    html = render_html_report(evaluate_suite(_suite("a", "b"), [sample]))
    assert "CASE RESULT · 2 CASES FAILED" in html
    assert "RELEASE STATUS" not in html and "READY" not in html
