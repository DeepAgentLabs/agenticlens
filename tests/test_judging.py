import pytest

from agenticlens.evaluation import (
    EvalTrace,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    JudgeVerdict,
    calibrate_judge,
    evaluate_suite,
    judge_verdict,
    structured_judge,
)
from agenticlens.evaluation import TestCase as EvalCase
from agenticlens.evaluation import TestSuite as EvalSuite
from agenticlens.evaluation.calibration import CalibrationDataset


def _report(verdict: JudgeVerdict, *, model: str = "gpt-4o-mini", **options):
    registry = EvaluatorRegistry()
    registry.register(
        structured_judge(
            "grounding",
            lambda context: verdict,
            judge_model="claude-judge",
            version="grounding-v1",
            **options,
        )
    )
    suite = EvalSuite(
        name="judged",
        version="1",
        cases=[
            EvalCase(
                id="a",
                name="a",
                evaluators=[EvaluatorConfig(name="grounding", threshold=0.5)],
                metadata={"model": model},
            )
        ],
    )
    sample = EvaluationSample(case_id="a", output="answer", trace=EvalTrace(trace_id="t-a"))
    return evaluate_suite(suite, [sample], registry=registry)


def test_structured_verdict_is_scored_and_kept_in_metadata() -> None:
    verdict = JudgeVerdict(
        verdict="partially_agree",
        confidence=0.8,
        rationale="Mostly grounded.",
        unsupported_claims=["refund in 2 days"],
        evidence_missed=["policy section 4"],
    )

    score = _report(verdict).cases[0].scores[0]

    assert score.value == 0.5 and score.passed
    assert score.evaluator == "grounding" and score.evaluator_version == "grounding-v1"
    assert score.evaluator_type == "llm_judge"
    assert "1 unsupported claim(s)" in score.explanation
    assert judge_verdict(score) == verdict
    assert score.metadata["judge_model"] == "claude-judge"
    assert score.metadata["evaluated_model"] == "gpt-4o-mini"
    assert score.metadata["self_confirmation_risk"] is False


def test_self_judging_is_skipped_by_default() -> None:
    verdict = JudgeVerdict(verdict="agree", confidence=0.99)

    case = _report(verdict, model="Claude-Judge").cases[0]

    score = case.scores[0]
    assert score.skipped
    assert "self-confirmation" in score.explanation
    assert case.passed  # a skipped check never fails the case


def test_self_judging_can_be_allowed_but_is_flagged() -> None:
    verdict = JudgeVerdict(verdict="agree", confidence=0.99)

    score = _report(verdict, model="claude-judge", allow_self_judging=True).cases[0].scores[0]

    assert not score.skipped
    assert score.metadata["self_confirmation_risk"] is True


def test_custom_verdict_values_and_validation() -> None:
    verdict = JudgeVerdict(verdict="partially_agree", confidence=0.5)
    score = (
        _report(
            verdict,
            verdict_values={"agree": 1.0, "partially_agree": 0.25, "disagree": 0.0},
        )
        .cases[0]
        .scores[0]
    )
    assert score.value == 0.25 and not score.passed

    with pytest.raises(ValueError, match="missing"):
        structured_judge(
            "x", lambda c: verdict, judge_model="m", version="1", verdict_values={"agree": 1.0}
        )
    with pytest.raises(ValueError, match="judge_model"):
        structured_judge("x", lambda c: verdict, judge_model=" ", version="1")


def test_structured_judge_scores_feed_calibration() -> None:
    report = _report(JudgeVerdict(verdict="disagree", confidence=0.9))
    dataset = CalibrationDataset(
        name="labels",
        version="1",
        suite_name="judged",
        suite_version="1",
        labels=[{"case_id": "a", "passed": False}],
    )

    calibration = calibrate_judge(report, dataset, evaluator="grounding")

    assert calibration.agreement_rate == 1.0


def test_judge_verdict_returns_none_for_plain_scores() -> None:
    from agenticlens.evaluation import Score

    assert judge_verdict(Score(name="x", value=1, passed=True, explanation="")) is None


def test_evaluated_model_falls_back_to_trace_metadata() -> None:
    from agenticlens.evaluation import evaluated_model

    context = EvaluationContext(
        case=EvalCase(id="a", name="a", expected_output="x"),
        sample=EvaluationSample(
            case_id="a", output="x", trace=EvalTrace(metadata={"model_name": "m-1"})
        ),
        config=EvaluatorConfig(name="j"),
    )
    assert evaluated_model(context) == "m-1"
