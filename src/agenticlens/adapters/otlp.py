"""Convert OTLP/HTTP JSON trace exports into AgenticLens `Run`/`Span` objects.

This is the inverse of `agenticlens.exporters.otlp_trace_exporter`: it reads
OTLP/HTTP JSON (an OTel Collector's file export, another vendor's trace dump,
or AgenticLens's own exported payloads) rather than emitting it. Every field
mapping prefers AgenticLens's own `agenticlens.*` attributes (a perfect
round-trip with the exporter), falls back to the OpenTelemetry GenAI semantic
convention (`gen_ai.*`, including documented legacy attribute names), and
never fabricates a value it cannot find — an unpriced span stays unpriced.
Any attribute not consumed by a mapping is preserved verbatim on
`Span.attributes` so importing never silently discards data.
"""

import json
import re
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

_OTLP_STATUS_ERROR = 2
_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9_-]")


def safe_trace_filename(trace_id: str) -> str:
    """Turn an arbitrary, untrusted trace id into a safe `<name>.json` stem.

    A `traceId` is an opaque string from whoever sent the OTLP payload —
    never trust it as a path component. Every character outside
    `[A-Za-z0-9_-]` (path separators, `..`, a leading `/` that would make it
    absolute, etc.) is replaced, so the result can never escape a configured
    save directory or collide with an unrelated absolute path.
    """
    safe = _UNSAFE_FILENAME_CHARS.sub("_", trace_id)
    return safe or "unknown-trace"


_GEN_AI_OPERATION_TO_SPAN_TYPE: dict[str, SpanType] = {
    "chat": SpanType.MODEL_CALL,
    "generate_content": SpanType.MODEL_CALL,
    "text_completion": SpanType.MODEL_CALL,
    "embeddings": SpanType.MODEL_CALL,
    "execute_tool": SpanType.TOOL_CALL,
    "create_agent": SpanType.DELEGATION,
    "invoke_agent": SpanType.DELEGATION,
}


def load_otlp_export(path: Path) -> list[Run]:
    """Load one OTLP/HTTP JSON file, or every ``*.json`` file in a directory."""
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    if not files:
        raise ValueError(f"No JSON OTLP exports found at {path}")

    runs: list[Run] = []
    for file in files:
        payload = json.loads(file.read_text(encoding="utf-8"))
        runs.extend(parse_otlp_payload(payload))
    return runs


def parse_otlp_payload(payload: dict[str, Any]) -> list[Run]:
    """Parse an OTLP/HTTP JSON payload into one `Run` per distinct trace id."""
    if "resourceSpans" not in payload:
        raise ValueError("Not an OTLP/HTTP JSON trace export: missing 'resourceSpans'")

    trace_order: list[str] = []
    spans_by_trace: dict[str, list[dict[str, Any]]] = {}
    resource_attrs_by_trace: dict[str, dict[str, Any]] = {}

    for resource_span in payload.get("resourceSpans", []):
        resource_attrs = _decode_attributes(resource_span.get("resource", {}).get("attributes", []))
        for scope_span in resource_span.get("scopeSpans", []):
            for span_dict in scope_span.get("spans", []):
                trace_id = span_dict.get("traceId")
                if not trace_id:
                    raise ValueError("OTLP span is missing a traceId")
                if "spanId" not in span_dict:
                    raise ValueError(f"OTLP span {span_dict.get('name')!r} is missing a spanId")
                if trace_id not in spans_by_trace:
                    trace_order.append(trace_id)
                    spans_by_trace[trace_id] = []
                    resource_attrs_by_trace[trace_id] = resource_attrs
                spans_by_trace[trace_id].append(span_dict)

    return [
        _build_run(trace_id, resource_attrs_by_trace[trace_id], spans_by_trace[trace_id])
        for trace_id in trace_order
    ]


