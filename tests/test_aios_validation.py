import json
from pathlib import Path

from agenticlens.validation import validate_aios_artifact

SPEC_ROOT = (Path(__file__).parent / "fixtures" / "ai-operations-spec").resolve()


def _write_artifact(tmp_path: Path, payload: dict) -> Path:
    artifact = tmp_path / "artifact.aios.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")
    return artifact


def test_validate_rejects_invalid_datetime_format(tmp_path: Path) -> None:
    payload = {
        "spec_version": "0.4-draft",
        "artifact_type": "run",
        "id": "run-1",
        "started_at": "not-a-date",
        "status": "completed",
        "requests": [],
        "steps": [],
        "relationships": [],
    }

    report = validate_aios_artifact(
        _write_artifact(tmp_path, payload),
        mode="validate",
        spec_root=SPEC_ROOT,
    )

    assert report.schema_valid is False
    assert any(issue.location == "$.started_at" for issue in report.issues)


def test_conformance_rejects_step_with_inverted_timestamps(tmp_path: Path) -> None:
    payload = {
        "spec_version": "0.4-draft",
        "artifact_type": "run",
        "id": "run-1",
        "started_at": "2026-07-21T06:00:00Z",
        "status": "completed",
        "requests": [],
        "steps": [
            {
                "id": "step-1",
                "category": "tool",
                "started_at": "2026-07-21T06:00:02Z",
                "ended_at": "2026-07-21T06:00:01Z",
            }
        ],
        "relationships": [
            {
                "id": "rel-contains",
                "type": "contains",
                "source": {"id": "run-1", "type": "run"},
                "target": {"id": "step-1", "type": "step"},
            }
        ],
    }

    report = validate_aios_artifact(
        _write_artifact(tmp_path, payload),
        mode="conformance",
        spec_root=SPEC_ROOT,
    )

    assert report.semantic_valid is False
    assert any(
        issue.code == "semantic.invalid-time-range" and issue.location == "$.steps.0"
        for issue in report.issues
    )


def test_conformance_rejects_non_external_workflow_reference_without_local_object(
    tmp_path: Path,
) -> None:
    payload = {
        "spec_version": "0.4-draft",
        "artifact_type": "run",
        "id": "run-1",
        "workflow_id": "workflow-1",
        "started_at": "2026-07-21T06:00:00Z",
        "status": "completed",
        "requests": [],
        "steps": [],
        "relationships": [
            {
                "id": "rel-run-of",
                "type": "run-of",
                "source": {"id": "run-1", "type": "run"},
                "target": {"id": "workflow-1", "type": "workflow"},
            }
        ],
    }

    report = validate_aios_artifact(
        _write_artifact(tmp_path, payload),
        mode="conformance",
        spec_root=SPEC_ROOT,
    )

    assert report.semantic_valid is False
    assert any(
        issue.code == "semantic.unresolved-reference"
        and issue.location == "$.relationships.0.target"
        for issue in report.issues
    )


def test_conformance_accepts_external_workflow_reference_with_matching_run_of(
    tmp_path: Path,
) -> None:
    payload = {
        "spec_version": "0.4-draft",
        "artifact_type": "run",
        "id": "run-1",
        "workflow_id": "workflow-1",
        "started_at": "2026-07-21T06:00:00Z",
        "status": "completed",
        "requests": [],
        "steps": [],
        "relationships": [
            {
                "id": "rel-run-of",
                "type": "run-of",
                "source": {"id": "run-1", "type": "run"},
                "target": {"id": "workflow-1", "type": "workflow", "external": True},
            }
        ],
    }

    report = validate_aios_artifact(
        _write_artifact(tmp_path, payload),
        mode="conformance",
        spec_root=SPEC_ROOT,
    )

    assert report.aligned is True
