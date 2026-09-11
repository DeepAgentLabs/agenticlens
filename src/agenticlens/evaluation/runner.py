import json
import urllib.error
import urllib.request
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, SchemaError
from referencing import Registry
from referencing.exceptions import Unresolvable

from agenticlens.evaluation.evaluators import EvaluationContext, EvaluatorRegistry
from agenticlens.evaluation.models import (
    CaseEvaluation,
    EvaluationReport,
    EvaluationSample,
    EvaluationSummary,
    HTTPTarget,
    LiveTarget,
    PythonTarget,
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


def _lookup_path(payload: Any, dotted_path: str) -> tuple[bool, Any]:
    current = payload
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def _schema_validator(schema: dict[str, Any]) -> Any:
    dialect = schema.get("$schema", "https://json-schema.org/draft/2020-12/schema")
    if dialect != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError("output_json_schema supports JSON Schema Draft 2020-12 only")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ValueError(f"Invalid output_json_schema: {exc.message}") from exc
    # Resolve embedded references only; never fetch schemas from the network.
    return Draft202012Validator(schema, registry=Registry())


def _validate_json_schema(payload: Any, schema: dict[str, Any]) -> tuple[bool, str]:
    validator = _schema_validator(schema)
    try:
        error = next(validator.iter_errors(payload), None)
    except Unresolvable as exc:
        raise ValueError(f"Unresolvable output_json_schema reference: {exc}") from exc
    if error is not None:
        return False, f"Output violates JSON Schema at {error.json_path}: {error.message}"
    return True, "Output matches the configured JSON Schema Draft 2020-12."


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"Non-finite JSON constant {value} is not allowed")


def _turn_count(sample: EvaluationSample) -> int | None:
    metadata_turns = sample.trace.metadata.get("turn_count")
    if isinstance(metadata_turns, int) and metadata_turns > 0:
        return metadata_turns
    return None


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
    parsed_output: Any | None = None
    output_json_error: str | None = None
    if case.output_json_schema is not None or case.required_output_fields:
        try:
            parsed_output = json.loads(output, parse_constant=_reject_json_constant)
        except ValueError as exc:
            output_json_error = str(exc)
    if case.output_json_schema is not None:
        if output_json_error is not None:
            scores.append(
                Score(
                    name="json_schema",
                    value=0.0,
                    passed=False,
                    explanation=f"Output is not valid JSON: {output_json_error}.",
                )
            )
        else:
            valid, reason = _validate_json_schema(parsed_output, case.output_json_schema)
            scores.append(
                Score(
                    name="json_schema",
                    value=float(valid),
                    passed=valid,
                    explanation=reason,
                )
            )
    for field_path in case.required_output_fields:
        exists = (
            output_json_error is None
            and parsed_output is not None
            and _lookup_path(parsed_output, field_path)[0]
        )
        scores.append(
            Score(
                name=f"required_field:{field_path}",
                value=float(exists),
                passed=exists,
                explanation=f"Output contains required field {field_path!r}."
                if exists
                else (
                    "Output is not valid JSON, so required field "
                    f"{field_path!r} could not be checked."
                    if output_json_error is not None
                    else f"Output is missing required field {field_path!r}."
                ),
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
    for tool_name, required_args in case.required_tool_arguments.items():
        matching_spans = [span for span in sample.trace.spans if span.tool_name == tool_name]
        args_present = False
        for span in matching_spans:
            tool_args = span.attributes.get("tool_args")
            if isinstance(tool_args, dict) and all(arg in tool_args for arg in required_args):
                args_present = True
                break
        scores.append(
            Score(
                name=f"tool_args:{tool_name}",
                value=float(args_present),
                passed=args_present,
                explanation=f"Tool {tool_name!r} included required arguments {required_args}."
                if args_present
                else f"Tool {tool_name!r} did not include required arguments {required_args}.",
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
    if case.max_turns is not None:
        turns = _turn_count(sample)
        passed = turns is not None and turns <= case.max_turns
        scores.append(
            Score(
                name="turn_count_threshold",
                value=float(passed),
                passed=passed,
                explanation=(
                    f"Turn count {turns} {'meets' if passed else 'exceeds'} the "
                    f"{case.max_turns} turn limit."
                    if turns is not None
                    else (
                        "Trace metadata is missing a positive integer turn_count, "
                        "so the max_turns check could not be evaluated."
                    )
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


def _load_python_callable(callable_path: str) -> Any:
    """Load a trusted Python live target from module:function or path.py:function."""
    module_name, _, attr_path = callable_path.rpartition(":")
    if not module_name or not attr_path:
        raise ValueError("python target callable_path must be in module:function format")
    try:
        target: Any = import_module(module_name)
    except ModuleNotFoundError as exc:
        file_path = Path(module_name)
        if not file_path.exists():
            raise
        spec = spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Unable to load Python target from {file_path}") from exc
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        target = module
    for part in attr_path.split("."):
        target = getattr(target, part)
    return target


def run_live_suite(
    suite: TestSuite,
    target: LiveTarget,
    *,
    registry: EvaluatorRegistry | None = None,
) -> EvaluationReport:
    """Run a trusted live target against every case in a suite.

    Live targets are intentionally powerful developer-facing integrations:
    Python targets execute local code and HTTP targets can reach arbitrary URLs.
    Only use trusted suite files and trusted target definitions.
    """
    samples: list[EvaluationSample] = []
    if isinstance(target, PythonTarget):
        callable_target = _load_python_callable(target.callable_path)
        for case in suite.cases:
            result = callable_target(case.input, case=case)
            sample = EvaluationSample.model_validate({**result, "case_id": case.id})
            samples.append(sample)
    elif isinstance(target, HTTPTarget):
        for case in suite.cases:
            request = urllib.request.Request(
                target.url,
                data=json.dumps({"input": case.input, "case_id": case.id}).encode("utf-8"),
                headers={"Content-Type": "application/json", **target.headers},
                method=target.method.upper(),
            )
            try:
                with urllib.request.urlopen(request, timeout=target.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.URLError as exc:
                raise ValueError(f"HTTP target request failed for case {case.id!r}: {exc}") from exc
            sample = EvaluationSample.model_validate({**payload, "case_id": case.id})
            samples.append(sample)
    else:
        raise ValueError(f"Unsupported live target kind: {target.kind}")
    return evaluate_suite(suite, samples, registry=registry)


def evaluate_suite(
    suite: TestSuite,
    samples: list[EvaluationSample],
    *,
    registry: EvaluatorRegistry | None = None,
) -> EvaluationReport:
    case_ids = [case.id for case in suite.cases]
    if not case_ids or len(case_ids) != len(set(case_ids)):
        raise ValueError("suite must contain nonempty, unique case IDs")
    for case in suite.cases:
        if case.output_json_schema is not None:
            _schema_validator(case.output_json_schema)
    by_case: dict[str, EvaluationSample] = {}
    expected = set(case_ids)
    for supplied in samples:
        if supplied.case_id in by_case:
            raise ValueError(f"Duplicate sample case ID: {supplied.case_id!r}")
        if supplied.case_id not in expected:
            raise ValueError(f"Unknown sample case ID: {supplied.case_id!r}")
        by_case[supplied.case_id] = supplied
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
            total_cost_usd=sum(costs) if len(costs) == len(results) else None,
            average_latency_ms=sum(result.latency_ms for result in results) / len(results),
        ),
        cases=results,
    )
