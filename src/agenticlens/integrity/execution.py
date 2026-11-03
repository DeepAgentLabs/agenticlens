"""AIOS draft Run capture/export/import with Lens-owned lossless extensions."""

import json
import tempfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agenticlens.integrity import Coverage, Manifest, Verification, seal, verify
from agenticlens.models.trace import Run, RunStatus
from agenticlens.validation import validate_aios_artifact

NAMESPACE = "io.deepagentlabs.agenticlens.execution"


class ExecutionRecord(BaseModel):
    """Explicit producer observations, never inferred from supervision verdicts."""

    model_config = ConfigDict(extra="forbid", strict=True)
    event_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    span_id: str | None = None
    occurred_at: str
    kind: Literal[
        "proposed",
        "allowed",
        "denied",
        "dispatched",
        "completed",
        "stop_acknowledged",
        "revocation_acknowledged",
    ]
    producer: str = Field(min_length=1)
    decision_id: str | None = None
    action_id: str | None = None
    actor: str | None = None
    policy_version: str | None = None
    approval_id: str | None = None
    outcome: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def aware_time(self) -> "ExecutionRecord":
        timestamp = datetime.fromisoformat(self.occurred_at.replace("Z", "+00:00"))
        if timestamp.utcoffset() is None:
            raise ValueError("Execution timestamps must be timezone-aware")
        return self


class ExecutionBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artifact: dict[str, Any]
    manifest: Manifest


def _validate(artifact: dict[str, Any]) -> None:
    # Reuse the packaged AIOS schemas and semantic checker. Temporary files are
    # internal only: no caller paths, fetching, imports or execution occur here.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "run.json"
        path.write_text(json.dumps(artifact, allow_nan=False), encoding="utf-8")
        report = validate_aios_artifact(path)
    if report.summary is None or report.summary.status != "aligned":
        raise ValueError("Invalid AIOS Run schema or semantic relationships")


