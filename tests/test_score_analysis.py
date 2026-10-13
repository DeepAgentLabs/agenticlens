"""Deterministic vs model-based scores, judge cost, disagreement, and judge usage."""

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from agenticlens.evaluation import (
    EvalTrace,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    JudgeUsage,
    JudgeVerdict,
    LLMJudgeEvaluator,
    Score,
    ScoreAnalysis,
    analyze_scores,
    evaluate_suite,
    prompt_fingerprint,
    render_html_report,
    score_kind,
    structured_judge,
)
from agenticlens.evaluation import (
    TestCase as EvalCase,
)
from agenticlens.evaluation import (
    TestSuite as EvalSuite,
)

ROOT = Path(__file__).resolve().parents[1]


def _suite(*judges: str) -> EvalSuite:
    return EvalSuite(
        name="s",
        version="1",
        cases=[
            EvalCase(
                id=case_id,
                name=case_id,
                expected_contains=["refund"],
                evaluators=[EvaluatorConfig(name=judge, threshold=0.5) for judge in judges],
            )
            for case_id in ("a", "b", "c")
        ],
    )


def _samples(outputs: dict[str, str]) -> list[EvaluationSample]:
    return [
        EvaluationSample(case_id=case_id, output=output, trace=EvalTrace(trace_id=case_id))
        for case_id, output in outputs.items()
    ]


def _verdicts(mapping: dict[str, str], usage: JudgeUsage | None = None) -> Any:
    def judge(context: EvaluationContext) -> JudgeVerdict:
        return JudgeVerdict(
            verdict=mapping[context.case.id],  # type: ignore[arg-type]
            confidence=0.9,
            usage=usage,
        )

    return judge


def test_score_kind() -> None:
    def score(evaluator_type: str, **metadata: Any) -> Score:
        return Score(
            name="x",
            value=1,
            passed=True,
            explanation="",
            evaluator_type=evaluator_type,
            metadata=metadata,
        )

    assert score_kind(score("llm_judge")) == "model_based"
    assert score_kind(score("llm_rubric")) == "model_based"
    assert score_kind(score("custom", judge_model="m")) == "model_based"
    assert score_kind(score("deterministic")) == "deterministic"
    assert score_kind(score("trace_rule")) == "deterministic"


def test_kinds_judge_cost_and_disagreement() -> None:
    registry = EvaluatorRegistry()
    usage = JudgeUsage(cost_usd=0.002, cost_source="measured", input_tokens=500, output_tokens=50)
    registry.register(
        structured_judge(
            "judge_a",
            _verdicts({"a": "agree", "b": "agree", "c": "disagree"}, usage),
            judge_model="m1",
            version="1",
        )
    )
    registry.register(
        structured_judge(
            "judge_b",
            _verdicts({"a": "agree", "b": "disagree", "c": "disagree"}),
            judge_model="m2",
            version="1",
        )
    )
    report = evaluate_suite(
        _suite("judge_a", "judge_b"),
        _samples({"a": "refund issued", "b": "no idea", "c": "refund later"}),
        registry=registry,
    )
    analysis = analyze_scores(report)

    assert analysis.deterministic.total == 3 and analysis.deterministic.passed == 2
    assert analysis.model_based.total == 6 and analysis.model_based.passed == 3
    assert analysis.model_based.evaluators == ["judge_a", "judge_b"]

    cost = analysis.judge_cost
    assert cost.judge_scores == 6 and cost.priced_scores == 3 and not cost.complete
    assert cost.total_cost_usd == pytest.approx(0.006)
    assert cost.cost_per_case_usd is None  # incomplete coverage
    judge_a = next(e for e in cost.evaluators if e.evaluator == "judge_a")
    assert judge_a.cost_sources == {"measured": 3}
    assert judge_a.input_tokens == 1500 and judge_a.judge_models == ["m1"]

    disagreed = {d.case_id: d for d in analysis.disagreements}
    assert set(disagreed) == {"b", "c"}
    assert disagreed["b"].passing == ["judge_a"]
    assert disagreed["b"].failing == ["deterministic", "judge_b"]
    assert disagreed["c"].deterministic_vs_model is True
    assert analysis.comparable_cases == 3
    assert analysis.disagreement_rate == pytest.approx(2 / 3)
    pair = next(
        p
        for p in analysis.pairwise_agreement
        if (p.evaluator_a, p.evaluator_b) == ("judge_a", "judge_b")
    )
    assert pair.shared_cases == 3 and pair.agreements == 2


