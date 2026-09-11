import json

import pytest
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.comparison.runner import compare_runs, summarize_runs
from agenticlens.evaluation import EvaluationSample, GateConfig, evaluate_gate, evaluate_suite
from agenticlens.evaluation.models import TestCase as Case
from agenticlens.evaluation.models import TestSuite as Suite
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def make_run(cost=0.0):
    return Run(
        application_name="checks",
        status=RunStatus.SUCCEEDED,
        spans=[Span(name="model", span_type=SpanType.MODEL_CALL, estimated_cost_usd=cost)],
    )


def score_output(schema, output):
    suite = Suite(
        name="structured", version="1", cases=[Case(id="a", name="a", output_json_schema=schema)]
    )
    return evaluate_suite(suite, [EvaluationSample(case_id="a", output=output, trace=make_run())])


@pytest.mark.parametrize(
    "schema,output,passed",
    [
        ({"type": "string", "enum": ["ok"]}, '"bad"', False),
        ({"type": "number", "minimum": 1}, "0", False),
        ({"type": "integer"}, "true", False),
        ({"type": "integer"}, "1.0", True),
        ({"type": "object", "additionalProperties": False}, '{"extra":1}', False),
        ({"type": "array", "uniqueItems": True}, "[1,1]", False),
        ({"oneOf": [{"type": "string"}, {"type": "null"}]}, "null", True),
        (
            {"$defs": {"count": {"type": "integer", "minimum": 1}}, "$ref": "#/$defs/count"},
            "0",
            False,
        ),
        (
            {"$defs": {"count": {"type": "integer", "minimum": 1}}, "$ref": "#/$defs/count"},
            "2",
            True,
        ),
        ({"type": "number"}, "NaN", False),
        ({"type": "number"}, "Infinity", False),
    ],
)
def test_schema_keywords_and_json_types(schema, output, passed):
    result = score_output(schema, output)
    assert result.cases[0].passed is passed


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "bogus"},
        {"minimum": "one"},
        {"$schema": "https://example.org/unsupported"},
    ],
)
def test_invalid_schema_is_configuration_error_even_without_samples(schema):
    suite = Suite(name="s", version="1", cases=[Case(id="a", name="a", output_json_schema=schema)])
    with pytest.raises(ValueError, match="output_json_schema"):
        evaluate_suite(suite, [])


def test_external_schema_reference_is_not_fetched(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Schema validation attempted network access")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    with pytest.raises(ValueError, match="Unresolvable"):
        score_output({"$ref": "https://example.org/schema.json"}, "{}")


@pytest.mark.parametrize("ids,match", [(["a", "a"], "Duplicate"), (["unknown"], "Unknown")])
def test_rejects_ambiguous_sample_identity(ids, match):
    suite = Suite(name="s", version="1", cases=[Case(id="a", name="a", expected_output="ok")])
    with pytest.raises(ValueError, match=match):
        evaluate_suite(
            suite, [EvaluationSample(case_id=i, output="ok", trace=make_run()) for i in ids]
        )


@pytest.mark.parametrize(
    "costs,expected",
    [
        ([0.1, None], None),
        ([None, None], None),
        ([0.0, 0.0], 0.0),
        ([0.1, 0.2], 0.3),
    ],
)
def test_cost_gate_requires_complete_costs(costs, expected):
    suite = Suite(
        name="s",
        version="1",
        cases=[Case(id=str(i), name=str(i), expected_output="ok") for i in range(2)],
    )
    samples = [
        EvaluationSample(case_id=str(i), output="ok", trace=make_run(cost))
        for i, cost in enumerate(costs)
    ]
    result = evaluate_suite(suite, samples)
    if expected is None:
        assert result.summary.total_cost_usd is None
    else:
        assert result.summary.total_cost_usd == pytest.approx(expected)
    decision = evaluate_gate(result, GateConfig(max_total_cost_usd=1))
    assert decision.passed is (expected is not None)


def test_missing_sample_keeps_total_unknown():
    suite = Suite(
        name="s", version="1", cases=[Case(id=i, name=i, expected_output="ok") for i in ("a", "b")]
    )
    result = evaluate_suite(
        suite, [EvaluationSample(case_id="a", output="ok", trace=make_run(0.1))]
    )
    assert result.summary.failed_cases == 1
    assert result.summary.total_cost_usd is None


def test_unpriced_span_makes_trace_and_case_cost_unknown():
    run = make_run(0.1)
    run.spans.append(Span(name="other", span_type=SpanType.TOOL_CALL))
    assert run.estimated_cost_usd is None
    suite = Suite(name="s", version="1", cases=[Case(id="a", name="a", max_cost_usd=1)])
    result = evaluate_suite(suite, [EvaluationSample(case_id="a", output="ok", trace=run)])
    assert not result.cases[0].passed
    run.spans[-1].estimated_cost_usd = 0.0
    assert run.estimated_cost_usd == 0.1


@pytest.mark.parametrize(
    "task_success,status,expected",
    [
        (False, RunStatus.SUCCEEDED, 0),
        (True, RunStatus.FAILED, 1),
        (None, RunStatus.SUCCEEDED, 1),
        (None, RunStatus.FAILED, 0),
        (None, RunStatus.RUNNING, 0),
    ],
)
def test_explicit_task_result_overrides_execution_status(task_success, status, expected):
    run = make_run(0.1)
    run.task_success, run.status = task_success, status
    result = summarize_runs("s", [run])
    assert result.success_rate == expected
    assert result.cost_per_successful_task == (0.1 if expected else None)


def test_incomplete_costs_do_not_produce_comparison_or_cost_per_success():
    result = compare_runs([make_run(0.1)], [make_run(0.01), make_run(None)])
    assert result.candidate.cost_usd is None
    assert result.candidate.cost_per_successful_task is None
    assert result.mean_cost_usd_delta is None


def test_cli_rejects_duplicate_samples_without_writing_report(tmp_path):
    suite = Suite(name="s", version="1", cases=[Case(id="a", name="a", expected_output="ok")])
    sample = EvaluationSample(case_id="a", output="ok", trace=make_run())
    source, data, out = [tmp_path / name for name in ("suite.json", "samples.json", "out.json")]
    source.write_text(suite.model_dump_json(), encoding="utf-8")
    data.write_text(json.dumps([sample.model_dump(mode="json")] * 2), encoding="utf-8")
    result = CliRunner().invoke(app, ["evaluate", str(source), str(data), "--save", str(out)])
    assert result.exit_code == 1
    assert "Duplicate sample" in result.output
    assert not out.exists()


def test_cost_gate_rejects_legacy_partial_summary():
    suite = Suite(
        name="s",
        version="1",
        cases=[Case(id=i, name=i, expected_output="ok") for i in ("a", "b")],
    )
    result = evaluate_suite(
        suite,
        [
            EvaluationSample(case_id="a", output="ok", trace=make_run(0.01)),
            EvaluationSample(case_id="b", output="ok", trace=make_run(None)),
        ],
    )
    result.summary.total_cost_usd = 0.01  # Older reports summed only known cases.
    decision = evaluate_gate(result, GateConfig(max_total_cost_usd=1))
    assert not decision.passed
    assert any("incomplete" in reason for reason in decision.reasons)
