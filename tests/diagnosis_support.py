"""Small builders for diagnosis tests: spans on a millisecond clock."""

from datetime import datetime, timedelta, timezone
from typing import Any

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)


def span(
    span_id: str,
    name: str,
    span_type: SpanType | str,
    start: float,
    duration: float = 10.0,
    status: str = "succeeded",
    **fields: Any,
) -> Span:
    return Span(
        span_id=span_id,
        name=name,
        span_type=SpanType(span_type),
        started_at=T0 + timedelta(milliseconds=start),
        completed_at=T0 + timedelta(milliseconds=start + duration),
        latency_ms=duration,
        status=RunStatus(status),
        **fields,
    )


def run(
    spans: list[Span],
    *,
    failed: bool = False,
    task_success: bool | None = None,
    duration: float = 1000.0,
    run_id: str = "run-1",
    **fields: Any,
) -> Run:
    return Run(
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        application_name="app",
        started_at=T0,
        completed_at=T0 + timedelta(milliseconds=duration),
        status=RunStatus.FAILED if failed else RunStatus.SUCCEEDED,
        task_success=task_success,
        spans=spans,
        **fields,
    )
