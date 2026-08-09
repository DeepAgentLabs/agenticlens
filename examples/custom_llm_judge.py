"""Provider-neutral LLM judge integration using the AgenticLens evaluator contract."""

from agenticlens.evaluation import (
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    Score,
    TestCase,
    TestSuite,
    evaluate_suite,
)
from agenticlens.models.trace import Run, RunStatus


def call_your_model(context: EvaluationContext) -> Score:
    """Replace this deterministic example with any provider or local model call."""
    rubric = str(context.config.config["rubric"])
    correct = "42" in context.sample.output
    return Score(
        name="answer_quality",
        value=0.95 if correct else 0.1,
        passed=correct,
        explanation=f"Judge applied rubric: {rubric}",
        metadata={"judge_model": "replace-with-your-model"},
    )


registry = EvaluatorRegistry()
registry.register(LLMJudgeEvaluator("answer_quality_judge", call_your_model))

suite = TestSuite(
    name="Custom judge example",
    version="1.0",
    cases=[
        TestCase(
            id="answer",
            name="Answer quality",
            evaluators=[
                EvaluatorConfig(
                    name="answer_quality_judge",
                    threshold=0.8,
                    config={"rubric": "The answer must be correct and concise."},
                )
            ],
        )
    ],
)
sample = EvaluationSample(
    case_id="answer",
    output="The combined total is 42.",
    trace=Run(
        application_name="custom-judge-example",
        status=RunStatus.SUCCEEDED,
        task_success=True,
    ),
)
report = evaluate_suite(suite, [sample], registry=registry)
print(report.model_dump_json(indent=2))
