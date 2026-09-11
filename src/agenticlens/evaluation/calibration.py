"""Offline judge agreement against a versioned, human-labelled reference set."""

from math import sqrt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

from agenticlens.evaluation.models import EvaluationReport


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
    for label in dataset.labels:
        case = case_map[label.case_id]
        scores = [score for score in case.scores if score.name == evaluator]
        if len(scores) != 1 or scores[0].evaluator_type != "llm_judge":
            raise ValueError(
                f"case {label.case_id!r} must have exactly one llm_judge score named {evaluator!r}"
            )
        score = scores[0]
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
