from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.evaluation import (
    BusinessRuleEvaluator,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    GateConfig,
    LLMJudgeEvaluator,
    PythonTarget,
    Score,
    evaluate_gate,
    evaluate_suite,
    render_html_report,
    run_live_suite,
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


def test_evaluate_suite_supports_json_fields_tool_args_and_turn_thresholds() -> None:
    suite = EvaluationTestSuite(
        name="structured",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Structured output",
                output_json_schema={
                    "type": "object",
                    "required": ["answer", "meta"],
                    "properties": {
                        "answer": {"type": "string"},
                        "meta": {"type": "object", "required": ["confidence"]},
                    },
                },
                required_output_fields=["meta.confidence"],
                required_tool_arguments={"add": ["a", "b"]},
                max_turns=2,
            )
        ],
    )
    run = make_run()
    run.metadata["turn_count"] = 2
    run.spans[0].attributes["tool_args"] = {"a": 40, "b": 2}

    report = evaluate_suite(
        suite,
        [
            EvaluationSample(
                case_id="case-1",
                output='{"answer":"42","meta":{"confidence":0.9}}',
                trace=run,
            )
        ],
    )
    assert report.cases[0].passed
    assert {score.name for score in report.cases[0].scores} >= {
        "json_schema",
        "required_field:meta.confidence",
        "tool_args:add",
        "turn_count_threshold",
    }


def test_evaluate_suite_supports_nullable_json_schema_types() -> None:
    suite = EvaluationTestSuite(
        name="schema",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Nullable field",
                output_json_schema={
                    "type": "object",
                    "required": ["answer", "reasoning"],
                    "properties": {
                        "answer": {"type": "string"},
                        "reasoning": {"type": ["string", "null"]},
                    },
                },
            )
        ],
    )

    report = evaluate_suite(
        suite,
        [
            EvaluationSample(
                case_id="case-1",
                output='{"answer":"42","reasoning":null}',
                trace=make_run(),
            )
        ],
    )

    assert report.cases[0].passed
    assert report.cases[0].scores[0].name == "json_schema"
    assert report.cases[0].scores[0].passed


def test_max_turns_requires_explicit_turn_count_metadata() -> None:
    suite = EvaluationTestSuite(
        name="turns",
        version="1",
        cases=[EvaluationTestCase(id="case-1", name="Turn gate", max_turns=1)],
    )

    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="ok", trace=make_run())],
    )

    assert not report.cases[0].passed
    assert report.cases[0].scores[0].name == "turn_count_threshold"
    assert report.cases[0].scores[0].explanation == (
        "Trace metadata is missing a positive integer turn_count, "
        "so the max_turns check could not be evaluated."
    )


def test_business_rule_evaluator_uses_business_rule_type() -> None:
    registry = EvaluatorRegistry()
    registry.register(
        BusinessRuleEvaluator(
            "business_rule",
            lambda context: Score(
                name="vip_rule",
                value=1.0 if context.sample.output == "vip" else 0.0,
                passed=False,
                explanation="VIP response requirement.",
            ),
        )
    )
    suite = EvaluationTestSuite(
        name="business",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="VIP policy",
                evaluators=[EvaluatorConfig(name="business_rule")],
            )
        ],
    )
    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="vip", trace=make_run())],
        registry=registry,
    )
    assert report.cases[0].scores[0].evaluator_type == "business_rule"


def test_run_live_suite_executes_python_target() -> None:
    suite = EvaluationTestSuite(
        name="live",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Answer",
                input={"response": '{"answer":"42","meta":{"confidence":0.9}}'},
                output_json_schema={"type": "object", "required": ["answer"]},
                required_tool_arguments={"add": ["a", "b"]},
                max_turns=1,
            )
        ],
    )
    report = run_live_suite(
        suite,
        PythonTarget(callable_path="tests/live_eval_target.py:run_case"),
    )
    assert report.summary.pass_rate == 1.0


def test_run_live_suite_preserves_suite_case_id_when_target_returns_one(tmp_path) -> None:
    target_file = tmp_path / "target.py"
    target_file.write_text(
        "\n".join(
            [
                "from datetime import datetime, timezone",
                "",
                "def run_case(payload, *, case):",
                "    return {",
                "        'case_id': 'wrong-case',",
                "        'output': 'ok',",
                "        'trace': {",
                "            'application_name': 'live-target',",
                "            'started_at': datetime.now(timezone.utc).isoformat(),",
                "            'completed_at': datetime.now(timezone.utc).isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': True,",
                "            'spans': [],",
                "        },",
                "    }",
            ]
        ),
        encoding="utf-8",
    )
    suite = EvaluationTestSuite(
        name="live",
        version="1",
        cases=[EvaluationTestCase(id="case-1", name="Answer", expected_output="ok")],
    )

    report = run_live_suite(
        suite,
        PythonTarget(callable_path=f"{target_file}:run_case"),
    )

    assert report.cases[0].case_id == "case-1"


def test_json_schema_supports_null_type() -> None:
    suite = EvaluationTestSuite(
        name="schema",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Null type",
                output_json_schema={"type": "null"},
            )
        ],
    )
    report = evaluate_suite(
        suite,
        [EvaluationSample(case_id="case-1", output="null", trace=make_run())],
    )

    assert report.cases[0].passed
    assert report.cases[0].scores[0].explanation == (
        "Output matches the configured JSON schema subset."
    )
