"""Capture, export, import and replay AIOS evidence without live tools or services."""

import json
import secrets
from datetime import datetime, timezone

from agenticlens.integrity import Coverage
from agenticlens.integrity.execution import (
    ExecutionBundle,
    ExecutionRecord,
    capture_execution,
    execution_summary,
    replay_execution,
)
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def main() -> None:
    key = secrets.token_bytes(32)
    timestamp = datetime(2026, 11, 2, tzinfo=timezone.utc)
    run = Run(
        run_id="example-run",
        trace_id="example-trace",
        application_name="offline-example",
        started_at=timestamp,
        completed_at=timestamp,
        status=RunStatus.SUCCEEDED,
        spans=[
            Span(
                span_id="example-tool",
                name="saved read",
                span_type=SpanType.TOOL_CALL,
                started_at=timestamp,
                completed_at=timestamp,
                status=RunStatus.SUCCEEDED,
            )
        ],
    )
    records = [
        ExecutionRecord(
            event_id=f"example-{kind}",
            run_id=run.run_id,
            span_id="example-tool",
            occurred_at=timestamp.isoformat(),
            kind=kind,
            producer="offline-fixture",
            action_id="action-1",
            decision_id="decision-1",
            actor="example-agent",
            policy_version="p1",
        )
        for kind in ("proposed", "allowed", "dispatched", "completed")
    ]
    bundle = capture_execution(
        run,
        records,
        coverage=Coverage(
            stream_id=run.run_id, description="synthetic saved example", complete=True
        ),
        key_id="ephemeral-demo",
        key=key,
    )
    restored = ExecutionBundle.model_validate_json(bundle.model_dump_json())
    imported_run, imported_records = replay_execution(
        restored, trusted_keys={"ephemeral-demo": key}, expected_run_id=run.run_id
    )
    assert imported_run == run and imported_records == records
    summary = execution_summary(
        restored, trusted_keys={"ephemeral-demo": key}, expected_run_id=run.run_id
    )
    assert summary["verification"]["status"] == "verified"
    print(json.dumps(summary, indent=2))
    # No output/key files are written and no actual tool was dispatched.


if __name__ == "__main__":
    main()
