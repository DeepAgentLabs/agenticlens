import json

import pytest
from pydantic import ValidationError

from agenticlens import Run, RunStatus, SpanType, trace
from agenticlens.analysis.trace import (
    analyze_trace,
    memory_share,
    retry_latency_ms,
    retry_token_share,
)
from agenticlens.metrics.trace import (
    latency_by_span_type,
    retry_count,
    tokens_by_span_type,
    tool_call_count,
)


def test_trace_captures_nested_spans_and_metrics(tmp_path):
    with (
        trace("support-agent", environment="test") as recording,
        recording.span("plan", SpanType.PLANNING) as plan,
        recording.span("lookup", SpanType.TOOL_CALL) as tool,
    ):
        plan.record_tokens(input_tokens=10, output_tokens=5)
        tool.record_tokens(input_tokens=3, output_tokens=7)

    run = recording.run
    assert run.status is RunStatus.SUCCEEDED
    assert run.task_success is True
    assert run.total_input_tokens == 13
    assert run.total_output_tokens == 12
    assert run.spans[1].parent_span_id == run.spans[0].span_id
    assert tokens_by_span_type(run)[SpanType.PLANNING] == 15
    assert tool_call_count(run) == 1
    assert retry_count(run) == 0
    assert latency_by_span_type(run)[SpanType.PLANNING] >= 0

    output = tmp_path / "run.json"
    recording.save(output)
    loaded = Run.model_validate_json(output.read_text(encoding="utf-8"))
    assert loaded == run


def test_trace_records_failures():
    recording = trace("broken-agent")
    with (
        pytest.raises(RuntimeError, match="boom"),
        recording,
        recording.span("retry", SpanType.RETRY),
    ):
        raise RuntimeError("boom")

    assert recording.run.status is RunStatus.FAILED
    assert recording.run.error_type == "RuntimeError"
    assert recording.run.spans[0].status is RunStatus.FAILED
    assert recording.run.spans[0].error_message == "boom"


def test_run_rejects_unknown_parent():
    payload = {
        "application_name": "bad",
        "spans": [
            {
                "name": "orphan",
                "span_type": "custom",
                "parent_span_id": "missing",
            }
        ],
    }
    with pytest.raises(ValidationError, match="unknown parent"):
        Run.model_validate(payload)


def test_trace_json_does_not_capture_values_by_default():
    with trace("privacy") as recording, recording.span("model", SpanType.MODEL_CALL) as span:
        span.record_tokens(4, 2)

    payload = json.loads(recording.run.model_dump_json())
    assert "input" not in payload["spans"][0]
    assert "output" not in payload["spans"][0]


def test_trace_redacts_explicitly_captured_values():
    with (
        trace("privacy", api_key="top-secret") as recording,
        recording.span("model", SpanType.MODEL_CALL) as span,
    ):
        span.record_io(
            input_data={"authorization": "Bearer abc", "message": "write me@example.com"},
            output_data="contact owner@example.com",
        )

    assert recording.run.metadata["api_key"] == "[REDACTED]"
    captured = recording.run.spans[0]
    assert captured.input_data["authorization"] == "[REDACTED]"
    assert captured.input_data["message"] == "write [REDACTED_EMAIL]"
    assert captured.output_data == "contact [REDACTED_EMAIL]"


def test_memory_and_retry_analysis_cites_span_evidence():
    with trace("diagnostics") as recording:
        with recording.span("memory", SpanType.MEMORY_READ) as memory:
            memory.record_tokens(80, 0)
        with recording.span("retry", SpanType.RETRY) as retry:
            retry.record_tokens(30, 0)

    assert memory_share(recording.run) == pytest.approx(80 / 110)
    assert retry_token_share(recording.run) == pytest.approx(30 / 110)
    assert retry_latency_ms(recording.run) >= 0
    findings = analyze_trace(recording.run)
    assert {finding.category for finding in findings} == {"memory", "retry"}
    assert findings[0].span_ids
