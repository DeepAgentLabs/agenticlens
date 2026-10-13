"""Diagnose a failed multi-agent run against healthy baseline runs.

Builds six healthy runs of a refund-support workflow and one incident run in
which the payments tool times out, its retry also times out, and the writer
agent then fails for lack of data. `diagnose_run()` attributes the failure to
the payments call (not to the writer, whose failure is a consequence),
rebuilds the incident timeline, flags anomalies against the baseline, and
`explain_run()` writes the investigation narrative.

Everything is deterministic and offline:

    uv run python examples/diagnosis_demo.py

writes `examples/diagnosis/artifacts/` (traces, diagnosis.json,
investigation.md). The same files reproduce from the CLI:

    agenticlens diagnose examples/diagnosis/artifacts/incident.json \\
        --baseline examples/diagnosis/artifacts/baseline \\
        --save diagnosis.json --markdown investigation.md
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agenticlens.diagnosis import diagnose_run, explain_run
from agenticlens.models.trace import Run, RunStatus, Span, SpanType

ARTIFACTS = Path(__file__).resolve().parent / "diagnosis" / "artifacts"
T0 = datetime(2026, 10, 2, 14, 0, tzinfo=timezone.utc)


def _run(run_id: str, *, day: int, incident: bool, jitter: float) -> Run:
    start = T0 + timedelta(days=day)
    spans: list[Span] = []
    clock = 0.0

    def add(span_id: str, name: str, span_type: SpanType, latency: float, **fields: object) -> None:
        nonlocal clock
        begin = start + timedelta(milliseconds=clock)
        clock += latency + 4
        spans.append(
            Span(
                span_id=f"{run_id}-{span_id}",
                name=name,
                span_type=span_type,
                started_at=begin,
                completed_at=begin + timedelta(milliseconds=latency),
                latency_ms=latency,
                **fields,  # type: ignore[arg-type]
            )
        )

    root = f"{run_id}-route"
    ok = RunStatus.SUCCEEDED
    add(
        "route",
        "route_ticket",
        SpanType.DELEGATION,
        30,
        agent_name="router",
        status=ok,
        attributes={"to_agent": "refunds"},
        estimated_cost_usd=0.0,
    )
    add(
        "plan",
        "plan_refund",
        SpanType.MODEL_CALL,
        410 + jitter,
        agent_name="refunds",
        parent_span_id=root,
        model_name="gpt-4o-mini",
        provider="openai",
        status=ok,
        input_tokens=820,
        output_tokens=96,
        estimated_cost_usd=0.00018,
    )
    add(
        "policy",
        "refund_policy_search",
        SpanType.RETRIEVAL,
        95 + jitter / 4,
        agent_name="refunds",
        parent_span_id=root,
        status=ok,
        attributes={"result_count": 4},
        estimated_cost_usd=0.0,
    )
    if incident:
        add(
            "pay",
            "issue_refund",
            SpanType.TOOL_CALL,
            5000,
            agent_name="refunds",
            parent_span_id=root,
            tool_name="payments",
            status=RunStatus.FAILED,
            error_type="TimeoutError",
            error_message="payments API timed out after 5000 ms",
            attributes={"timeout_ms": 5000, "tool_args": {"order_id": "A-1182"}},
            estimated_cost_usd=0.0,
        )
        add(
            "retry",
            "retry issue_refund",
            SpanType.RETRY,
            5000,
            agent_name="refunds",
            parent_span_id=f"{run_id}-pay",
            retry_number=1,
            status=RunStatus.FAILED,
            error_type="TimeoutError",
            error_message="payments API timed out after 5000 ms",
            estimated_cost_usd=0.0,
        )
        add(
            "write",
            "write_reply",
            SpanType.FINAL_RESPONSE,
            380,
            agent_name="writer",
            parent_span_id=root,
            model_name="gpt-4o-mini",
            provider="openai",
            status=RunStatus.FAILED,
            error_type="MissingData",
            error_message="no refund confirmation to report",
            input_tokens=1460,
            output_tokens=40,
            estimated_cost_usd=0.00024,
        )
    else:
        add(
            "pay",
            "issue_refund",
            SpanType.TOOL_CALL,
            640 + jitter,
            agent_name="refunds",
            parent_span_id=root,
            tool_name="payments",
            status=ok,
            attributes={"timeout_ms": 5000, "tool_args": {"order_id": "A-1182"}},
            estimated_cost_usd=0.0,
        )
        add(
            "write",
            "write_reply",
            SpanType.FINAL_RESPONSE,
            520 + jitter,
            agent_name="writer",
            parent_span_id=root,
            model_name="gpt-4o-mini",
            provider="openai",
            status=ok,
            input_tokens=1180,
            output_tokens=210,
            estimated_cost_usd=0.0003,
        )
    return Run(
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        application_name="refund-support",
        framework="custom",
        task_type="refund",
        started_at=start,
        completed_at=start + timedelta(milliseconds=clock),
        status=RunStatus.FAILED if incident else RunStatus.SUCCEEDED,
        task_success=not incident,
        spans=spans,
    )


def main(out: Path = ARTIFACTS) -> None:
    baseline_dir = out / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    baseline = [
        _run(f"healthy-{index}", day=index, incident=False, jitter=float(index * 7 % 23))
        for index in range(1, 7)
    ]
    for run in baseline:
        (baseline_dir / f"{run.run_id}.json").write_text(
            json.dumps(run.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8"
        )
    incident = _run("incident-0042", day=8, incident=True, jitter=5.0)
    (out / "incident.json").write_text(
        json.dumps(incident.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8"
    )

    report = diagnose_run(incident, baseline=baseline)
    (out / "diagnosis.json").write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    narrative = explain_run(report)
    (out / "investigation.md").write_text(narrative, encoding="utf-8")

    attribution = report.attribution
    print(f"Faulty step: {attribution.faulty_step} (agent {attribution.faulty_agent})")
    print(f"Category: {attribution.category.value if attribution.category else 'n/a'}")
    print(f"Confidence: {attribution.confidence:.0%}")
    print(f"Anomalies: {len(report.anomalies.anomalies) if report.anomalies else 0}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ARTIFACTS)
