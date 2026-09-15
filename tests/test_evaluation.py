from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.evaluation import (
    DatasetLabel,
    EvaluationSample,
    dataset_from_samples,
    dataset_to_samples,
    evaluate_suite,
    render_html_report,
    split_dataset,
    summarize_dataset,
    to_eval_trace,
)
from agenticlens.evaluation import (
    TestCase as EvaluationTestCase,
)
from agenticlens.evaluation import (
    TestSuite as EvaluationTestSuite,
)
from agenticlens.models.trace import Run, RunStatus, Span, SpanType

# The evaluation *engine* itself (evaluate_suite, evaluate_gate, evaluators,
# JSON Schema/tool/latency/cost checks, live targets) now lives in and is
# tested by the standalone `agentic-evals` package -- see that repo's test
# suite. What's left here is what's still actually AgenticLens-specific:
# rendering, dataset versioning, and the Run -> EvalTrace adapter.


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


def test_to_eval_trace_carries_over_tool_name_latency_and_cost() -> None:
    run = make_run(latency_ms=250, cost=0.01)

    trace = to_eval_trace(run)

    assert trace.trace_id == run.trace_id
    assert trace.total_latency_ms == run.total_latency_ms
    assert trace.estimated_cost_usd == 0.01
    assert trace.spans[0].tool_name == "add"


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
                trace=to_eval_trace(make_run()),
            )
        ],
    )
    html = render_html_report(report)
    assert "&lt;Release&gt;" in html
    assert "<script>alert(1)</script>" not in html


def test_dataset_helpers_round_trip_samples_and_splits() -> None:
    samples = [
        EvaluationSample(
            case_id=f"case-{index}", output=str(index), trace=to_eval_trace(make_run())
        )
        for index in range(1, 7)
    ]
    dataset = dataset_from_samples(name="support", version="1", samples=samples)
    summary = summarize_dataset(dataset)

    assert summary.total_records == 6
    assert dataset_to_samples(dataset)[0].case_id == "case-1"

    split = split_dataset(dataset, train_ratio=0.5, validation_ratio=1 / 3, test_ratio=1 / 6)
    split_summary = summarize_dataset(split)
    assert split_summary.split_counts == {"test": 1, "train": 3, "validation": 2}


def test_dataset_label_requires_reference_judgment() -> None:
    with pytest.raises(
        ValueError,
        match="must define expected_value, expected_passed, or expected_verdict",
    ):
        DatasetLabel(score_name="answer_quality")
