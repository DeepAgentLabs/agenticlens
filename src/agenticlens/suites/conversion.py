"""Turn production traces and user feedback into reviewable test cases.

Converted cases are drafts: each is marked `review_status: needs_review` and
records its source (trace/run or feedback ID) so a reviewer can trace it back.
Nothing here decides that recorded behaviour is correct; the reviewer does.

From a trace, a case expects what the successful run did: the same tools in
the same order, and latency/cost within a margin of what was observed. The
recorded output becomes `expected_output` only when asked, because exact
model outputs rarely repeat. Failed runs are skipped: a failure says what
went wrong, not what is right. Use feedback with a `corrected_output` for those.
"""

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml
from agentic_evals import TestCase

from agenticlens.models.trace import Run, RunStatus, Span, SpanType
from agenticlens.suites.models import (
    DOMAIN_KEY,
    REVIEW_STATUS_KEY,
    SOURCE_KEY,
    CaseSource,
    ConversionResult,
    FeedbackBatch,
    FeedbackRecord,
    SkippedItem,
)


def _run_input(run: Run) -> Any:
    if run.metadata.get("input") is not None:
        return run.metadata["input"]
    for span in run.spans:
        if span.input_data is not None:
            return span.input_data
    return None


def _run_output(run: Run) -> Any:
    finals = [span for span in run.spans if span.span_type == SpanType.FINAL_RESPONSE]
    for span in reversed(finals or run.spans):
        if span.output_data is not None:
            return span.output_data
    return run.metadata.get("output")


def _tool_sequence(spans: Iterable[Span]) -> list[str]:
    """Tool names of successful tool calls, in order, consecutive repeats collapsed."""
    sequence: list[str] = []
    for span in spans:
        if span.span_type != SpanType.TOOL_CALL or span.status == RunStatus.FAILED:
            continue
        name = span.tool_name or span.name
        if not sequence or sequence[-1] != name:
            sequence.append(name)
    return sequence


def _run_succeeded(run: Run) -> bool:
    if run.task_success is not None:
        return run.task_success
    return run.status == RunStatus.SUCCEEDED


def case_from_run(
    run: Run,
    *,
    latency_margin: float | None = 1.5,
    cost_margin: float | None = 1.5,
    include_output: bool = False,
    case_id: str | None = None,
) -> TestCase:
    """Build a draft case from one successful run.

    Raises `ValueError` when the run failed, has no recorded input, or yields
    no expectation (no tools, latency, cost, or output to check).
    """
    if not _run_succeeded(run):
        raise ValueError("run did not succeed; convert corrected feedback instead")
    run_input = _run_input(run)
    if run_input is None:
        raise ValueError("run has no recorded input (metadata.input or span input_data)")
    data: dict[str, Any] = {}
    tools = _tool_sequence(run.spans)
    if tools:
        data["required_tools"] = sorted(set(tools))
        if len(tools) > 1:
            data["required_tool_order"] = tools
    if latency_margin is not None and run.total_latency_ms > 0:
        data["max_latency_ms"] = round(run.total_latency_ms * latency_margin, 3)
    cost = run.estimated_cost_usd
    if cost_margin is not None and cost is not None and cost > 0:
        data["max_cost_usd"] = round(cost * cost_margin, 8)
    if include_output:
        output = _run_output(run)
        if isinstance(output, str) and output:
            data["expected_output"] = output
    if not data:
        raise ValueError("run has no tool calls, latency, cost, or text output to expect")

    domain = run.task_type or run.metadata.get("domain")
    metadata: dict[str, Any] = {
        SOURCE_KEY: CaseSource(kind="trace", trace_id=run.trace_id, run_id=run.run_id).model_dump(
            exclude_none=True
        ),
        REVIEW_STATUS_KEY: "needs_review",
    }
    if domain:
        metadata[DOMAIN_KEY] = str(domain)
    tags = ["from-trace", *[str(tag) for tag in run.metadata.get("tags", [])]]
    return TestCase(
        id=case_id or f"trace-{run.run_id}",
        name=run.task_id or f"{run.application_name} run {run.run_id[:8]}",
        input=run_input,
        tags=list(dict.fromkeys(tags)),
        metadata=metadata,
        **data,
    )


