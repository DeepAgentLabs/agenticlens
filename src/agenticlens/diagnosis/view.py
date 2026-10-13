"""Read-only helpers over a `Run` that diagnosis rules share.

`TraceView` orders spans by start time, applies the analysis guard's span
and depth limits once, and answers the questions rules keep asking: who is
a span's agent, did it fail, was the failure recovered, was a fault injected.
"""

import hashlib
import json
from collections import defaultdict
from typing import Any

from agenticlens.analysis.trace import retry_attribution
from agenticlens.diagnosis.guardrails import AnalysisGuard
from agenticlens.models.trace import Evidence, Run, RunStatus, Span, SpanType

#: Span attributes that mark a deliberately injected fault. `agentic-chaos`
#: writes these with `agentic_chaos.integrations.agenticlens.span_attributes()`.
CHAOS_INJECTED_KEY = "chaos.injected"
CHAOS_FAULT_TYPE_KEY = "chaos.fault_type"
CHAOS_EVENT_ID_KEY = "chaos.event_id"

_TIMEOUT_MARKERS = ("timeout", "timed out", "deadline exceeded")


def fingerprint(value: Any) -> str:
    """A stable short hash of a JSON-compatible value."""
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _input_fingerprint(span: Span) -> str | None:
    if span.input_reference:
        return f"ref:{span.input_reference}"
    if span.input_data is not None:
        return fingerprint(span.input_data)
    arguments = span.attributes.get("tool_args")
    return None if arguments is None else fingerprint(arguments)


def _output_fingerprint(span: Span) -> str | None:
    if span.output_reference:
        return f"ref:{span.output_reference}"
    return None if span.output_data is None else fingerprint(span.output_data)


class TraceView:
    def __init__(self, run: Run, guard: AnalysisGuard) -> None:
        self.run = run
        positions = {span.span_id: index for index, span in enumerate(run.spans)}
        ordered = sorted(run.spans, key=lambda span: (span.started_at, positions[span.span_id]))
        ordered = ordered[: guard.limit_spans(len(ordered))]
        parents = {span.span_id: span.parent_span_id for span in run.spans}

        self.depth: dict[str, int] = {}
        kept: list[Span] = []
        for span in ordered:
            depth = 0
            current = span.parent_span_id
            while current is not None:
                depth += 1
                current = parents.get(current)
            self.depth[span.span_id] = depth
            if guard.allow_depth(depth):
                kept.append(span)
        self.spans = kept
        self.by_id = {span.span_id: span for span in kept}
        self.position = {span.span_id: index for index, span in enumerate(kept)}
        self.children: dict[str, list[Span]] = defaultdict(list)
        for span in kept:
            if span.parent_span_id in self.by_id:
                self.children[span.parent_span_id].append(span)
        self._all_by_id = {span.span_id: span for span in run.spans}
        self.retry_triggers = {
            retry_id: info["triggering_failure_span_id"]
            for retry_id, info in retry_attribution(run).items()
            if retry_id in self.by_id
        }

    # -- structure -----------------------------------------------------------

    def descendants(self, span_id: str) -> list[Span]:
        found: list[Span] = []
        stack = list(self.children.get(span_id, []))
        while stack:
            span = stack.pop()
            found.append(span)
            stack.extend(self.children.get(span.span_id, []))
        return found

    def ancestors(self, span: Span) -> list[Span]:
        chain: list[Span] = []
        current = self._all_by_id.get(span.parent_span_id or "")
        while current is not None:
            chain.append(current)
            current = self._all_by_id.get(current.parent_span_id or "")
        return chain

    def agent_of(self, span: Span) -> str | None:
        """The span's agent, inherited from the nearest ancestor that names one."""
        if span.agent_name:
            return span.agent_name
        return next((a.agent_name for a in self.ancestors(span) if a.agent_name), None)

    # -- status --------------------------------------------------------------

    @staticmethod
    def failed(span: Span) -> bool:
        return span.status is RunStatus.FAILED

    @staticmethod
    def succeeded(span: Span) -> bool:
        return span.status is RunStatus.SUCCEEDED

    @staticmethod
    def injected_fault(span: Span) -> dict[str, Any] | None:
        attributes = span.attributes
        if not (attributes.get(CHAOS_INJECTED_KEY) or attributes.get(CHAOS_FAULT_TYPE_KEY)):
            return None
        return {
            "fault_type": attributes.get(CHAOS_FAULT_TYPE_KEY),
            "event_id": attributes.get(CHAOS_EVENT_ID_KEY),
        }

    @staticmethod
    def timed_out(span: Span) -> bool:
        text = f"{span.error_type or ''} {span.error_message or ''}".casefold()
        if any(marker in text for marker in _TIMEOUT_MARKERS):
            return True
        limit = span.attributes.get("timeout_ms")
        return (
            span.status is RunStatus.FAILED
            and isinstance(limit, (int, float))
            and not isinstance(limit, bool)
            and span.latency_ms >= limit
        )

    @staticmethod
    def operation_key(span: Span) -> tuple[str, str, str]:
        return (span.span_type.value, span.name, span.tool_name or "")

    def recovered_by(self, span: Span) -> Span | None:
        """A later span that redid `span`'s operation successfully, if any."""
        for retry_id, trigger_id in self.retry_triggers.items():
            if trigger_id != span.span_id:
                continue
            retry = self.by_id[retry_id]
            if self.succeeded(retry):
                return retry
            done = next((d for d in self.descendants(retry_id) if self.succeeded(d)), None)
            if done is not None:
                return done
        key = self.operation_key(span)
        start = self.position.get(span.span_id, -1)
        for later in self.spans[start + 1 :]:
            if self.operation_key(later) == key and self.succeeded(later):
                return later
        return None

    # -- fingerprints --------------------------------------------------------

    @staticmethod
    def input_fingerprint(span: Span) -> str | None:
        return _input_fingerprint(span)

    @staticmethod
    def output_fingerprint(span: Span) -> str | None:
        return _output_fingerprint(span)

    # -- evidence ------------------------------------------------------------

    def evidence(
        self,
        span: Span,
        *,
        source: str = "trace.span",
        reasoning: str | None = None,
        confidence: float = 1.0,
        **details: Any,
    ) -> Evidence:
        base: dict[str, Any] = {
            "span_name": span.name,
            "span_type": span.span_type.value,
            "status": span.status.value,
        }
        if span.agent_name or self.agent_of(span):
            base["agent_name"] = self.agent_of(span)
        if span.error_type:
            base["error_type"] = span.error_type
        if span.error_message:
            base["error_message"] = span.error_message
        if span.tool_name:
            base["tool_name"] = span.tool_name
        base.update({key: value for key, value in details.items() if value is not None})
        return Evidence(
            source=source,
            span_id=span.span_id,
            timestamp=span.completed_at or span.started_at,
            confidence=confidence,
            reasoning=reasoning,
            details=base,
        )


def is_span_type(span: Span, *types: SpanType) -> bool:
    return span.span_type in types
