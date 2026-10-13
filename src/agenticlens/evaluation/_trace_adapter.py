"""Bridge AgenticLens's own `Run`/`Span` trace schema into `agentic_evals`'s
minimal, tool-agnostic `EvalTrace`/`EvalSpan` shape.

`agentic_evals` deliberately doesn't know about AgenticLens's `Run` (see its
README) — this is the one place that direction gets bridged, so anyone
building an `EvaluationSample` from an AgenticLens `Run` (e.g. one just
captured live, or imported from OTLP) doesn't have to hand-roll the
conversion themselves.

Span semantics: `EvalSpan` keeps only `tool_name` and `attributes`, so the
adapter also copies what trace-aware evaluators need into namespaced
attributes (`agenticlens.span_type`, `agenticlens.name`,
`agenticlens.agent_name`, `agenticlens.status`, `agenticlens.input_fingerprint`,
and `agenticlens.retrieved` for retrieval output), and the run's outcome into
`metadata` (`agenticlens.run_status`, `agenticlens.task_success`). Existing
attributes are never overwritten.

Cost provenance: AgenticLens span costs are computed from token counts and a
price table, so a `Run`'s cost is `estimated` unless the producer says
otherwise with `metadata["cost_source"] = "measured"` (for example, a cost
read back from a provider invoice).
"""

import hashlib
import json
from datetime import datetime
from typing import Any

from agentic_evals import EvalSpan, EvalTrace

from agenticlens.models.trace import Run

LENS_PREFIX = "agenticlens."


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _lens_attributes(span: dict[str, Any]) -> dict[str, Any]:
    """Namespaced span semantics for trace-aware evaluators."""
    attributes: dict[str, Any] = dict(span.get("attributes") or {})
    fields = {
        "span_type": span.get("span_type"),
        "name": span.get("name"),
        "agent_name": span.get("agent_name"),
        "status": span.get("status"),
        "span_id": span.get("span_id"),
        "parent_span_id": span.get("parent_span_id"),
    }
    if span.get("input_reference"):
        fields["input_fingerprint"] = f"ref:{span['input_reference']}"
    elif span.get("input_data") is not None:
        fields["input_fingerprint"] = _fingerprint(span["input_data"])
    elif attributes.get("tool_args") is not None:
        # Canonical JSON, so equal argument dicts match whatever their key order.
        fields["input_fingerprint"] = _fingerprint(attributes["tool_args"])
    if span.get("span_type") == "retrieval" and span.get("output_data") is not None:
        fields["retrieved"] = span["output_data"]
    for key, value in fields.items():
        if value is not None:
            attributes.setdefault(LENS_PREFIX + key, value)
    return attributes


def _lens_metadata(metadata: dict[str, Any], status: Any, task_success: Any) -> dict[str, Any]:
    enriched = dict(metadata)
    if status is not None:
        enriched.setdefault(LENS_PREFIX + "run_status", status)
    if task_success is not None:
        enriched.setdefault(LENS_PREFIX + "task_success", task_success)
    return enriched


COST_SOURCES = ("measured", "estimated")


def _cost_source(declared: Any, cost: float | None) -> str | None:
    if cost is None:
        return None
    return declared if declared in COST_SOURCES else "estimated"


def to_eval_trace(run: Run) -> EvalTrace:
    cost = run.estimated_cost_usd
    return EvalTrace.model_validate(
        {
            "trace_id": run.trace_id,
            "spans": [
                EvalSpan(
                    tool_name=span.tool_name,
                    attributes=_lens_attributes(span.model_dump(mode="json")),
                )
                for span in run.spans
            ],
            "total_latency_ms": run.total_latency_ms,
            "estimated_cost_usd": cost,
            "cost_source": _cost_source(run.metadata.get("cost_source"), cost),
            "metadata": _lens_metadata(run.metadata, run.status.value, run.task_success),
        }
    )


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    # Python 3.10's fromisoformat() rejects the "Z" suffix pydantic emits for UTC.
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(text)


_RUN_KEYS = frozenset({"started_at", "completed_at", "application_name", "run_id"})
_RUN_SPAN_KEYS = frozenset({"span_type", "estimated_cost_usd", "span_id"})


def _is_run_shaped(payload: dict[str, Any]) -> bool:
    """True for AgenticLens `Run` payloads; `EvalTrace` payloads pass through.

    `total_latency_ms` only appears on `EvalTrace`. Otherwise a payload is
    `Run`-shaped when it carries a `Run`-only key or a span with a `Span`-only
    key, so an `EvalTrace` that simply omits `total_latency_ms` keeps its
    trace-level cost instead of having it recomputed from spans.
    """
    if "total_latency_ms" in payload:
        return False
    if _RUN_KEYS & payload.keys():
        return True
    spans = payload.get("spans") or []
    return any(isinstance(span, dict) and _RUN_SPAN_KEYS & span.keys() for span in spans)


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
    if not isinstance(payload, dict) or not _is_run_shaped(payload):
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
    metadata = payload.get("metadata") or {}

    return {
        "trace_id": payload.get("trace_id", ""),
        "spans": [
            {
                "tool_name": span.get("tool_name"),
                "attributes": _lens_attributes(span) if isinstance(span, dict) else {},
            }
            for span in spans
        ],
        "total_latency_ms": total_latency_ms,
        "estimated_cost_usd": estimated_cost_usd,
        "cost_source": _cost_source(
            payload.get("cost_source", metadata.get("cost_source")), estimated_cost_usd
        ),
        "metadata": _lens_metadata(metadata, payload.get("status"), payload.get("task_success")),
    }