def cases_from_runs(
    runs: Iterable[Run],
    *,
    latency_margin: float | None = 1.5,
    cost_margin: float | None = 1.5,
    include_output: bool = False,
) -> ConversionResult:
    """Convert every run it can; report the rest as skipped with a reason."""
    result = ConversionResult()
    seen: set[str] = set()
    for run in runs:
        if run.run_id in seen:
            result.skipped.append(SkippedItem(source_id=run.run_id, reason="duplicate run_id"))
            continue
        seen.add(run.run_id)
        try:
            result.cases.append(
                case_from_run(
                    run,
                    latency_margin=latency_margin,
                    cost_margin=cost_margin,
                    include_output=include_output,
                )
            )
        except ValueError as exc:
            result.skipped.append(SkippedItem(source_id=run.run_id, reason=str(exc)))
    return result


def load_feedback(path: Path) -> list[FeedbackRecord]:
    """Load feedback from JSON/YAML (`{"feedback": [...]}` or a list) or JSON Lines."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        data: Any = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        data = json.loads(text) if suffix == ".json" else yaml.safe_load(text)
    if isinstance(data, list):
        data = {"feedback": data}
    return FeedbackBatch.model_validate(data).feedback


def _is_positive(record: FeedbackRecord) -> bool:
    if record.rating is not None:
        return record.rating == "positive"
    return record.score is not None and record.score >= 0.5


def case_from_feedback(
    record: FeedbackRecord, *, runs: Mapping[str, Run] | None = None
) -> TestCase:
    """Build a draft case from one feedback record.

    The expected output is the corrected output when given, otherwise the
    output the user rated positively. A missing input is taken from the run
    the feedback names (by `run_id` or `trace_id`) when `runs` has it.
    """
    run = None
    if runs:
        run = runs.get(record.run_id or "") or runs.get(record.trace_id or "")
    case_input = record.input if record.input is not None else (_run_input(run) if run else None)
    if case_input is None:
        raise ValueError("feedback has no input and names no known run")
    if record.corrected_output:
        expected = record.corrected_output
    elif _is_positive(record) and record.output:
        expected = record.output
    elif _is_positive(record):
        raise ValueError("positive feedback has no output to confirm")
    else:
        raise ValueError("negative feedback needs a corrected_output to define the expectation")

    metadata: dict[str, Any] = {
        **record.metadata,
        SOURCE_KEY: CaseSource(
            kind="feedback",
            feedback_id=record.feedback_id,
            trace_id=record.trace_id or (run.trace_id if run else None),
            run_id=record.run_id or (run.run_id if run else None),
        ).model_dump(exclude_none=True),
        REVIEW_STATUS_KEY: "needs_review",
        "feedback_rating": "positive" if _is_positive(record) else "negative",
    }
    if record.comment:
        metadata["feedback_comment"] = record.comment
    if not _is_positive(record) and record.output:
        metadata["rejected_output"] = record.output
    domain = record.domain or (run.task_type if run else None)
    if domain:
        metadata[DOMAIN_KEY] = domain
    tags = ["from-feedback", *record.tags]
    return TestCase(
        id=f"feedback-{record.feedback_id}",
        name=f"Feedback {record.feedback_id}",
        input=case_input,
        expected_output=expected,
        tags=list(dict.fromkeys(tags)),
        metadata=metadata,
    )


def cases_from_feedback(
    records: Iterable[FeedbackRecord], *, runs: Iterable[Run] = ()
) -> ConversionResult:
    """Convert every feedback record it can; report the rest as skipped with a reason."""
    by_id: dict[str, Run] = {}
    for run in runs:
        by_id[run.run_id] = run
        by_id.setdefault(run.trace_id, run)
    result = ConversionResult()
    for record in records:
        try:
            result.cases.append(case_from_feedback(record, runs=by_id))
        except ValueError as exc:
            result.skipped.append(SkippedItem(source_id=record.feedback_id, reason=str(exc)))
    return result
