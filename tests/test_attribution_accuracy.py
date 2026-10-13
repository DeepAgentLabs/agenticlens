"""Attribution accuracy on controlled failures, and the committed corpus."""

import json
import runpy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from agenticlens.diagnosis import (
    AttributionAccuracyReport,
    ControlledFailure,
    FailureCategory,
    controlled_failure_from_run,
    evaluate_attribution,
    load_controlled_failures,
)
from diagnosis_support import run, span

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "examples" / "diagnosis" / "controlled_failures"
SAVED = ROOT / "examples" / "diagnosis" / "attribution-accuracy.json"


def test_corpus_builder_reproduces_committed_traces(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / "examples" / "diagnosis" / "build_controlled_failures.py"))
    written = module["build"](tmp_path)
    assert len(written) == 40
    for path in written:
        assert path.read_text("utf-8") == (CORPUS / path.name).read_text("utf-8"), path.name


def test_corpus_accuracy_matches_saved_report_and_clears_floor() -> None:
    report = evaluate_attribution(load_controlled_failures(CORPUS))
    assert report.total_cases == 40
    assert report.step.accuracy is not None and report.step.accuracy >= 0.9
    assert report.category.total == 40
    saved = AttributionAccuracyReport.model_validate_json(SAVED.read_text("utf-8"))
    assert report.model_dump() == saved.model_dump()


def test_accuracy_schema_matches_model_and_validates_saved_report() -> None:
    schema_path = ROOT / "schemas" / "diagnosis" / "attribution-accuracy-report.schema.json"
    published = json.loads(schema_path.read_text("utf-8"))
    generated = AttributionAccuracyReport.model_json_schema()
    assert published["$defs"] == generated["$defs"]
    assert published["properties"] == generated["properties"]
    Draft202012Validator(published).validate(json.loads(SAVED.read_text("utf-8")))


def _failing_run(**metadata: object) -> object:
    return run(
        [
            span("a", "plan", "model_call", 0, agent_name="p"),
            span("t", "fetch", "tool_call", 10, status="failed", agent_name="w"),
        ],
        failed=True,
        metadata=dict(metadata),
    )


def test_ground_truth_from_metadata() -> None:
    case = controlled_failure_from_run(
        _failing_run(expected_faulty_span_id="t", expected_category="tool_error")  # type: ignore[arg-type]
    )
    assert case.expected_span_id == "t"
    assert case.expected_span_name == "fetch"
    assert case.expected_agent == "w"
    assert case.expected_category is FailureCategory.TOOL_ERROR


def test_ground_truth_from_chaos_markers() -> None:
    trace = run([span("k", "kb", "retrieval", 0, attributes={"chaos.injected": True})])
    assert controlled_failure_from_run(trace).expected_span_id == "k"


def test_ground_truth_errors() -> None:
    with pytest.raises(ValueError, match="exactly one span"):
        controlled_failure_from_run(_failing_run())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not in the trace"):
        controlled_failure_from_run(_failing_run(expected_faulty_span_id="nope"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="expected_span_id or expected_span_name"):
        ControlledFailure(case_id="x", run=run([]))


def test_wrong_predictions_are_counted_and_top3_helps() -> None:
    trace = run(
        [
            span("t", "fetch", "tool_call", 0, status="failed", agent_name="w"),
            span("v", "check", "validation", 20, status="failed", agent_name="w"),
        ],
        failed=True,
    )
    case = ControlledFailure(
        case_id="c",
        run=trace,
        expected_span_name="check",
        expected_agent="w",
        expected_category=FailureCategory.VALIDATION_FAILURE,
    )
    report = evaluate_attribution([case])
    [outcome] = report.outcomes
    assert outcome.step_correct is False and outcome.top3_correct is True
    assert outcome.agent_correct is True
    assert outcome.category_correct is False
    assert report.step.accuracy == 0.0 and report.calibration_gap > 0
    assert report.warnings  # fewer than 30 cases


def test_loader_accepts_case_objects_and_lists(tmp_path: Path) -> None:
    trace = run([span("t", "fetch", "tool_call", 0, status="failed")], failed=True)
    case = ControlledFailure(case_id="one", run=trace, expected_span_id="t")
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([case.model_dump(mode="json")]), "utf-8")
    [loaded] = load_controlled_failures(path)
    assert loaded.case_id == "one"
    with pytest.raises(ValueError, match="unique"):
        path.write_text(json.dumps([case.model_dump(mode="json")] * 2), "utf-8")
        load_controlled_failures(path)
    with pytest.raises(ValueError, match="no JSON files"):
        load_controlled_failures(_empty(tmp_path))
    with pytest.raises(ValueError, match="at least one"):
        evaluate_attribution([])


def _empty(tmp_path: Path) -> Path:
    empty = tmp_path / "empty"
    empty.mkdir()
    return empty
