import json
from pathlib import Path
from typing import Any

import yaml

from agenticlens.evaluation.evaluators import EvaluationContext, EvaluatorRegistry
from agenticlens.evaluation.models import (
    CaseEvaluation,
    EvaluationReport,
    EvaluationSample,
    EvaluationSummary,
    Score,
    TestCase,
    TestSuite,
)


def _load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def load_suite(path: Path) -> TestSuite:
    return TestSuite.model_validate(_load_data(path))


def load_samples(path: Path) -> list[EvaluationSample]:
    data = _load_data(path)
    items = data["samples"] if isinstance(data, dict) and "samples" in data else data
    return [EvaluationSample.model_validate(item) for item in items]


def _score_case(
    case: TestCase,
    sample: EvaluationSample,
    registry: EvaluatorRegistry | None,
) -> list[Score]:
    scores: list[Score] = []
    output = sample.output.strip()
    if case.expected_output is not None:
        passed = output == case.expected_output.strip()
        scores.append(
            Score(
                name="exact_match",
                value=float(passed),
                passed=passed,
                explanation="Output exactly matches the reference."
                if passed
                else "Output does not exactly match the reference.",
            )
        )
    for expected in case.expected_contains:
        passed = expected.casefold() in output.casefold()
        scores.append(
            Score(
                name=f"contains:{expected}",
                value=float(passed),
                passed=passed,
                explanation=f"Output contains required text: {expected!r}."
                if passed
                else f"Output is missing required text: {expected!r}.",
            )
        )

    tools = {span.tool_name for span in sample.trace.spans if span.tool_name}
    for tool in case.required_tools:
        passed = tool in tools
        scores.append(
            Score(
                name=f"required_tool:{tool}",
                value=float(passed),
                passed=passed,
                explanation=f"Required tool {tool!r} was called."
                if passed
                else f"Required tool {tool!r} was not called.",
            )
        )
    for tool in case.forbidden_tools:
        passed = tool not in tools
        scores.append(
            Score(
                name=f"forbidden_tool:{tool}",
                value=float(passed),
                passed=passed,
                explanation=f"Forbidden tool {tool!r} was not called."
                if passed
                else f"Forbidden tool {tool!r} was called.",
            )
        )
    if case.max_latency_ms is not None:
        passed = sample.trace.total_latency_ms <= case.max_latency_ms
        scores.append(
            Score(
                name="latency_threshold",
                value=float(passed),
                passed=passed,
                explanation=(
                    f"Latency {sample.trace.total_latency_ms:.1f} ms "
                    f"{'meets' if passed else 'exceeds'} the "
                    f"{case.max_latency_ms:.1f} ms limit."
                ),
            )
        )
    if case.max_cost_usd is not None:
        cost = sample.trace.estimated_cost_usd
        passed = cost is not None and cost <= case.max_cost_usd
        scores.append(
            Score(
                name="cost_threshold",
                value=float(passed),
                passed=passed,
                explanation=(
                    f"Cost ${cost:.6f} meets the ${case.max_cost_usd:.6f} limit."
                    if passed and cost is not None
                    else "Cost is unavailable or exceeds the configured limit."
                ),
            )
        )
    for evaluator_config in case.evaluators:
        if registry is None:
            raise ValueError(
                f"test case {case.id!r} requires evaluator {evaluator_config.name!r}, "
                "but no evaluator registry was supplied"
            )
        evaluator = registry.get(evaluator_config.name)
        custom_scores = evaluator.evaluate(
            EvaluationContext(case=case, sample=sample, config=evaluator_config)
        )
        scores.extend(custom_scores)
    return scores


def evaluate_suite(
    suite: TestSuite,
    samples: list[EvaluationSample],
    *,
    registry: EvaluatorRegistry | None = None,
) -> EvaluationReport:
    by_case = {sample.case_id: sample for sample in samples}
    results: list[CaseEvaluation] = []
    for case in suite.cases:
        sample = by_case.get(case.id)
        if sample is None:
            scores = [
                Score(
                    name="sample_available",
                    value=0,
                    passed=False,
                    explanation="No evaluation sample was supplied for this test case.",
                )
            ]
            results.append(
                CaseEvaluation(
                    case_id=case.id,
                    case_name=case.name,
                    passed=False,
                    scores=scores,
                    output="",
                    trace_id="",
                    latency_ms=0,
                )
            )
            continue
        scores = _score_case(case, sample, registry)
        results.append(
            CaseEvaluation(
                case_id=case.id,
                case_name=case.name,
                passed=all(score.passed or not score.required for score in scores),
                scores=scores,
                output=sample.output,
                trace_id=sample.trace.trace_id,
                latency_ms=sample.trace.total_latency_ms,
                cost_usd=sample.trace.estimated_cost_usd,
            )
        )
    passed = sum(result.passed for result in results)
    all_scores = [score.value for result in results for score in result.scores]
    costs = [result.cost_usd for result in results if result.cost_usd is not None]
    return EvaluationReport(
        suite_name=suite.name,
        suite_version=suite.version,
        summary=EvaluationSummary(
            total_cases=len(results),
            passed_cases=passed,
            failed_cases=len(results) - passed,
            pass_rate=passed / len(results),
            average_score=sum(all_scores) / len(all_scores),
            total_cost_usd=sum(costs) if costs else None,
            average_latency_ms=sum(result.latency_ms for result in results) / len(results),
        ),
        cases=results,
    )
