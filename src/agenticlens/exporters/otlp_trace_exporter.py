from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

_DEFAULT_TIMEOUT_SECONDS = 10.0
_INTERNAL_KIND = 1
_CLIENT_KIND = 3


class OTLPTraceExporter:
    """Export AgenticLens runs as OTLP/HTTP JSON traces."""

    def to_payload(self, run: Run) -> dict[str, Any]:
        return {
            "resourceSpans": [
                {
                    "resource": {"attributes": self._resource_attributes(run)},
                    "scopeSpans": [
                        {
                            "scope": {
                                "name": "agenticlens",
                                "version": _agenticlens_version(),
                            },
                            "spans": [self._span_payload(run, span) for span in run.spans],
                        }
                    ],
                }
            ]
        }

    def save(self, run: Run, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_payload(run), indent=2), encoding="utf-8")

    def export(
        self,
        run: Run,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        payload = json.dumps(self.to_payload(run)).encode("utf-8")
        request_headers = {"Content-Type": "application/json", **(headers or {})}
        request = Request(endpoint, data=payload, headers=request_headers, method="POST")
        with urlopen(request, timeout=timeout):
            return

    def _resource_attributes(self, run: Run) -> list[dict[str, Any]]:
        attributes = [
            _string_attribute("service.name", run.application_name),
            _string_attribute("service.namespace", "agenticlens"),
            _string_attribute("service.version", _agenticlens_version()),
            _string_attribute("agenticlens.run_id", run.run_id),
            _string_attribute("agenticlens.status", run.status.value),
        ]
        for key, value in (
            ("agenticlens.framework", run.framework),
            ("agenticlens.framework_version", run.framework_version),
            ("agenticlens.task_id", run.task_id),
            ("agenticlens.task_type", run.task_type),
            ("agenticlens.experiment_id", run.experiment_id),
            ("agenticlens.variant_id", run.variant_id),
        ):
            if value is not None:
                attributes.append(_string_attribute(key, value))
        if run.task_success is not None:
            attributes.append(_attribute("agenticlens.task_success", run.task_success))
        for key, value in sorted(run.metadata.items()):
            attributes.append(_attribute(f"agenticlens.metadata.{key}", value))
        return attributes

    def _span_payload(self, run: Run, span: Span) -> dict[str, Any]:
        ended_at = span.completed_at or run.completed_at or datetime.now(timezone.utc)
        payload = {
            "traceId": _normalize_trace_id(run.trace_id),
            "spanId": _normalize_span_id(span.span_id),
            "parentSpanId": _normalize_parent_span_id(span.parent_span_id),
            "name": span.name,
            "kind": _kind_for(span),
            "startTimeUnixNano": _to_unix_nano(span.started_at),
            "endTimeUnixNano": _to_unix_nano(ended_at),
            "attributes": self._span_attributes(span),
            "status": _status_payload(span),
        }
        events = _events_for(span)
        if events:
            payload["events"] = events
        return payload

    def _span_attributes(self, span: Span) -> list[dict[str, Any]]:
        attributes = [
            _string_attribute("agenticlens.span_type", span.span_type.value),
            _attribute("agenticlens.input_tokens", span.input_tokens),
            _attribute("agenticlens.output_tokens", span.output_tokens),
            _attribute("agenticlens.total_tokens", span.total_tokens),
            _attribute("agenticlens.latency_ms", span.latency_ms),
        ]
        for key, value in (
            ("agenticlens.agent_name", span.agent_name),
            ("agenticlens.model_name", span.model_name),
            ("agenticlens.provider", span.provider),
            ("agenticlens.tool_name", span.tool_name),
            ("agenticlens.input_reference", span.input_reference),
            ("agenticlens.output_reference", span.output_reference),
            ("agenticlens.error_type", span.error_type),
        ):
            if value is not None:
                attributes.append(_string_attribute(key, value))
        if span.retry_number is not None:
            attributes.append(_attribute("agenticlens.retry_number", span.retry_number))
        if span.estimated_cost_usd is not None:
            attributes.append(_attribute("agenticlens.estimated_cost_usd", span.estimated_cost_usd))
        if span.error_message is not None:
            attributes.append(_string_attribute("agenticlens.error_message", span.error_message))
        if span.input_data is not None:
            attributes.append(_attribute("agenticlens.input_data", span.input_data))
        if span.output_data is not None:
            attributes.append(_attribute("agenticlens.output_data", span.output_data))
        for key, value in sorted(span.attributes.items()):
            attributes.append(_attribute(key, value))
        return attributes


def _attribute(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "value": _any_value(value)}


def _string_attribute(key: str, value: str) -> dict[str, Any]:
    return {"key": key, "value": {"stringValue": value}}


def _any_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {"stringValue": "null"}
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int):
        return {"intValue": str(value)}
    if isinstance(value, float):
        if math.isfinite(value):
            return {"doubleValue": value}
        return {"stringValue": str(value)}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, dict):
        return {
            "kvlistValue": {
                "values": [
                    {"key": str(key), "value": _any_value(item)} for key, item in value.items()
                ]
            }
        }
    if isinstance(value, (list, tuple)):
        return {"arrayValue": {"values": [_any_value(item) for item in value]}}
    return {"stringValue": str(value)}


def _normalize_trace_id(value: str) -> str:
    return _normalize_hex_id(value, width=32)


def _normalize_span_id(value: str) -> str:
    return _normalize_hex_id(value, width=16)


def _normalize_parent_span_id(value: str | None) -> str:
    if value is None:
        return ""
    return _normalize_span_id(value)


def _normalize_hex_id(value: str, *, width: int) -> str:
    compact = "".join(ch for ch in value.lower() if ch in "0123456789abcdef")
    if len(compact) == width:
        return compact
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return digest[:width]


def _to_unix_nano(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    timestamp = value.astimezone(timezone.utc).timestamp()
    return str(int(timestamp * 1_000_000_000))


def _kind_for(span: Span) -> int:
    if span.span_type in {SpanType.MODEL_CALL, SpanType.TOOL_CALL, SpanType.RETRIEVAL}:
        return _CLIENT_KIND
    return _INTERNAL_KIND


def _status_payload(span: Span) -> dict[str, Any]:
    if span.status is RunStatus.FAILED:
        return {"code": 2, "message": span.error_message or "span failed"}
    return {"code": 1}


def _events_for(span: Span) -> list[dict[str, Any]]:
    if span.error_message is None:
        return []
    return [
        {
            "timeUnixNano": _to_unix_nano(span.completed_at or span.started_at),
            "name": "exception",
            "attributes": [
                _string_attribute("exception.type", span.error_type or "Exception"),
                _string_attribute("exception.message", span.error_message),
            ],
        }
    ]


def _agenticlens_version() -> str:
    try:
        return importlib.metadata.version("agenticlens")
    except importlib.metadata.PackageNotFoundError:
        return "0.4.0"
