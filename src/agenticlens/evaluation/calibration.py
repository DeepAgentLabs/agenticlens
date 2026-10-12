"""Offline judge agreement against a versioned, human-labelled reference set."""

from math import sqrt
from typing import Literal

from agentic_evals import EvaluationReport
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator


class ReferenceLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1)
    passed: StrictBool


class CalibrationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    suite_name: str = Field(min_length=1)
    suite_version: str = Field(min_length=1)
    labels: list[ReferenceLabel] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_labels(self) -> "CalibrationDataset":
        ids = [label.case_id for label in self.labels]
        if len(ids) != len(set(ids)):
            raise ValueError("reference case IDs must be unique")
        return self


class CalibrationCase(BaseModel):
    case_id: str
    trace_id: str
    judge_value: float
    judge_passed: bool
    reference_passed: bool
    agreed: bool


class CalibrationReport(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    dataset_name: str
    dataset_version: str
    suite_name: str
    suite_version: str
    evaluator: str
    evaluator_version: str | None = None
    sample_count: int
    agreement_rate: float
    confidence_level: float = Field(default=0.95, ge=0.95, le=0.95)
    interval_method: Literal["wilson"] = "wilson"
    agreement_interval: tuple[float, float]
    true_accepts: int
    true_rejects: int
    false_accepts: int
    false_rejects: int
    cases: list[CalibrationCase]
    warnings: list[str]


def calibrate_judge(
    report: EvaluationReport,
    dataset: CalibrationDataset,
    *,
    evaluator: str,
) -> CalibrationReport:
    """Compare saved llm_judge verdicts; require exact case and suite matching.

    Uses Score.passed (the recorded threshold decision), not an assumed 0.5
    threshold. The Wilson interval assumes independent representative cases;
    this measures verdict agreement, not probabilistic confidence calibration.

    All judged scores must come from one evaluator version: mixing judge
    prompts or models in one calibration run raises. Scores without a
    recorded version are accepted with a warning.
    """
    if not evaluator.strip():
        raise ValueError("evaluator must not be empty")
    if (report.suite_name, report.suite_version) != (dataset.suite_name, dataset.suite_version):
        raise ValueError("reference dataset must match the report suite name and version")
    case_map = {case.case_id: case for case in report.cases}
    if len(case_map) != len(report.cases):
        raise ValueError("report case IDs must be unique")
    if set(case_map) != {label.case_id for label in dataset.labels}:
        raise ValueError("reference labels must exactly match report case IDs")
    cases: list[CalibrationCase] = []
    versions: set[str | None] = set()
    for label in dataset.labels:
        case = case_map[label.case_id]
        scores = [score for score in case.scores if score.name == evaluator]
        if len(scores) != 1 or scores[0].evaluator_type != "llm_judge":
            raise ValueError(
                f"case {label.case_id!r} must have exactly one llm_judge score named {evaluator!r}"
            )
        score = scores[0]
        versions.add(score.evaluator_version)
        cases.append(
            CalibrationCase(
                case_id=case.case_id,
                trace_id=case.trace_id,
                judge_value=score.value,
                judge_passed=score.passed,
                reference_passed=label.passed,
                agreed=score.passed == label.passed,
            )
        )
    if len(versions) > 1:
        listed = ", ".join(sorted(str(version) for version in versions))
        raise ValueError(
            f"judge scores for {evaluator!r} come from different evaluator versions ({listed}); "
            "calibrate one judge version at a time"
        )
    evaluator_version = next(iter(versions))
    n = len(cases)
    agreement = sum(case.agreed for case in cases) / n
    # Two-sided 95% Wilson score interval (NIST/SEMATECH handbook, prc241).
    z = 1.959963984540054
    denominator = 1 + z * z / n
    center = (agreement + z * z / (2 * n)) / denominator
    radius = z * sqrt(agreement * (1 - agreement) / n + z * z / (4 * n * n)) / denominator
    warnings = [
        "Agreement is against supplied reference labels, not proof of judge correctness.",
        "The 95% Wilson interval assumes independent, representative cases.",
    ]
    if n < 30:
        warnings.append("Fewer than 30 cases: treat this as exploratory evidence.")
    if evaluator_version is None:
        warnings.append(
            "Judge scores carry no evaluator version; record one so this result can be "
            "tied to a specific judge prompt and model."
        )
    if len({case.reference_passed for case in cases}) == 1:
        warnings.append(
            "References contain only one class; both error directions are not assessed."
        )
    return CalibrationReport(
        dataset_name=dataset.name,
        dataset_version=dataset.version,
        suite_name=report.suite_name,
        suite_version=report.suite_version,
        evaluator=evaluator,
        evaluator_version=evaluator_version,
        sample_count=n,
        agreement_rate=agreement,
        agreement_interval=(max(0.0, center - radius), min(1.0, center + radius)),
        true_accepts=sum(c.judge_passed and c.reference_passed for c in cases),
        true_rejects=sum(not c.judge_passed and not c.reference_passed for c in cases),
        false_accepts=sum(c.judge_passed and not c.reference_passed for c in cases),
        false_rejects=sum(not c.judge_passed and c.reference_passed for c in cases),
        cases=cases,
        warnings=warnings,
    )


class ThresholdPoint(BaseModel):
    threshold: float
    agreement_rate: float
    balanced_accuracy: float | None
    false_accepts: int
    false_rejects: int


class ThresholdTuningReport(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    dataset_name: str
    dataset_version: str
    evaluator: str
    sample_count: int
    current_agreement_rate: float
    recommended_threshold: float
    recommended: ThresholdPoint
    objective: Literal["balanced_accuracy", "agreement_rate"]
    points: list[ThresholdPoint]
    warnings: list[str]


def tune_judge_threshold(
    report: EvaluationReport,
    dataset: CalibrationDataset,
    *,
    evaluator: str,
    thresholds: list[float] | None = None,
) -> ThresholdTuningReport:
    """Sweep pass thresholds over saved judge values against reference labels.

    Each point re-decides `judge_value >= threshold` for every case. The
    recommended threshold maximizes balanced accuracy (the mean of the
    true-accept and true-reject rates) when both reference classes are
    present, otherwise raw agreement; ties go to the lowest threshold.
    Candidate thresholds default to every distinct judge value plus 0 and 1.

    This is fitted on the same labels it is scored on; confirm a new
    threshold on a held-out split before adopting it.
    """
    calibration = calibrate_judge(report, dataset, evaluator=evaluator)
    cases = calibration.cases
    candidates = sorted(
        set(thresholds)
        if thresholds is not None
        else {0.0, 1.0, *(case.judge_value for case in cases)}
    )
    if not candidates or any(not 0 <= value <= 1 for value in candidates):
        raise ValueError("thresholds must be a non-empty list of values between 0 and 1")
    positives = sum(case.reference_passed for case in cases)
    negatives = len(cases) - positives
    both_classes = positives > 0 and negatives > 0

    points: list[ThresholdPoint] = []
    for threshold in candidates:
        decisions = [(case.judge_value >= threshold, case.reference_passed) for case in cases]
        true_accepts = sum(judged and ref for judged, ref in decisions)
        true_rejects = sum(not judged and not ref for judged, ref in decisions)
        points.append(
            ThresholdPoint(
                threshold=threshold,
                agreement_rate=(true_accepts + true_rejects) / len(cases),
                balanced_accuracy=(
                    (true_accepts / positives + true_rejects / negatives) / 2
                    if both_classes
                    else None
                ),
                false_accepts=sum(judged and not ref for judged, ref in decisions),
                false_rejects=sum(not judged and ref for judged, ref in decisions),
            )
        )

    def objective(point: ThresholdPoint) -> float:
        if both_classes and point.balanced_accuracy is not None:
            return point.balanced_accuracy
        return point.agreement_rate

    best = max(points, key=lambda point: (objective(point), -point.threshold))
    warnings = [
        "Threshold is fitted and scored on the same labels; validate it on held-out cases.",
    ]
    if not both_classes:
        warnings.append(
            "References contain only one class; optimizing raw agreement instead of "
            "balanced accuracy, which can favor always-accept or always-reject."
        )
    if len(cases) < 30:
        warnings.append("Fewer than 30 cases: the recommended threshold is unstable.")
    return ThresholdTuningReport(
        dataset_name=dataset.name,
        dataset_version=dataset.version,
        evaluator=evaluator,
        sample_count=len(cases),
        current_agreement_rate=calibration.agreement_rate,
        recommended_threshold=best.threshold,
        recommended=best,
        objective="balanced_accuracy" if both_classes else "agreement_rate",
        points=points,
        warnings=warnings,
    )
