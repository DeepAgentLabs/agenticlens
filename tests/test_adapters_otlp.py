import json
from datetime import datetime, timedelta, timezone

import pytest

from agenticlens.adapters import load_otlp_export, parse_otlp_payload, safe_trace_filename
from agenticlens.exporters import OTLPTraceExporter
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def _string_attr(key: str, value: str) -> dict:
    return {"key": key, "value": {"stringValue": value}}


def _int_attr(key: str, value: int) -> dict:
    return {"key": key, "value": {"intValue": str(value)}}


def _otlp_span(
    *,
    trace_id: str,
    span_id: str,
    name: str,
    attributes: list[dict],
    parent_span_id: str = "",
    start_ns: int = 1_700_000_000_000_000_000,
    end_ns: int = 1_700_000_000_500_000_000,
    status_code: int = 1,
) -> dict:
    return {
        "traceId": trace_id,
        "spanId": span_id,
        "parentSpanId": parent_span_id,
        "name": name,
        "kind": 3,
        "startTimeUnixNano": str(start_ns),
        "endTimeUnixNano": str(end_ns),
        "attributes": attributes,
        "status": {"code": status_code},
    }


def _payload(resource_attrs: list[dict], spans: list[dict]) -> dict:
    return {
        "resourceSpans": [
            {
                "resource": {"attributes": resource_attrs},
                "scopeSpans": [{"scope": {"name": "test"}, "spans": spans}],
            }
        ]
    }


@pytest.mark.parametrize(
    "trace_id",
    ["../../etc/passwd", "/etc/passwd", "..", ".", "a/b\\c", "C:\\evil", ""],
)
def test_safe_trace_filename_never_escapes_or_traverses(trace_id: str) -> None:
    safe = safe_trace_filename(trace_id)

    assert "/" not in safe
    assert "\\" not in safe
    assert safe not in ("", ".", "..")


def test_honors_exported_run_status_over_span_inference() -> None:
    payload = _payload(
        [
            _string_attr("service.name", "task-runner"),
            _string_attr("agenticlens.status", "failed"),
        ],
        [
            _otlp_span(
                trace_id="f" * 32,
                span_id="1" * 16,
                name="chat",
                attributes=[_string_attr("gen_ai.operation.name", "chat")],
                status_code=1,  # every individual span still succeeded
            )
        ],
    )

    [imported] = parse_otlp_payload(payload)

    assert imported.status is RunStatus.FAILED


def test_round_trips_an_agenticlens_exported_run() -> None:
    started = datetime.now(timezone.utc)
    run = Run(
        application_name="support-agent",
        started_at=started,
        completed_at=started + timedelta(milliseconds=500),
        status=RunStatus.SUCCEEDED,
        spans=[
            Span(
                name="Classify intent",
                span_type=SpanType.PLANNING,
                agent_name="planner",
                model_name="gpt-4o-mini",
                provider="openai",
                started_at=started,
                latency_ms=200,
                input_tokens=400,
                output_tokens=100,
                estimated_cost_usd=0.002,
            ),
            Span(
                name="lookup_order",
                span_type=SpanType.TOOL_CALL,
                tool_name="lookup_order",
                started_at=started + timedelta(milliseconds=200),
                latency_ms=50,
            ),
        ],
    )

    payload = OTLPTraceExporter().to_payload(run)
    [imported] = parse_otlp_payload(payload)

    assert imported.application_name == "support-agent"
    assert imported.status is RunStatus.SUCCEEDED
    assert len(imported.spans) == 2
    by_name = {span.name: span for span in imported.spans}
    assert by_name["Classify intent"].span_type is SpanType.PLANNING
    assert by_name["Classify intent"].agent_name == "planner"
    assert by_name["Classify intent"].model_name == "gpt-4o-mini"
    assert by_name["Classify intent"].input_tokens == 400
    assert by_name["Classify intent"].output_tokens == 100
    assert by_name["Classify intent"].estimated_cost_usd == 0.002
    assert by_name["lookup_order"].span_type is SpanType.TOOL_CALL
    assert by_name["lookup_order"].tool_name == "lookup_order"


def test_round_trips_run_level_error_type() -> None:
    started = datetime.now(timezone.utc)
    run = Run(
        application_name="support-agent",
        started_at=started,
        completed_at=started + timedelta(milliseconds=500),
        status=RunStatus.FAILED,
        error_type="ToolTimeoutError",
        spans=[
            Span(
                name="lookup_order",
                span_type=SpanType.TOOL_CALL,
                tool_name="lookup_order",
                started_at=started,
                latency_ms=50,
                status=RunStatus.FAILED,
            ),
        ],
    )

    payload = OTLPTraceExporter().to_payload(run)
    [imported] = parse_otlp_payload(payload)

    assert imported.error_type == "ToolTimeoutError"


