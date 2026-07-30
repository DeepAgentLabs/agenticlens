from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.evaluation import (
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    GateConfig,
    LLMJudgeEvaluator,
    Score,
    evaluate_gate,
    evaluate_suite,
    render_html_report,
)
from agenticlens.evaluation import (
    TestCase as EvaluationTestCase,
)
from agenticlens.evaluation import (
    TestSuite as EvaluationTestSuite,
)
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def make_run(*, latency_ms: float = 100, cost: float | None = 0.002) -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        application_name="test-agent",
        started_at=started,
        completed_at=started + timedelta(milliseconds=latency_ms),
        status=RunStatus.SUCCEEDED,
        spans=[
            Span(
                name="calculator",
                span_type=SpanType.TOOL_CALL,
                tool_name="add",
                status=RunStatus.SUCCEEDED,
                estimated_cost_usd=cost,
            )
        ],
    )


def test_evaluate_suite_scores_output_tools_latency_and_cost() -> None:
    suite = EvaluationTestSuite(
        name="release",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="answer",
                expected_contains=["42"],
                required_tools=["add"],
                forbidden_tools=["network"],
                max_latency_ms=200,
                max_cost_usd=0.01,
            )
        ],
    )
    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="The answer is 42.", trace=make_run())],
    )
    assert report.summary.pass_rate == 1
    assert report.summary.average_score == 1
    assert report.summary.total_cost_usd == 0.002


def test_missing_sample_fails_evaluation_and_gate() -> None:
    suite = EvaluationTestSuite(
        name="release",
        version="1",
        cases=[EvaluationTestCase(id="missing", name="missing", expected_output="ok")],
    )
    report = evaluate_suite(suite, [])
    decision = evaluate_gate(report, GateConfig())
    assert report.summary.failed_cases == 1
    assert not decision.passed
    assert len(decision.reasons) == 3


def test_gate_checks_operational_thresholds() -> None:
    suite = EvaluationTestSuite(
        name="release",
        version="1",
        cases=[EvaluationTestCase(id="case-1", name="answer", expected_output="ok")],
    )
    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="ok", trace=make_run())],
    )
    decision = evaluate_gate(
        report,
        GateConfig(max_average_latency_ms=50, max_total_cost_usd=0.001),
    )
    assert not decision.passed
    assert len(decision.reasons) == 2


def test_html_report_escapes_untrusted_content() -> None:
    suite = EvaluationTestSuite(
        name="<Release>",
        version="1",
        cases=[EvaluationTestCase(id="case-1", name="<script>", expected_contains=["safe"])],
    )
    report = evaluate_suite(
        suite,
        [
            EvaluationSample(
                case_id="case-1",
                output="<script>alert(1)</script> safe",
                trace=make_run(),
            )
        ],
    )
    html = render_html_report(report)
    assert "&lt;Release&gt;" in html
    assert "<script>alert(1)</script>" not in html


def test_registered_llm_judge_uses_suite_threshold() -> None:
    def judge(context: EvaluationContext) -> Score:
        assert context.config.config["rubric"] == "Correct and concise"
        return Score(
            name="answer_quality",
            value=0.85,
            passed=False,
            explanation="The response is correct and concise.",
        )

    registry = EvaluatorRegistry()
    registry.register(LLMJudgeEvaluator("quality_judge", judge))
    suite = EvaluationTestSuite(
        name="judge-suite",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Judge answer quality",
                evaluators=[
                    EvaluatorConfig(
                        name="quality_judge",
                        threshold=0.8,
                        config={"rubric": "Correct and concise"},
                    )
                ],
            )
        ],
    )
    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="42", trace=make_run())],
        registry=registry,
    )

    assert report.cases[0].passed
    assert report.cases[0].scores[0].evaluator_type == "llm_judge"
    assert report.cases[0].scores[0].value == 0.85


def test_unregistered_evaluator_is_rejected() -> None:
    suite = EvaluationTestSuite(
        name="custom",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Custom",
                evaluators=[EvaluatorConfig(name="missing")],
            )
        ],
    )

    with pytest.raises(ValueError, match="no evaluator registry"):
        evaluate_suite(
            suite,
            [EvaluationSample(case_id="case-1", output="ok", trace=make_run())],
        )
