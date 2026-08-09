import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from agenticlens import Run, RunStatus, SpanType, trace
from agenticlens.analysis.trace import (
    analyze_trace,
    classify_retry_outcomes,
    duplicated_context_groups,
    memory_share,
    retry_attribution,
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


def test_run_rejects_parent_cycles():
    payload = {
        "application_name": "bad",
        "spans": [
            {"span_id": "a", "name": "one", "span_type": "custom", "parent_span_id": "b"},
            {"span_id": "b", "name": "two", "span_type": "custom", "parent_span_id": "a"},
        ],
    }
    with pytest.raises(ValidationError, match="cycle"):
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


def test_trace_records_framework_and_experiment_identity():
    with trace(
        "identity",
        framework="langgraph",
        framework_version="1.2",
        task_id="case-1",
        task_type="support",
        experiment_id="experiment-1",
        variant_id="candidate",
    ) as recording:
        pass

    assert recording.run.framework == "langgraph"
    assert recording.run.framework_version == "1.2"
    assert recording.run.task_id == "case-1"
    assert recording.run.task_type == "support"
    assert recording.run.experiment_id == "experiment-1"
    assert recording.run.variant_id == "candidate"


def test_span_maps_structured_identity_fields():
    with (
        trace("structured-span") as recording,
        recording.span(
            "tool",
            SpanType.TOOL_CALL,
            agent_name="analyst",
            model_name="test-model",
            provider="local",
            tool_name="calculator",
        ),
    ):
        pass

    span = recording.run.spans[0]
    assert span.agent_name == "analyst"
    assert span.model_name == "test-model"
    assert span.provider == "local"
    assert span.tool_name == "calculator"
    assert "tool_name" not in span.attributes


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
    assert findings[0].evidence


def test_retry_analysis_attributes_triggering_failure_and_outcomes():
    recording = trace("retry-attribution")
    with recording:
        with pytest.raises(RuntimeError), recording.span("tool", SpanType.TOOL_CALL):
            raise RuntimeError("network")
        with recording.span("retry", SpanType.RETRY) as retry:
            retry.record_tokens(5, 0)
            with recording.span("tool-success", SpanType.TOOL_CALL):
                pass

    outcomes = classify_retry_outcomes(recording.run)
    attribution = retry_attribution(recording.run)
    retry_span = next(span for span in recording.run.spans if span.span_type is SpanType.RETRY)
    assert outcomes["recovered"] == 1
    assert attribution[retry_span.span_id]["triggering_failure_span_id"]
    assert "triggering_failure_span_id" not in retry_span.attributes


def test_duplicate_context_detection_groups_reused_inputs():
    with trace("duplicates") as recording:
        with recording.span("one", SpanType.MODEL_CALL, input_reference="context:42"):
            pass
        with recording.span("two", SpanType.MODEL_CALL, input_reference="context:42"):
            pass

    groups = duplicated_context_groups(recording.run)
    findings = analyze_trace(recording.run, duplicated_context_threshold=2)
    assert groups == [[recording.run.spans[0].span_id, recording.run.spans[1].span_id]]
    assert any(finding.category == "context" for finding in findings)


def test_trace_exports_to_otlp_when_configured() -> None:
    with (
        patch("agenticlens.exporters.otlp_trace_exporter.OTLPTraceExporter.export") as export,
        trace("support-agent", otlp_endpoint="http://collector:4318/v1/traces") as recording,
        recording.span("plan", SpanType.PLANNING),
    ):
        pass

    export.assert_called_once()
    exported_run = export.call_args.args[0]
    assert exported_run.application_name == "support-agent"


def test_trace_resets_context_when_otlp_export_fails() -> None:
    with patch(
        "agenticlens.exporters.otlp_trace_exporter.OTLPTraceExporter.export",
        side_effect=ValueError("not-a-url"),
    ):
        with trace("support-agent", otlp_endpoint="not-a-url") as recording:
            pass

    assert recording.run.metadata["otlp_export_error"] == "not-a-url"

    with trace("fresh-trace") as next_recording:
        pass

    assert next_recording.run.application_name == "fresh-trace"


def test_trace_preserves_application_exception_when_otlp_export_fails() -> None:
    recording = trace("support-agent", otlp_endpoint="not-a-url")
    with patch(
        "agenticlens.exporters.otlp_trace_exporter.OTLPTraceExporter.export",
        side_effect=ValueError("not-a-url"),
    ):
        with pytest.raises(RuntimeError, match="boom"), recording:
            raise RuntimeError("boom")

    assert recording.run.error_type == "RuntimeError"
    assert recording.run.metadata["otlp_export_error"] == "not-a-url"
