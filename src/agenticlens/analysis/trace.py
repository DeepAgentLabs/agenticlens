import json
from collections import defaultdict
from typing import Any

from agenticlens.models.trace import Evidence, Finding, Run, Span, SpanType


def _evidence(
    *,
    source: str,
    span: Span | None = None,
    reasoning: str | None = None,
    details: dict[str, Any] | None = None,
) -> Evidence:
    return Evidence(
        source=source,
        span_id=span.span_id if span else None,
        timestamp=span.completed_at if span else None,
        confidence=1.0,
        reasoning=reasoning,
        details=details or {},
    )


def memory_tokens(run: Run) -> int:
    return sum(
        span.total_tokens
        for span in run.spans
        if span.span_type in {SpanType.MEMORY_READ, SpanType.MEMORY_WRITE}
    )


def memory_share(run: Run) -> float:
    return memory_tokens(run) / run.total_tokens if run.total_tokens else 0.0


def retry_tokens(run: Run) -> int:
    return sum(span.total_tokens for span in run.spans if span.span_type is SpanType.RETRY)


def retry_latency_ms(run: Run) -> float:
    return sum(span.latency_ms for span in run.spans if span.span_type is SpanType.RETRY)


def retry_cost_usd(run: Run) -> float:
    return sum(
        span.estimated_cost_usd or 0.0 for span in run.spans if span.span_type is SpanType.RETRY
    )


def retry_token_share(run: Run) -> float:
    return retry_tokens(run) / run.total_tokens if run.total_tokens else 0.0


def retry_latency_share(run: Run) -> float:
    return retry_latency_ms(run) / run.total_latency_ms if run.total_latency_ms else 0.0


def retry_attribution(run: Run) -> dict[str, dict[str, str | None]]:
    attribution: dict[str, dict[str, str | None]] = {}
    spans_by_id = {span.span_id: span for span in run.spans}
    for retry_span in (span for span in run.spans if span.span_type is SpanType.RETRY):
        triggering = spans_by_id.get(retry_span.parent_span_id or "")
        if triggering is None or triggering.status.value != "failed":
            retry_index = run.spans.index(retry_span)
            triggering = next(
                (
                    candidate
                    for candidate in reversed(run.spans[:retry_index])
                    if candidate.status.value == "failed"
                ),
                None,
            )
        attribution[retry_span.span_id] = {
            "triggering_failure_span_id": triggering.span_id if triggering else None,
            "triggering_failure_type": triggering.error_type if triggering else None,
        }
    return attribution


def classify_retry_outcomes(run: Run) -> dict[str, int]:
    outcomes = {"recovered": 0, "failed": 0, "unknown": 0}
    children_by_parent: dict[str, list[Span]] = defaultdict(list)
    for span in run.spans:
        if span.parent_span_id:
            children_by_parent[span.parent_span_id].append(span)

    for retry_span in (span for span in run.spans if span.span_type is SpanType.RETRY):
        descendants = children_by_parent.get(retry_span.span_id, [])
        if any(child.status.value == "succeeded" for child in descendants):
            outcomes["recovered"] += 1
        elif retry_span.status.value == "failed" or any(
            child.status.value == "failed" for child in descendants
        ):
            outcomes["failed"] += 1
        else:
            outcomes["unknown"] += 1
    return outcomes


def duplicated_context_groups(run: Run) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for span in run.spans:
        fingerprint: str | None = None
        if span.input_reference:
            fingerprint = f"ref:{span.input_reference}"
        elif span.input_data is not None:
            fingerprint = "data:" + json.dumps(
                span.input_data,
                sort_keys=True,
                ensure_ascii=True,
                default=str,
            )
        if fingerprint:
            groups[fingerprint].append(span.span_id)
    return [span_ids for span_ids in groups.values() if len(span_ids) > 1]


def analyze_trace(
    run: Run,
    *,
    memory_share_threshold: float = 0.5,
    retry_share_threshold: float = 0.2,
    duplicated_context_threshold: int = 2,
) -> list[Finding]:
    """Produce deterministic findings whose evidence is reproducible from the trace."""
    findings: list[Finding] = []
    memory_spans = [
        span
        for span in run.spans
        if span.span_type in {SpanType.MEMORY_READ, SpanType.MEMORY_WRITE}
    ]
    measured_memory_share = memory_share(run)
    if measured_memory_share > memory_share_threshold:
        findings.append(
            Finding(
                category="memory",
                title="High memory token share",
                description="Memory spans consume a large share of recorded tokens.",
                severity="medium",
                confidence=1.0,
                span_ids=[span.span_id for span in memory_spans],
                evidence=[
                    _evidence(
                        source="trace.metrics",
                        reasoning="Memory spans exceed the configured token-share threshold.",
                        details={
                            "memory_tokens": memory_tokens(run),
                            "total_tokens": run.total_tokens,
                            "memory_share": measured_memory_share,
                            "threshold": memory_share_threshold,
                        },
                    )
                ]
                + [
                    _evidence(
                        source="trace.span",
                        span=span,
                        details={"span_type": span.span_type.value, "tokens": span.total_tokens},
                    )
                    for span in memory_spans
                ],
            )
        )

    retry_spans = [span for span in run.spans if span.span_type is SpanType.RETRY]
    measured_retry_share = retry_token_share(run)
    retry_outcomes = classify_retry_outcomes(run)
    retry_sources = retry_attribution(run)
    if measured_retry_share > retry_share_threshold:
        findings.append(
            Finding(
                category="retry",
                title="High retry overhead",
                description="Retry spans consume a large share of recorded tokens.",
                severity="medium",
                confidence=1.0,
                span_ids=[span.span_id for span in retry_spans],
                evidence=[
                    _evidence(
                        source="trace.metrics",
                        reasoning="Retry spans exceed the configured token-share threshold.",
                        details={
                            "retry_tokens": retry_tokens(run),
                            "retry_latency_ms": retry_latency_ms(run),
                            "retry_cost_usd": retry_cost_usd(run),
                            "retry_token_share": measured_retry_share,
                            "threshold": retry_share_threshold,
                            "outcomes": retry_outcomes,
                        },
                    )
                ]
                + [
                    _evidence(
                        source="trace.retry",
                        span=span,
                        details={
                            "retry_number": span.retry_number,
                            **retry_sources.get(span.span_id, {}),
                        },
                    )
                    for span in retry_spans
                ],
            )
        )

    duplicate_groups = duplicated_context_groups(run)
    if any(len(group) >= duplicated_context_threshold for group in duplicate_groups):
        findings.append(
            Finding(
                category="context",
                title="Duplicated context across spans",
                description="The same context payload or reference is reused across spans.",
                severity="low",
                confidence=1.0,
                span_ids=[span_id for group in duplicate_groups for span_id in group],
                evidence=[
                    _evidence(
                        source="trace.context",
                        reasoning=(
                            "Duplicate context was detected from repeated input "
                            "payloads or references."
                        ),
                        details={"duplicate_groups": duplicate_groups},
                    )
                ],
            )
        )
    return findings
