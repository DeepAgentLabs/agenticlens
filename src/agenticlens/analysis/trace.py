from agenticlens.models.trace import Finding, Run, SpanType


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


def analyze_trace(
    run: Run,
    *,
    memory_share_threshold: float = 0.5,
    retry_share_threshold: float = 0.2,
) -> list[Finding]:
    """Produce deterministic findings whose evidence is reproducible from the trace."""
    findings: list[Finding] = []
    memory_spans = [
        span.span_id
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
                span_ids=memory_spans,
                evidence={
                    "memory_tokens": memory_tokens(run),
                    "total_tokens": run.total_tokens,
                    "memory_share": measured_memory_share,
                    "threshold": memory_share_threshold,
                },
            )
        )

    retry_spans = [span.span_id for span in run.spans if span.span_type is SpanType.RETRY]
    measured_retry_share = retry_token_share(run)
    if measured_retry_share > retry_share_threshold:
        findings.append(
            Finding(
                category="retry",
                title="High retry overhead",
                description="Retry spans consume a large share of recorded tokens.",
                severity="medium",
                confidence=1.0,
                span_ids=retry_spans,
                evidence={
                    "retry_tokens": retry_tokens(run),
                    "retry_latency_ms": retry_latency_ms(run),
                    "retry_cost_usd": retry_cost_usd(run),
                    "retry_token_share": measured_retry_share,
                    "threshold": retry_share_threshold,
                },
            )
        )
    return findings
