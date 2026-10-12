import pytest

from agenticlens.evaluation import (
    CaseEvaluation,
    EvaluationReport,
    EvaluationSummary,
    Score,
    tune_judge_threshold,
)
from agenticlens.evaluation.calibration import CalibrationDataset


def _inputs(values: list[float], labels: list[bool], threshold: float = 0.5):
    report = EvaluationReport(
        suite_name="s",
        suite_version="1",
        summary=EvaluationSummary(
            total_cases=len(values),
            passed_cases=0,
            failed_cases=len(values),
            pass_rate=0,
            average_score=0,
            average_latency_ms=0,
        ),
        cases=[
            CaseEvaluation(
                case_id=str(i),
                case_name=str(i),
                passed=value >= threshold,
                output="",
                trace_id=f"t{i}",
                latency_ms=0,
                scores=[
                    Score(
                        name="judge",
                        value=value,
                        passed=value >= threshold,
                        explanation="",
                        evaluator_type="llm_judge",
                    )
                ],
            )
            for i, value in enumerate(values)
        ],
    )
    dataset = CalibrationDataset(
        name="labels",
        version="1",
        suite_name="s",
        suite_version="1",
        labels=[{"case_id": str(i), "passed": label} for i, label in enumerate(labels)],
    )
    return report, dataset


def test_recommends_threshold_that_separates_the_classes() -> None:
    # The judge is too lenient at 0.5: 0.6 and 0.65 should fail.
    report, dataset = _inputs(
        [0.9, 0.85, 0.8, 0.65, 0.6, 0.2], [True, True, True, False, False, False]
    )

    tuning = tune_judge_threshold(report, dataset, evaluator="judge")

    assert tuning.objective == "balanced_accuracy"
    assert tuning.recommended_threshold == 0.8
    assert tuning.recommended.agreement_rate == 1.0
    assert tuning.current_agreement_rate == pytest.approx(4 / 6)
    assert any("held-out" in warning for warning in tuning.warnings)


def test_explicit_threshold_grid_and_ties_prefer_lowest() -> None:
    report, dataset = _inputs([0.9, 0.1], [True, False])

    tuning = tune_judge_threshold(report, dataset, evaluator="judge", thresholds=[0.3, 0.5, 0.7])

    assert [point.threshold for point in tuning.points] == [0.3, 0.5, 0.7]
    assert tuning.recommended_threshold == 0.3


def test_single_class_falls_back_to_agreement_with_warning() -> None:
    report, dataset = _inputs([0.9, 0.4], [True, True])

    tuning = tune_judge_threshold(report, dataset, evaluator="judge")

    assert tuning.objective == "agreement_rate"
    assert tuning.recommended.balanced_accuracy is None
    assert any("one class" in warning for warning in tuning.warnings)


def test_invalid_thresholds_are_rejected() -> None:
    report, dataset = _inputs([0.9, 0.1], [True, False])
    with pytest.raises(ValueError, match="thresholds"):
        tune_judge_threshold(report, dataset, evaluator="judge", thresholds=[1.5])
    with pytest.raises(ValueError, match="thresholds"):
        tune_judge_threshold(report, dataset, evaluator="judge", thresholds=[])
