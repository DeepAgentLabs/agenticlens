from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agenticlens import Run, RunStatus, Span, SpanType
from agenticlens.evaluation import (
    DatasetLabel,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    Score,
    TestCase,
    TestSuite,
    calibrate_judge,
    dataset_from_samples,
    dataset_to_samples,
    evaluate_suite,
    split_dataset,
    summarize_dataset,
)


def _run(*, latency_ms: float, cost: float) -> Run:
    started = datetime.now(timezone.utc)
    return Run(
        application_name="dataset-calibration-demo",
        started_at=started,
        completed_at=started + timedelta(milliseconds=latency_ms),
        status=RunStatus.SUCCEEDED,
        task_success=True,
        spans=[
            Span(
                name="judge-demo-model",
                span_type=SpanType.MODEL_CALL,
                started_at=started,
                completed_at=started + timedelta(milliseconds=latency_ms),
                latency_ms=latency_ms,
                estimated_cost_usd=cost,
                status=RunStatus.SUCCEEDED,
            )
        ],
    )


def _judge(context: EvaluationContext) -> Score:
    mentions_refund = "refund" in context.sample.output.casefold()
    value = 0.92 if mentions_refund else 0.18
    verdict = "grounded" if mentions_refund else "ungrounded"
    return Score(
        name="answer_quality",
        value=value,
        passed=False,
        explanation="Demo judge scored the answer against a simple refund rubric.",
        metadata={"judge_verdict": verdict},
    )


def main() -> None:
    suite = TestSuite(
        name="support-quality-demo",
        version="1.0",
        cases=[
            TestCase(
                id="refund-1",
                name="Refund response",
                evaluators=[
                    EvaluatorConfig(
                        name="answer_quality_judge",
                        threshold=0.8,
                        config={"rubric": "Answer should be correct and grounded."},
                    )
                ],
            ),
            TestCase(
                id="shipping-1",
                name="Shipping response",
                evaluators=[
                    EvaluatorConfig(
                        name="answer_quality_judge",
                        threshold=0.8,
                        config={"rubric": "Answer should be correct and grounded."},
                    )
                ],
            ),
            TestCase(
                id="refund-2",
                name="Refund update response",
                evaluators=[
                    EvaluatorConfig(
                        name="answer_quality_judge",
                        threshold=0.8,
                        config={"rubric": "Answer should be correct and grounded."},
                    )
                ],
            ),
            TestCase(
                id="policy-1",
                name="Policy response",
                evaluators=[
                    EvaluatorConfig(
                        name="answer_quality_judge",
                        threshold=0.8,
                        config={"rubric": "Answer should be correct and grounded."},
                    )
                ],
            ),
        ],
    )
    samples = [
        EvaluationSample(
            case_id="refund-1",
            output="Your refund is in progress and should settle within 5 business days.",
            trace=_run(latency_ms=35, cost=0.0012),
        ),
        EvaluationSample(
            case_id="shipping-1",
            output="Shipping usually takes 2 to 3 business days.",
            trace=_run(latency_ms=28, cost=0.0010),
        ),
        EvaluationSample(
            case_id="refund-2",
            output="The refund has been approved and is now queued for payout.",
            trace=_run(latency_ms=31, cost=0.0011),
        ),
        EvaluationSample(
            case_id="policy-1",
            output="Gift cards are final sale and cannot be returned.",
            trace=_run(latency_ms=24, cost=0.0009),
        ),
    ]

    dataset = dataset_from_samples(
        name="support-review-demo",
        version="2026-08-16",
        samples=samples,
        description="Local dataset example with split assignment and judge labels.",
    )
    labels_by_case = {
        "refund-1": DatasetLabel(
            score_name="answer_quality",
            expected_value=1.0,
            expected_passed=True,
            expected_verdict="grounded",
            notes="Reviewer confirmed correct refund handling.",
        ),
        "shipping-1": DatasetLabel(
            score_name="answer_quality",
            expected_value=0.0,
            expected_passed=False,
            expected_verdict="ungrounded",
            notes="Does not address the refund rubric.",
        ),
        "refund-2": DatasetLabel(
            score_name="answer_quality",
            expected_value=1.0,
            expected_passed=True,
            expected_verdict="grounded",
        ),
        "policy-1": DatasetLabel(
            score_name="answer_quality",
            expected_value=0.0,
            expected_passed=False,
            expected_verdict="ungrounded",
        ),
    }
    dataset = dataset.model_copy(
        update={
            "records": [
                record.model_copy(update={"labels": [labels_by_case[record.case_id]]})
                for record in dataset.records
            ]
        }
    )
    split = split_dataset(
        dataset,
        train_ratio=0.5,
        validation_ratio=0.25,
        test_ratio=0.25,
        seed=7,
    )
    summary = summarize_dataset(split)

    registry = EvaluatorRegistry()
    registry.register(LLMJudgeEvaluator("answer_quality_judge", _judge))
    report = evaluate_suite(suite, dataset_to_samples(split), registry=registry)
    calibration = calibrate_judge(report, split, score_name="answer_quality")

    print("Dataset summary:")
    print(summary.model_dump_json(indent=2))
    print("\nEvaluation summary:")
    print(report.summary.model_dump_json(indent=2))
    print("\nCalibration report:")
    print(calibration.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
