"""Bridge AgenticLens's own `Run`/`Span` trace schema into `agentic_evals`'s
minimal, tool-agnostic `EvalTrace`/`EvalSpan` shape.

`agentic_evals` deliberately doesn't know about AgenticLens's `Run` (see its
README) — this is the one place that direction gets bridged, so anyone
building an `EvaluationSample` from an AgenticLens `Run` (e.g. one just
captured live, or imported from OTLP) doesn't have to hand-roll the
conversion themselves.
"""

from datetime import datetime
from typing import Any

from agentic_evals import EvalSpan, EvalTrace

from agenticlens.models.trace import Run


def to_eval_trace(run: Run) -> EvalTrace:
    return EvalTrace(
        trace_id=run.trace_id,
        spans=[
            EvalSpan(tool_name=span.tool_name, attributes=dict(span.attributes))
            for span in run.spans
        ],
        total_latency_ms=run.total_latency_ms,
        estimated_cost_usd=run.estimated_cost_usd,
        metadata=dict(run.metadata),
    )


def _parse_datetime(value: Any) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def to_eval_trace_dict(payload: Any) -> Any:
    """Normalize a raw trace payload into `EvalTrace`'s dict shape.

    Live-target callables/HTTP endpoints and older saved sample files can
    still emit AgenticLens's `Run`-shaped trace (`started_at`/`completed_at`
    timestamps, per-span `estimated_cost_usd`) rather than `EvalTrace`'s
    (`total_latency_ms`, trace-level `estimated_cost_usd`). Passed through
    unadapted, `agentic_evals`'s pydantic models silently ignore those
    unknown fields, defaulting latency/cost checks to 0/None. This is the
    dict-level counterpart of `to_eval_trace()`, used as the `trace_adapter`
    hook for `agentic_evals`'s `load_samples()`/`run_live_suite()`.
    """
    if not isinstance(payload, dict) or "total_latency_ms" in payload:
        return payload  # not a dict, or already EvalTrace-shaped

    spans = payload.get("spans") or []
    started_at = payload.get("started_at")
    completed_at = payload.get("completed_at")
    total_latency_ms = 0.0
    if started_at is not None and completed_at is not None:
        total_latency_ms = max(
            0.0,
            (_parse_datetime(completed_at) - _parse_datetime(started_at)).total_seconds() * 1000,
        )

    span_costs = [span.get("estimated_cost_usd") for span in spans]
    estimated_cost_usd = (
        sum(cost for cost in span_costs if cost is not None)
        if span_costs and all(cost is not None for cost in span_costs)
        else None
    )

    return {
        "trace_id": payload.get("trace_id", ""),
        "spans": [
            {"tool_name": span.get("tool_name"), "attributes": span.get("attributes") or {}}
            for span in spans
        ],
        "total_latency_ms": total_latency_ms,
        "estimated_cost_usd": estimated_cost_usd,
        "metadata": payload.get("metadata") or {},
    }
