"""Structured judge verdicts, evidence audit, and judge-threshold tuning.

1. A deterministic stand-in judge returns a `JudgeVerdict` (verdict,
   confidence, unsupported claims, missed evidence). `structured_judge()`
   records it on each score with the judge's model and version.
2. `audit_report()` checks every score names its evaluator and version,
   every failed case has a trace, and how complete the cost data is.
3. `tune_judge_threshold()` sweeps pass thresholds against human labels.

    python examples/structured_judge_demo.py

Replace `grounding_judge` with a call to your own model; AgenticLens never
calls a model itself. Use a judge model different from the model being
evaluated -- the same model is skipped as self-confirmation by default.
"""

from agenticlens.evaluation import (
    EvalSpan,
    EvalTrace,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    JudgeVerdict,
    TestCase,
    TestSuite,
    audit_report,
    evaluate_suite,
    judge_verdict,
    structured_judge,
    tune_judge_threshold,
)
from agenticlens.evaluation.calibration import CalibrationDataset

POLICY = {"refund": "30 days", "shipping": "3-5 business days", "warranty": "1 year"}


def grounding_judge(context: EvaluationContext) -> JudgeVerdict:
    """Stand-in judge: checks the answer against the policy fact for its topic."""
    fact = POLICY[context.case.metadata["topic"]]
    answer = context.sample.output
    if fact in answer:
        return JudgeVerdict(verdict="agree", confidence=0.9, rationale="Matches policy.")
    if any(word in answer for word in fact.split()):
        return JudgeVerdict(
            verdict="partially_agree",
            confidence=0.6,
            rationale="Partly matches policy.",
            evidence_missed=[fact],
        )
    return JudgeVerdict(
        verdict="disagree",
        confidence=0.85,
        rationale="Contradicts policy.",
        unsupported_claims=[answer],
        evidence_missed=[fact],
    )


ANSWERS = {
    "refund": "Refunds are accepted within 30 days.",
    "shipping": "Shipping takes 3 days.",
    "warranty": "There is a lifetime warranty.",
}


def main() -> None:
    registry = EvaluatorRegistry()
    registry.register(
        structured_judge(
            "grounding",
            grounding_judge,
            judge_model="judge-model-b",
            version="grounding-prompt-v2",
        )
    )
    suite = TestSuite(
        name="policy-grounding",
        version="1",
        cases=[
            TestCase(
                id=topic,
                name=f"{topic} answer is grounded",
                evaluators=[EvaluatorConfig(name="grounding", threshold=0.5)],
                metadata={"topic": topic, "model": "support-model-a"},
            )
            for topic in POLICY
        ],
    )
    samples = [
        EvaluationSample(
            case_id=topic,
            output=answer,
            trace=EvalTrace(
                trace_id=f"trace-{topic}",
                total_latency_ms=800,
                estimated_cost_usd=0.002,
                cost_source="measured",
                spans=[EvalSpan(tool_name="policy_lookup")],
            ),
        )
        for topic, answer in ANSWERS.items()
    ]
    report = evaluate_suite(suite, samples, registry=registry)

    for case in report.cases:
        score = case.scores[0]
        verdict = judge_verdict(score)
        assert verdict is not None
        print(
            f"{case.case_id:9} {verdict.verdict:16} value={score.value:.1f} "
            f"by {score.evaluator}@{score.evaluator_version} "
            f"unsupported={verdict.unsupported_claims}"
        )

    audit = audit_report(report)
    print(f"\nEvidence audit passed: {audit.passed}; evaluators: {audit.evaluators}")
    print(f"Cost coverage: {audit.cost.priced_cases}/{audit.cost.total_cases} {audit.cost.sources}")

    # Human reviewers say the partially-correct shipping answer should fail.
    labels = CalibrationDataset(
        name="policy-review",
        version="2026-10",
        suite_name=suite.name,
        suite_version=suite.version,
        labels=[
            {"case_id": "refund", "passed": True},
            {"case_id": "shipping", "passed": False},
            {"case_id": "warranty", "passed": False},
        ],
    )
    tuning = tune_judge_threshold(report, labels, evaluator="grounding")
    print(
        f"\nCurrent agreement {tuning.current_agreement_rate:.0%}; "
        f"recommended threshold {tuning.recommended_threshold:.2f} "
        f"-> agreement {tuning.recommended.agreement_rate:.0%}"
    )
    for warning in tuning.warnings:
        print(f"  ! {warning}")


if __name__ == "__main__":
    main()
