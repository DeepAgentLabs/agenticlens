from collections import defaultdict

from agenticlens.models.trace import Run, SpanType


def tokens_by_span_type(run: Run) -> dict[SpanType, int]:
    totals: dict[SpanType, int] = defaultdict(int)
    for span in run.spans:
        totals[span.span_type] += span.total_tokens
    return dict(totals)


def latency_by_span_type(run: Run) -> dict[SpanType, float]:
    totals: dict[SpanType, float] = defaultdict(float)
    for span in run.spans:
        totals[span.span_type] += span.latency_ms
    return dict(totals)


def retry_count(run: Run) -> int:
    return sum(span.span_type is SpanType.RETRY for span in run.spans)


def tool_call_count(run: Run) -> int:
    return sum(span.span_type is SpanType.TOOL_CALL for span in run.spans)