def _build_run(
    trace_id: str, resource_attrs: dict[str, Any], span_dicts: list[dict[str, Any]]
) -> Run:
    known_ids = {span_dict["spanId"] for span_dict in span_dicts}
    spans = [_build_span(span_dict, known_ids) for span_dict in span_dicts]

    started_at = min((span.started_at for span in spans), default=None)
    completed_at = max(
        (span.completed_at for span in spans if span.completed_at is not None), default=None
    )
    status = (
        RunStatus.FAILED
        if any(span.status is RunStatus.FAILED for span in spans)
        else RunStatus.SUCCEEDED
    )
    raw_status = resource_attrs.get("agenticlens.status")
    if isinstance(raw_status, str):
        with suppress(ValueError):
            status = RunStatus(raw_status)  # falls back to span-derived inference if invalid

    run_kwargs: dict[str, Any] = {
        "trace_id": trace_id,
        "application_name": _as_str(resource_attrs.get("service.name")) or "imported-otlp-trace",
        "spans": spans,
        "status": status,
    }
    if started_at is not None:
        run_kwargs["started_at"] = started_at
    if completed_at is not None:
        run_kwargs["completed_at"] = completed_at

    if "agenticlens.run_id" in resource_attrs:
        run_kwargs["run_id"] = resource_attrs["agenticlens.run_id"]
    for field, key in (
        ("framework", "agenticlens.framework"),
        ("framework_version", "agenticlens.framework_version"),
        ("task_id", "agenticlens.task_id"),
        ("task_type", "agenticlens.task_type"),
        ("experiment_id", "agenticlens.experiment_id"),
        ("variant_id", "agenticlens.variant_id"),
        ("error_type", "agenticlens.error_type"),
    ):
        if key in resource_attrs:
            run_kwargs[field] = resource_attrs[key]
    if "agenticlens.task_success" in resource_attrs:
        run_kwargs["task_success"] = bool(resource_attrs["agenticlens.task_success"])

    metadata: dict[str, Any] = {}
    unrecognized_resource_attrs: dict[str, Any] = {}
    consumed_resource_keys = {
        "service.name",
        "agenticlens.run_id",
        "agenticlens.status",
        "agenticlens.framework",
        "agenticlens.framework_version",
        "agenticlens.task_id",
        "agenticlens.task_type",
        "agenticlens.experiment_id",
        "agenticlens.variant_id",
        "agenticlens.task_success",
        "agenticlens.error_type",
    }
    for key, value in resource_attrs.items():
        if key.startswith("agenticlens.metadata."):
            metadata[key.removeprefix("agenticlens.metadata.")] = value
        elif key not in consumed_resource_keys and not key.startswith("service."):
            unrecognized_resource_attrs[key] = value
    if unrecognized_resource_attrs:
        metadata["otlp_import_resource_attributes"] = unrecognized_resource_attrs
    run_kwargs["metadata"] = metadata

    return Run(**run_kwargs)


def _build_span(span_dict: dict[str, Any], known_ids: set[str]) -> Span:
    attrs = _decode_attributes(span_dict.get("attributes", []))
    parent_id = span_dict.get("parentSpanId") or None
    if parent_id is not None and parent_id not in known_ids:
        parent_id = None  # sampled/filtered export: treat as a root span, not an error

    started_at = _from_unix_nano(span_dict.get("startTimeUnixNano"))
    completed_at = _from_unix_nano(span_dict.get("endTimeUnixNano"))
    latency_ms = _as_float(attrs.get("agenticlens.latency_ms"))
    if latency_ms is None and started_at is not None and completed_at is not None:
        latency_ms = (completed_at - started_at).total_seconds() * 1000

    error_type, error_message = _exception_event(span_dict)

    span_kwargs: dict[str, Any] = {
        "span_id": span_dict["spanId"],
        "parent_span_id": parent_id,
        "name": span_dict.get("name", "unnamed span"),
        "span_type": _span_type(attrs),
        "status": (
            RunStatus.FAILED
            if span_dict.get("status", {}).get("code") == _OTLP_STATUS_ERROR
            else RunStatus.SUCCEEDED
        ),
        "agent_name": _first_str(attrs, "agenticlens.agent_name", "gen_ai.agent.name"),
        "model_name": _first_str(
            attrs, "agenticlens.model_name", "gen_ai.request.model", "gen_ai.response.model"
        ),
        "provider": _first_str(
            attrs, "agenticlens.provider", "gen_ai.provider.name", "gen_ai.system"
        ),
        "tool_name": _first_str(attrs, "agenticlens.tool_name", "gen_ai.tool.name"),
        "input_tokens": _first_int(
            attrs,
            "agenticlens.input_tokens",
            "gen_ai.usage.input_tokens",
            "gen_ai.usage.prompt_tokens",
        )
        or 0,
        "output_tokens": _first_int(
            attrs,
            "agenticlens.output_tokens",
            "gen_ai.usage.output_tokens",
            "gen_ai.usage.completion_tokens",
        )
        or 0,
        "estimated_cost_usd": _as_float(attrs.get("agenticlens.estimated_cost_usd")),
        "retry_number": _as_int(attrs.get("agenticlens.retry_number")),
        "error_type": _as_str(attrs.get("agenticlens.error_type")) or error_type,
        "error_message": _as_str(attrs.get("agenticlens.error_message")) or error_message,
        "input_reference": _as_str(attrs.get("agenticlens.input_reference")),
        "output_reference": _as_str(attrs.get("agenticlens.output_reference")),
        "input_data": attrs.get("agenticlens.input_data"),
        "output_data": attrs.get("agenticlens.output_data"),
        "latency_ms": latency_ms or 0.0,
    }
    if started_at is not None:
        span_kwargs["started_at"] = started_at
    if completed_at is not None:
        span_kwargs["completed_at"] = completed_at

    span_kwargs["attributes"] = _unmapped_attributes(attrs)
    return Span(**span_kwargs)


