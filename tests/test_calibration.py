import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.evaluation.calibration import CalibrationDataset, calibrate_judge
from agenticlens.evaluation.models import (
    CaseEvaluation,
    EvaluationReport,
    EvaluationSummary,
    Score,
)


def make_inputs(verdicts=(True, False, True, False), labels=(True, False, False, True)):
    report = EvaluationReport(
        suite_name="support",
        suite_version="1",
        summary=EvaluationSummary(
            total_cases=4,
            passed_cases=2,
            failed_cases=2,
            pass_rate=0.5,
            average_score=0.5,
            average_latency_ms=0,
        ),
        cases=[
            CaseEvaluation(
                case_id=str(i),
                case_name=str(i),
                passed=verdict,
                output="",
                trace_id=f"trace-{i}",
                latency_ms=0,
                scores=[
                    Score(
                        name="quality",
                        value=0.7,
                        passed=verdict,
                        explanation="saved verdict",
                        evaluator_type="llm_judge",
                    )
                ],
            )
            for i, verdict in enumerate(verdicts)
        ],
    )
    dataset = CalibrationDataset(
        name="reviewed",
        version="2",
        suite_name="support",
        suite_version="1",
        labels=[{"case_id": str(i), "passed": label} for i, label in enumerate(labels)],
    )
    return report, dataset


def test_agreement_confusion_and_trace_evidence():
    report, dataset = make_inputs()
    result = calibrate_judge(report, dataset, evaluator="quality")
    assert result.agreement_rate == 0.5
    assert (
        result.true_accepts,
        result.true_rejects,
        result.false_accepts,
        result.false_rejects,
    ) == (1, 1, 1, 1)
    assert result.agreement_interval == pytest.approx((0.15003899, 0.84996101))
    assert result.cases[3].trace_id == "trace-3"
    assert result.cases[3].judge_value == 0.7
    assert not result.cases[3].judge_passed  # Do not re-threshold the saved score.
    assert result.dataset_version == "2"


@pytest.mark.parametrize(
    "verdicts,expected",
    [
        ((True,), 1.0),
        ((False,), 0.0),
    ],
)
def test_extreme_agreement_has_nonzero_uncertainty(verdicts, expected):
    report, dataset = make_inputs(verdicts, (True,))
    result = calibrate_judge(report, dataset, evaluator="quality")
    assert result.agreement_rate == expected
    low, high = result.agreement_interval
    assert 0 <= low < high <= 1
    assert high - low > 0.7
    assert any("one class" in warning for warning in result.warnings)


@pytest.mark.parametrize(
    "change", ["missing", "extra", "duplicate", "suite", "version", "score", "type", "ambiguous"]
)
def test_rejects_misaligned_or_ambiguous_evidence(change):
    report, dataset = make_inputs()
    if change == "missing":
        report.cases.pop()
    elif change == "extra":
        dataset.labels.pop()
    elif change == "duplicate":
        report.cases.append(report.cases[0])
    elif change == "suite":
        dataset.suite_name = "other"
    elif change == "version":
        dataset.suite_version = "other"
    elif change == "score":
        report.cases[0].scores.clear()
    elif change == "type":
        report.cases[0].scores[0].evaluator_type = "deterministic"
    else:
        report.cases[0].scores.append(report.cases[0].scores[0])
    with pytest.raises(ValueError):
        calibrate_judge(report, dataset, evaluator="quality")


@pytest.mark.parametrize(
    "labels", [[], [{"case_id": "a", "passed": "false"}], [{"case_id": "a", "passed": True}] * 2]
)
def test_reference_validation(labels):
    with pytest.raises(ValidationError):
        CalibrationDataset(name="x", version="1", suite_name="s", suite_version="1", labels=labels)


def test_cli_writes_report_and_rejects_bad_input(tmp_path):
    report, dataset = make_inputs()
    source, labels, target = [
        tmp_path / name for name in ("report.json", "labels.json", "out.json")
    ]
    source.write_text(report.model_dump_json(), encoding="utf-8")
    labels.write_text(dataset.model_dump_json(), encoding="utf-8")
    args = ["calibrate", str(source), str(labels), "--evaluator", "quality", "--save", str(target)]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    assert json.loads(target.read_text())["false_accepts"] == 1
    labels.write_text("{}", encoding="utf-8")
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 1
    assert "Unable to calibrate" in result.output