def _records(run: Run, records: list[ExecutionRecord]) -> None:
    ids = [record.event_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate execution event identity")
    spans = {span.span_id for span in run.spans}
    for record in records:
        if record.run_id != run.run_id or (
            record.span_id is not None and record.span_id not in spans
        ):
            raise ValueError("Execution run/span correlation mismatch")


def export_execution(run: Run, records: list[ExecutionRecord]) -> dict[str, Any]:
    """Export observed spans and explicitly supplied events; fabricate no dispatch."""
    # Revalidate mutable Pydantic inputs and use detached JSON snapshots.
    run = Run.model_validate(run.model_dump(mode="json"))
    if run.schema_version != "1.0":
        raise ValueError("Unsupported native Lens Run schema version")
    records = [ExecutionRecord.model_validate(r.model_dump()) for r in records]
    _records(run, records)
    statuses = {
        RunStatus.RUNNING: "running",
        RunStatus.SUCCEEDED: "completed",
        RunStatus.FAILED: "failed",
    }
    artifact: dict[str, Any] = {
        "spec_version": "0.4-draft",
        "artifact_type": "run",
        "id": run.run_id,
        "started_at": run.started_at.isoformat(),
        "status": statuses[run.status],
        "requests": [],
        "steps": [],
        "relationships": [],
        "events": [],
        "extensions": {
            NAMESPACE: {
                "format": "lens.execution/1",
                "native_run": run.model_dump(mode="json"),
                "capture_order": [r.event_id for r in records],
                "mapping": "Lens spans to steps; explicit producer records to extension events",
                "limitations": [
                    "No inferred dispatch or completeness",
                    "Extension event semantics are Lens-local",
                ],
            }
        },
    }
    if run.completed_at is not None:
        artifact["ended_at"] = run.completed_at.isoformat()
    for span in run.spans:
        step: dict[str, Any] = {
            "id": span.span_id,
            "name": span.name,
            "category": span.span_type.value,
            "status": statuses[span.status],
            "started_at": span.started_at.isoformat(),
        }
        if span.completed_at is not None:
            step["ended_at"] = span.completed_at.isoformat()
        artifact["steps"].append(step)
        artifact["relationships"].append(
            {
                "id": "contains:" + span.span_id,
                "type": "contains",
                "source": {"id": run.run_id, "type": "run"},
                "target": {"id": span.span_id, "type": "step"},
            }
        )
        if span.parent_span_id is not None:
            artifact["relationships"].append(
                {
                    "id": "parent:" + span.span_id,
                    "type": "parent-of",
                    "source": {"id": span.parent_span_id, "type": "step"},
                    "target": {"id": span.span_id, "type": "step"},
                }
            )
    artifact["events"] = [
        {
            "event_id": r.event_id,
            "event_name": NAMESPACE + "." + r.kind,
            "occurred_at": r.occurred_at,
            "object_id": r.span_id or run.run_id,
            "object_type": "step" if r.span_id else "run",
            "extensions": {NAMESPACE: r.model_dump(mode="json")},
        }
        for r in records
    ]
    _validate(artifact)
    return artifact


def import_execution(artifact: dict[str, Any]) -> tuple[Run, list[ExecutionRecord]]:
    """Validate schema, semantic references and the lossless Lens mapping offline."""
    _validate(artifact)
    try:
        extension = artifact["extensions"][NAMESPACE]
        if extension["format"] != "lens.execution/1":
            raise ValueError("Unsupported execution mapping")
        run = Run.model_validate(extension["native_run"])
        records = [
            ExecutionRecord.model_validate(e["extensions"][NAMESPACE]) for e in artifact["events"]
        ]
        if export_execution(run, records) != artifact:
            raise ValueError("AIOS projection and native evidence disagree")
    except (KeyError, TypeError) as exc:
        raise ValueError("Missing Lens execution mapping") from exc
    return run, records


def capture_execution(
    run: Run, records: list[ExecutionRecord], *, coverage: Coverage, key_id: str, key: bytes
) -> ExecutionBundle:
    if coverage.stream_id != run.run_id:
        raise ValueError("Coverage must identify the captured run")
    artifact = export_execution(run, records)
    return ExecutionBundle(
        artifact=artifact, manifest=seal([artifact], coverage=coverage, key_id=key_id, key=key)
    )


def verify_execution(
    bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str
) -> Verification:
    result = verify(
        [bundle.artifact],
        bundle.manifest,
        trusted_keys=trusted_keys,
        expected_stream_id=expected_run_id,
    )
    if result.status in {"verified", "incomplete"}:
        try:
            run, _ = import_execution(bundle.artifact)
            if run.run_id != expected_run_id:
                raise ValueError("Run mismatch")
        except (ValueError, TypeError, KeyError):
            return Verification(
                status="failed", reason="Invalid execution mapping or AIOS conformance"
            )
    return result


def replay_execution(
    bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str
) -> tuple[Run, list[ExecutionRecord]]:
    result = verify_execution(bundle, trusted_keys=trusted_keys, expected_run_id=expected_run_id)
    if result.status != "verified":
        raise ValueError(f"Execution replay refused: {result.status}")
    return import_execution(deepcopy(bundle.artifact))


def execution_summary(
    bundle: ExecutionBundle, *, trusted_keys: dict[str, bytes], expected_run_id: str
) -> dict[str, Any]:
    """Redacted downstream projection: no native payloads or unverified causal claims."""
    result = verify_execution(bundle, trusted_keys=trusted_keys, expected_run_id=expected_run_id)
    summary: dict[str, Any] = {"verification": result.model_dump(mode="json"), "causal_links": []}
    if result.status == "verified":
        run, records = import_execution(bundle.artifact)
        summary.update(run_id=run.run_id, trace_id=run.trace_id, status=run.status.value)
        summary["causal_links"] = [r.model_dump(exclude={"attributes", "outcome"}) for r in records]
    return summary
