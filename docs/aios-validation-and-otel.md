# AIOS Validation and OpenTelemetry Export

AgenticLens can now validate AI Operations Specification draft artifacts and
export structured traces to OTLP/HTTP collectors.

## AIOS draft validation

Use `validate` to run JSON Schema checks against AIOS draft workflow or run
artifacts:

```bash
agenticlens validate workflow.json --version 0.4
agenticlens validate run.json --version 0.4 --save validation-report.json
```

Use `conformance` to run both schema and semantic checks and report draft
alignment:

```bash
agenticlens conformance run.json --version 0.4
agenticlens conformance run.json --version 0.4 --save conformance-report.json
```

When the sibling `ai-operations-spec` repository is not checked out next to
`agenticlens`, pass `--spec-root` explicitly:

```bash
agenticlens conformance run.json \
  --version 0.4 \
  --spec-root ../ai-operations-spec
```

Conformance output distinguishes AIOS-defined pass/fail issues from
AgenticLens-specific rendering. Because AIOS `v0.4` is still a draft, the CLI
reports draft alignment rather than stable conformance.

## OTLP/HTTP trace export

Structured `trace()` runs can be exported as OTLP/HTTP JSON for tools such as
Grafana, Jaeger, or other OTel-compatible collectors.

Configure export directly in code:

```python
from agenticlens import SpanType, trace

with trace(
    "support-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    otlp_headers={"Authorization": "Bearer local-dev-token"},
) as recording:
    with recording.span("planner", SpanType.PLANNING) as planner:
        planner.record_tokens(input_tokens=120, output_tokens=30)
```

You can also configure the endpoint through environment variables:

```bash
export AGENTICLENS_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
export AGENTICLENS_OTLP_HEADERS='Authorization=Bearer local-dev-token'
export AGENTICLENS_OTLP_TIMEOUT_SECONDS=10
```

After these are set, any configured `trace()` run exports automatically when the
trace context exits.

## Local OTLP payload export

If you want to inspect the generated OTLP payload before posting it, use the
exporter directly:

```python
from agenticlens import SpanType, trace
from agenticlens.exporters import OTLPTraceExporter

with trace("support-agent") as recording:
    with recording.span("planner", SpanType.PLANNING):
        pass

OTLPTraceExporter().save(recording.run, "run-otlp.json")
```

See `examples/operational_intelligence_demo.py` for a runnable example that
saves both a run artifact and an OTLP payload, then validates the run with
`agenticlens conformance`.