def test_imports_third_party_genai_payload_split_across_resource_spans() -> None:
    trace_id = "a" * 32
    chat_span = _otlp_span(
        trace_id=trace_id,
        span_id="1" * 16,
        name="chat gpt-4o",
        attributes=[
            _string_attr("gen_ai.operation.name", "chat"),
            _string_attr("gen_ai.provider.name", "openai"),
            _string_attr("gen_ai.request.model", "gpt-4o"),
            _int_attr("gen_ai.usage.input_tokens", 250),
            _int_attr("gen_ai.usage.output_tokens", 80),
        ],
    )
    tool_span = _otlp_span(
        trace_id=trace_id,
        span_id="2" * 16,
        parent_span_id="1" * 16,
        name="execute_tool lookup_order",
        attributes=[
            _string_attr("gen_ai.operation.name", "execute_tool"),
            _string_attr("gen_ai.tool.name", "lookup_order"),
        ],
    )
    payload = {
        "resourceSpans": [
            {
                "resource": {"attributes": [_string_attr("service.name", "support-agent")]},
                "scopeSpans": [{"scope": {"name": "vendor-a"}, "spans": [chat_span]}],
            },
            {
                "resource": {"attributes": [_string_attr("service.name", "support-agent")]},
                "scopeSpans": [{"scope": {"name": "vendor-a"}, "spans": [tool_span]}],
            },
        ]
    }

    [run] = parse_otlp_payload(payload)

    assert run.application_name == "support-agent"
    by_name = {span.name: span for span in run.spans}
    chat = by_name["chat gpt-4o"]
    assert chat.span_type is SpanType.MODEL_CALL
    assert chat.provider == "openai"
    assert chat.model_name == "gpt-4o"
    assert chat.input_tokens == 250
    assert chat.output_tokens == 80
    tool = by_name["execute_tool lookup_order"]
    assert tool.span_type is SpanType.TOOL_CALL
    assert tool.tool_name == "lookup_order"
    assert tool.parent_span_id == "1" * 16


def test_maps_legacy_genai_attribute_names() -> None:
    trace_id = "b" * 32
    span = _otlp_span(
        trace_id=trace_id,
        span_id="3" * 16,
        name="legacy chat",
        attributes=[
            _string_attr("gen_ai.system", "anthropic"),
            _int_attr("gen_ai.usage.prompt_tokens", 120),
            _int_attr("gen_ai.usage.completion_tokens", 40),
        ],
    )
    [run] = parse_otlp_payload(_payload([], [span]))

    result = run.spans[0]
    assert result.provider == "anthropic"
    assert result.input_tokens == 120
    assert result.output_tokens == 40
    # No operation.name/tool.name and no other gen_ai.* signal beyond system+usage
    # still counts as a GenAI signal -> MODEL_CALL, not CUSTOM.
    assert result.span_type is SpanType.MODEL_CALL


def test_multiple_trace_ids_produce_multiple_runs() -> None:
    span_a = _otlp_span(trace_id="a" * 32, span_id="1" * 16, name="a", attributes=[])
    span_b = _otlp_span(trace_id="b" * 32, span_id="2" * 16, name="b", attributes=[])

    runs = parse_otlp_payload(_payload([], [span_a, span_b]))

    assert {run.trace_id for run in runs} == {"a" * 32, "b" * 32}


def test_orphaned_parent_span_id_becomes_a_root_span() -> None:
    span = _otlp_span(
        trace_id="c" * 32,
        span_id="1" * 16,
        name="orphan",
        parent_span_id="9" * 16,  # not present anywhere in this trace
        attributes=[],
    )
    [run] = parse_otlp_payload(_payload([], [span]))

    assert run.spans[0].parent_span_id is None


def test_unrecognized_attributes_are_preserved_verbatim() -> None:
    span = _otlp_span(
        trace_id="d" * 32,
        span_id="1" * 16,
        name="custom",
        attributes=[_string_attr("vendor.custom_field", "keep-me")],
    )
    [run] = parse_otlp_payload(_payload([], [span]))

    assert run.spans[0].attributes["vendor.custom_field"] == "keep-me"


def test_failed_status_code_maps_to_failed_status() -> None:
    span = _otlp_span(
        trace_id="e" * 32, span_id="1" * 16, name="broken", attributes=[], status_code=2
    )
    [run] = parse_otlp_payload(_payload([], [span]))

    assert run.spans[0].status is RunStatus.FAILED
    assert run.status is RunStatus.FAILED


def test_missing_resource_spans_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="resourceSpans"):
        parse_otlp_payload({})


def test_empty_export_returns_no_runs() -> None:
    assert parse_otlp_payload({"resourceSpans": []}) == []


def test_load_otlp_export_reads_a_single_file(tmp_path) -> None:
    span = _otlp_span(trace_id="f" * 32, span_id="1" * 16, name="file-case", attributes=[])
    path = tmp_path / "export.json"
    path.write_text(json.dumps(_payload([], [span])), encoding="utf-8")

    [run] = load_otlp_export(path)

    assert run.trace_id == "f" * 32


def test_load_otlp_export_reads_every_file_in_a_directory(tmp_path) -> None:
    span_a = _otlp_span(trace_id="a" * 32, span_id="1" * 16, name="a", attributes=[])
    span_b = _otlp_span(trace_id="b" * 32, span_id="1" * 16, name="b", attributes=[])
    (tmp_path / "one.json").write_text(json.dumps(_payload([], [span_a])), encoding="utf-8")
    (tmp_path / "two.json").write_text(json.dumps(_payload([], [span_b])), encoding="utf-8")

    runs = load_otlp_export(tmp_path)

    assert {run.trace_id for run in runs} == {"a" * 32, "b" * 32}