_CONSUMED_SPAN_ATTR_PREFIXES = ("agenticlens.span_type",)
_CONSUMED_SPAN_ATTR_KEYS = {
    "agenticlens.agent_name",
    "agenticlens.model_name",
    "agenticlens.provider",
    "agenticlens.tool_name",
    "agenticlens.input_tokens",
    "agenticlens.output_tokens",
    "agenticlens.total_tokens",
    "agenticlens.estimated_cost_usd",
    "agenticlens.retry_number",
    "agenticlens.error_type",
    "agenticlens.error_message",
    "agenticlens.latency_ms",
    "agenticlens.input_reference",
    "agenticlens.output_reference",
    "agenticlens.input_data",
    "agenticlens.output_data",
    "gen_ai.agent.name",
    "gen_ai.request.model",
    "gen_ai.response.model",
    "gen_ai.provider.name",
    "gen_ai.system",
    "gen_ai.tool.name",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.prompt_tokens",
    "gen_ai.usage.completion_tokens",
    "gen_ai.operation.name",
}


def _unmapped_attributes(attrs: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in attrs.items()
        if key not in _CONSUMED_SPAN_ATTR_KEYS and not key.startswith(_CONSUMED_SPAN_ATTR_PREFIXES)
    }


def _span_type(attrs: dict[str, Any]) -> SpanType:
    raw = attrs.get("agenticlens.span_type")
    if isinstance(raw, str):
        try:
            return SpanType(raw)
        except ValueError:
            pass

    operation = attrs.get("gen_ai.operation.name")
    if isinstance(operation, str) and operation in _GEN_AI_OPERATION_TO_SPAN_TYPE:
        return _GEN_AI_OPERATION_TO_SPAN_TYPE[operation]

    if "gen_ai.tool.name" in attrs:
        return SpanType.TOOL_CALL

    if any(key.startswith("gen_ai.") for key in attrs):
        return SpanType.MODEL_CALL

    return SpanType.CUSTOM


def _exception_event(span_dict: dict[str, Any]) -> tuple[str | None, str | None]:
    for event in span_dict.get("events", []):
        if event.get("name") != "exception":
            continue
        event_attrs = _decode_attributes(event.get("attributes", []))
        return (
            _as_str(event_attrs.get("exception.type")),
            _as_str(event_attrs.get("exception.message")),
        )
    return None, None


def _decode_attributes(attribute_list: list[dict[str, Any]]) -> dict[str, Any]:
    return {item["key"]: _decode_any_value(item.get("value", {})) for item in attribute_list}


def _decode_any_value(value: dict[str, Any]) -> Any:
    if "stringValue" in value:
        return value["stringValue"]
    if "intValue" in value:
        try:
            return int(value["intValue"])
        except (TypeError, ValueError):
            return None
    if "doubleValue" in value:
        return value["doubleValue"]
    if "boolValue" in value:
        return value["boolValue"]
    if "arrayValue" in value:
        return [_decode_any_value(item) for item in value["arrayValue"].get("values", [])]
    if "kvlistValue" in value:
        return {
            item["key"]: _decode_any_value(item.get("value", {}))
            for item in value["kvlistValue"].get("values", [])
        }
    return None


def _from_unix_nano(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        nanos = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(nanos / 1_000_000_000, tz=timezone.utc)


def _first_str(attrs: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        found = _as_str(attrs.get(key))
        if found is not None:
            return found
    return None


def _first_int(attrs: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        found = _as_int(attrs.get(key))
        if found is not None:
            return found
    return None


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
