"""Compact trace builders for optimization tests."""

from datetime import datetime, timedelta, timezone
from typing import Any

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

START = datetime(2026, 10, 1, tzinfo=timezone.utc)


def span(
    run_id: str,
    index: int,
    span_type: SpanType,
    *,
    name: str | None = None,
    tokens: tuple[int, int] = (100, 10),
    cost: float | None = 0.001,
    latency_ms: float = 50.0,
    status: RunStatus = RunStatus.SUCCEEDED,
    **fields: Any,
) -> Span:
    return Span(
        span_id=f"{run_id}-{index}",
        name=name or span_type.value,
        span_type=span_type,
        started_at=START,
        completed_at=START + timedelta(milliseconds=latency_ms),
        latency_ms=latency_ms,
        input_tokens=tokens[0],
        output_tokens=tokens[1],
        estimated_cost_usd=cost,
        status=status,
        **fields,
    )


def run(
    run_id: str,
    spans: list[Span],
    *,
    variant_id: str | None = None,
    task_success: bool | None = None,
    latency_ms: float = 1000.0,
) -> Run:
    return Run(
        run_id=run_id,
        application_name="test-app",
        variant_id=variant_id,
        started_at=START,
        completed_at=START + timedelta(milliseconds=latency_ms),
        status=RunStatus.SUCCEEDED,
        spans=spans,
        task_success=task_success,
    )


def chunks(used: list[int], total: int = 8, tokens: int = 100) -> list[dict[str, Any]]:
    return [{"rank": r, "tokens": tokens, "used": r in used} for r in range(1, total + 1)]


def retrieval_run(run_id: str, used: list[int], *, cost: float | None = 0.01) -> Run:
    return run(
        run_id,
        [
            span(run_id, 1, SpanType.RETRIEVAL, name="kb", attributes={"chunks": chunks(used)}),
            span(run_id, 2, SpanType.MODEL_CALL, tokens=(900, 100), cost=cost),
        ],
    )