def test_judge_cost_estimated_from_tokens_and_pricing() -> None:
    def judge(context: EvaluationContext) -> Score:
        return Score(
            name="j",
            value=1,
            passed=True,
            explanation="ok",
            metadata={
                "judge_model": "gpt-4o-mini",
                "judge_provider": "openai",
                "judge_input_tokens": 1000,
                "judge_output_tokens": 1000,
            },
        )

    registry = EvaluatorRegistry()
    registry.register(LLMJudgeEvaluator("j", judge, version="1"))
    report = evaluate_suite(
        _suite("j"), _samples({"a": "refund", "b": "refund", "c": "refund"}), registry=registry
    )
    cost = analyze_scores(report).judge_cost
    assert cost.complete and cost.evaluators[0].cost_sources == {"estimated": 3}
    assert cost.total_cost_usd and cost.total_cost_usd > 0
    assert cost.cost_per_case_usd == pytest.approx(cost.total_cost_usd / 3)


def test_deterministic_only_report_has_no_judge_cost_or_comparisons() -> None:
    report = evaluate_suite(_suite(), _samples({"a": "refund", "b": "x", "c": "refund"}))
    analysis = analyze_scores(report)
    assert analysis.model_based.total == 0 and analysis.judge_cost.total_cost_usd is None
    assert analysis.comparable_cases == 0 and analysis.disagreement_rate is None
    assert "Score analysis" not in render_html_report(report)


def test_structured_judge_records_identity_usage_and_latency() -> None:
    registry = EvaluatorRegistry()
    registry.register(
        structured_judge(
            "q",
            _verdicts(
                {"a": "agree", "b": "agree", "c": "agree"},
                JudgeUsage(cost_usd=0.01, input_tokens=10, output_tokens=2),
            ),
            judge_model="m",
            judge_provider="anthropic",
            version="2",
            prompt_version="p-3",
            prompt_template="Grade this.",
        )
    )
    report = evaluate_suite(
        _suite("q"), _samples({"a": "refund", "b": "refund", "c": "refund"}), registry=registry
    )
    metadata = next(s for s in report.cases[0].scores if s.name == "q").metadata
    assert metadata["judge_provider"] == "anthropic"
    assert metadata["judge_prompt_version"] == "p-3"
    assert metadata["judge_prompt_sha256"] == prompt_fingerprint("Grade this.")
    assert metadata["judge_cost_usd"] == 0.01
    assert metadata["judge_cost_source"] == "estimated"  # unspecified -> estimated
    assert metadata["judge_input_tokens"] == 10 and metadata["judge_latency_ms"] >= 0


def test_self_judging_skip_keeps_judge_identity() -> None:
    registry = EvaluatorRegistry()
    registry.register(
        structured_judge("q", _verdicts({}), judge_model="m", version="1", prompt_version="v")
    )
    suite = _suite("q")
    for case in suite.cases:
        case.metadata["evaluated_model"] = "m"
    report = evaluate_suite(
        suite, _samples({"a": "refund", "b": "refund", "c": "refund"}), registry=registry
    )
    score = next(s for s in report.cases[0].scores if s.name == "q")
    assert score.skipped and score.metadata["judge_prompt_version"] == "v"


def test_html_report_shows_score_analysis() -> None:
    registry = EvaluatorRegistry()
    registry.register(
        structured_judge(
            "q", _verdicts({"a": "agree", "b": "agree", "c": "agree"}), judge_model="m", version="1"
        )
    )
    report = evaluate_suite(
        _suite("q"), _samples({"a": "refund", "b": "nope", "c": "refund"}), registry=registry
    )
    html = render_html_report(report)
    assert "Score analysis" in html and "Model-based" in html
    assert "Evaluator disagreement: 1/3" in html


def test_score_analysis_schema_matches_model() -> None:
    published = json.loads(
        (ROOT / "schemas" / "evaluation" / "score-analysis.schema.json").read_text("utf-8")
    )
    generated = ScoreAnalysis.model_json_schema()
    assert published["$defs"] == generated["$defs"]
    assert published["properties"] == generated["properties"]
    saved = ROOT / "examples" / "advanced_evaluation" / "artifacts" / "score-analysis.json"
    Draft202012Validator(published).validate(json.loads(saved.read_text("utf-8")))
