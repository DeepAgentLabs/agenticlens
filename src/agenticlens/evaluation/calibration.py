from math import sqrt
from statistics import NormalDist

from agenticlens.evaluation.datasets import find_dataset_label
from agenticlens.evaluation.models import (
    CalibrationCase,
    CalibrationMetric,
    CalibrationReport,
    ConfidenceInterval,
    EvaluationDataset,
    EvaluationReport,
)


def _z_value(confidence_level: float) -> float:
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")
    return NormalDist().inv_cdf(0.5 + confidence_level / 2)


def _mean_confidence_interval(
    values: list[float],
    *,
    confidence_level: float,
) -> ConfidenceInterval | None:
    if not values:
        return None
    mean = sum(values) / len(values)
    if len(values) == 1:
        return ConfidenceInterval(
            lower=mean,
            upper=mean,
            confidence_level=confidence_level,
            method="normal_single_sample",
        )
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    margin = _z_value(confidence_level) * sqrt(variance / len(values))
    upper = min(1.0, mean + margin) if all(0 <= value <= 1 for value in values) else mean + margin
    return ConfidenceInterval(
        lower=max(0.0, mean - margin),
        upper=upper,
        confidence_level=confidence_level,
        method="normal_approximation",
    )


def _wilson_interval(
    successes: int,
    total: int,
    *,
    confidence_level: float,
) -> ConfidenceInterval | None:
    if total <= 0:
        return None
    z = _z_value(confidence_level)
    z2 = z**2
    proportion = successes / total
    denominator = 1 + z2 / total
    center = (proportion + z2 / (2 * total)) / denominator
    margin = z * sqrt((proportion * (1 - proportion) + z2 / (4 * total)) / total) / denominator
    return ConfidenceInterval(
        lower=max(0.0, center - margin),
        upper=min(1.0, center + margin),
        confidence_level=confidence_level,
        method="wilson_score",
    )


def calibrate_judge(
    report: EvaluationReport,
    dataset: EvaluationDataset,
    *,
    score_name: str,
    confidence_level: float = 0.95,
) -> CalibrationReport:
    record_by_case = {record.case_id: record for record in dataset.records}
    cases: list[CalibrationCase] = []

    for evaluated_case in report.cases:
        record = record_by_case.get(evaluated_case.case_id)
        if record is None:
            continue
        label = find_dataset_label(record, score_name)
        if label is None:
            continue
        score = next((item for item in evaluated_case.scores if item.name == score_name), None)
        if score is None:
            continue

        expected_passed = (
            label.expected_passed
            if label.expected_passed is not None
            else (
                label.expected_value >= label.threshold
                if label.expected_value is not None and label.threshold is not None
                else None
            )
        )
        absolute_error = (
            abs(score.value - label.expected_value) if label.expected_value is not None else None
        )
        judge_verdict = score.metadata.get("judge_verdict")
        verdict_agreement = (
            judge_verdict == label.expected_verdict
            if judge_verdict is not None and label.expected_verdict is not None
            else None
        )
        pass_agreement = score.passed == expected_passed if expected_passed is not None else None
        cases.append(
            CalibrationCase(
                case_id=evaluated_case.case_id,
                case_name=evaluated_case.case_name,
                judge_score=score.value,
                expected_score=label.expected_value,
                absolute_error=absolute_error,
                judge_passed=score.passed,
                expected_passed=expected_passed,
                pass_agreement=pass_agreement,
                judge_verdict=judge_verdict if isinstance(judge_verdict, str) else None,
                expected_verdict=label.expected_verdict,
                verdict_agreement=verdict_agreement,
                metadata={
                    "score_explanation": score.explanation,
                    **({"label_notes": label.notes} if label.notes else {}),
                },
            )
        )

    if not cases:
        raise ValueError(f"No labeled calibration cases were found for score {score_name!r}.")

    judge_scores = [case.judge_score for case in cases]
    expected_scores = [case.expected_score for case in cases if case.expected_score is not None]
    absolute_errors = [case.absolute_error for case in cases if case.absolute_error is not None]
    squared_errors = [case.absolute_error**2 for case in cases if case.absolute_error is not None]
    pass_agreements = [case.pass_agreement for case in cases if case.pass_agreement is not None]
    verdict_agreements = [
        case.verdict_agreement for case in cases if case.verdict_agreement is not None
    ]

    metrics = [
        CalibrationMetric(
            name="mean_judge_score",
            value=sum(judge_scores) / len(judge_scores),
            sample_size=len(judge_scores),
            confidence_interval=_mean_confidence_interval(
                judge_scores, confidence_level=confidence_level
            ),
        ),
    ]
    if expected_scores:
        metrics.append(
            CalibrationMetric(
                name="mean_expected_score",
                value=sum(expected_scores) / len(expected_scores),
                sample_size=len(expected_scores),
                confidence_interval=_mean_confidence_interval(
                    expected_scores, confidence_level=confidence_level
                ),
            )
        )
    if absolute_errors:
        metrics.append(
            CalibrationMetric(
                name="mean_absolute_error",
                value=sum(absolute_errors) / len(absolute_errors),
                sample_size=len(absolute_errors),
                confidence_interval=_mean_confidence_interval(
                    absolute_errors, confidence_level=confidence_level
                ),
            )
        )
        metrics.append(
            CalibrationMetric(
                name="root_mean_squared_error",
                value=sqrt(sum(squared_errors) / len(squared_errors)),
                sample_size=len(squared_errors),
            )
        )
    if pass_agreements:
        agreement_count = sum(1 for item in pass_agreements if item)
        metrics.append(
            CalibrationMetric(
                name="pass_rate_agreement",
                value=agreement_count / len(pass_agreements),
                sample_size=len(pass_agreements),
                confidence_interval=_wilson_interval(
                    agreement_count,
                    len(pass_agreements),
                    confidence_level=confidence_level,
                ),
            )
        )
    if verdict_agreements:
        agreement_count = sum(1 for item in verdict_agreements if item)
        metrics.append(
            CalibrationMetric(
                name="verdict_agreement",
                value=agreement_count / len(verdict_agreements),
                sample_size=len(verdict_agreements),
                confidence_interval=_wilson_interval(
                    agreement_count,
                    len(verdict_agreements),
                    confidence_level=confidence_level,
                ),
            )
        )

    return CalibrationReport(
        suite_name=report.suite_name,
        suite_version=report.suite_version,
        dataset_name=dataset.name,
        dataset_version=dataset.version,
        score_name=score_name,
        confidence_level=confidence_level,
        summary=metrics,
        cases=cases,
    )
