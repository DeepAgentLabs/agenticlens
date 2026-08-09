from __future__ import annotations

from pathlib import Path

from agenticlens import SpanType, trace
from agenticlens.exporters import OTLPTraceExporter


def main() -> None:
    artifacts = Path("examples/artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)

    with trace("support-agent", environment="demo") as recording:
        with recording.span("planner", SpanType.PLANNING) as planner:
            planner.record_tokens(input_tokens=120, output_tokens=30)
        with recording.span("lookup", SpanType.TOOL_CALL) as lookup:
            lookup.record_tokens(input_tokens=12, output_tokens=6)
            lookup.set_attribute("tool.name", "knowledge-base-search")

    run_path = artifacts / "support-run.json"
    otlp_path = artifacts / "support-run-otlp.json"
    recording.save(run_path)
    OTLPTraceExporter().save(recording.run, otlp_path)

    print(f"Saved AgenticLens run to {run_path}")
    print(f"Saved OTLP payload to {otlp_path}")
    print(
        "Validate with: "
        "uv run agenticlens conformance "
        f"{run_path} --version 0.4 --spec-root ../ai-operations-spec"
    )


if __name__ == "__main__":
    main()
