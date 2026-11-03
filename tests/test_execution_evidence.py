"""Capture/export/import and redacted downstream verification of AIOS evidence."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.integrity import Coverage, Manifest, Verification, seal
from agenticlens.integrity.execution import (
    NAMESPACE,
    ExecutionBundle,
    ExecutionRecord,
    capture_execution,
    execution_summary,
    export_execution,
    import_execution,
    replay_execution,
    verify_execution,
)
from agenticlens.models.trace import Run, RunStatus, Span, SpanType

KEY = b"execution-demo-key-at-least-32-bytes"


def capture(complete=True):
    run = Run(
        run_id="run-evidence",
        trace_id="trace-evidence",
        application_name="demo",
        status=RunStatus.SUCCEEDED,
        spans=[Span(span_id="tool", name="read", span_type=SpanType.TOOL_CALL)],
    )
    records = [
        ExecutionRecord(
            event_id=str(i),
            run_id=run.run_id,
            span_id="tool",
            occurred_at="2026-11-02T10:00:00Z",
            kind=kind,
            producer="fixture-host",
            decision_id="decision-1",
            action_id="action-1",
            actor="test-agent",
            policy_version="p1",
            approval_id="approval-1",
            attributes={"secret": "private"},
        )
        for i, kind in enumerate(["proposed", "allowed", "dispatched", "completed"])
    ]
    return (
        run,
        records,
        capture_execution(
            run,
            records,
            coverage=Coverage(stream_id=run.run_id, description="fixture", complete=complete),
            key_id="test",
            key=KEY,
        ),
    )


def test_lossless_roundtrip_and_no_execution(monkeypatch):
    run, records, bundle = capture()
    native, imported = replay_execution(
        bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id
    )
    assert native == run
    assert imported == records
    assert bundle.artifact["spec_version"] == "0.4-draft"
    assert import_execution(json.loads(json.dumps(bundle.artifact))) == (run, records)
    # No callback is accepted or evaluated, even when payloads contain code-looking text.
    run.metadata["code"] = "raise RuntimeError('must never execute')"
    assert import_execution(export_execution(run, []))[0] == run


@pytest.mark.parametrize(
    "complete,keys,status",
    [
        (True, {"test": KEY}, "verified"),
        (False, {"test": KEY}, "incomplete"),
        (True, {}, "unknown"),
    ],
)
def test_downstream_statuses_and_redaction(complete, keys, status):
    run, _, bundle = capture(complete)
    summary = execution_summary(bundle, trusted_keys=keys, expected_run_id=run.run_id)
    assert summary["verification"]["status"] == status
    assert "private" not in json.dumps(summary)
    assert bool(summary["causal_links"]) == (status == "verified")
    if status == "verified":
        assert summary["causal_links"][0]["decision_id"] == "decision-1"


def test_projection_mismatch_rejected_even_if_authenticated():
    run, _, bundle = capture()
    bundle.artifact["steps"][0]["name"] = "forged projection"
    bundle.manifest = seal(
        [bundle.artifact], coverage=bundle.manifest.coverage, key_id="test", key=KEY
    )
    result = verify_execution(bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id)
    assert result.status == "failed"
    with pytest.raises(ValueError):
        replay_execution(bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id)


@pytest.mark.parametrize("attack", ["schema", "reference", "event", "truncate"])
def test_invalid_capture_or_tampering(attack):
    run, _, bundle = capture()
    if attack == "schema":
        bundle.artifact["spec_version"] = "0.99-draft"
    elif attack == "reference":
        bundle.artifact["events"][0]["object_id"] = "unknown"
    elif attack == "event":
        bundle.artifact["events"][0]["extensions"][NAMESPACE]["kind"] = "denied"
    else:
        bundle.artifact["events"].pop()
    assert (
        verify_execution(bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id).status
        == "failed"
    )
    # A valid MAC still cannot make an invalid AIOS mapping valid.
    bundle.manifest = seal(
        [bundle.artifact], coverage=bundle.manifest.coverage, key_id="test", key=KEY
    )
    assert (
        verify_execution(bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id).status
        == "failed"
    )


def test_wrong_run_duplicate_events_and_unknown_span():
    run, records, bundle = capture()
    assert (
        verify_execution(bundle, trusted_keys={"test": KEY}, expected_run_id="other").status
        == "failed"
    )
    for replacement in [{"run_id": "other"}, {"span_id": "missing"}]:
        bad = records[0].model_copy(update=replacement)
        with pytest.raises(ValueError, match="correlation"):
            export_execution(run, [bad])
    with pytest.raises(ValueError, match="Duplicate"):
        export_execution(run, [records[0], records[0]])
    with pytest.raises(ValueError, match="timezone"):
        ExecutionRecord.model_validate(
            {**records[0].model_dump(), "occurred_at": "2026-11-02T10:00:00"}
        )


def test_cli_export_and_replay(tmp_path):
    run, records, _ = capture()
    native = tmp_path / "run.json"
    observations = tmp_path / "records.json"
    keys = tmp_path / "keys.json"
    output = tmp_path / "bundle.json"
    native.write_text(run.model_dump_json())
    observations.write_text(json.dumps([r.model_dump() for r in records]))
    keys.write_text(json.dumps({"test": KEY.hex()}))
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "evidence",
            "export",
            str(native),
            str(observations),
            str(output),
            "--key-id",
            "test",
            "--key-file",
            str(keys),
            "--complete",
        ],
    )
    assert result.exit_code == 0, result.output
    args = ["evidence", "replay", str(output), "--run-id", run.run_id, "--key-file", str(keys)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert [r["kind"] for r in json.loads(result.output)["records"]] == [r.kind for r in records]
    output.write_text("{}")
    assert runner.invoke(app, args).exit_code == 1


def test_schema_files_match_models():
    from agenticlens.integrity.execution import ExecutionRecord

    for name, model in [
        ("manifest", Manifest),
        ("verification", Verification),
        ("execution-bundle", ExecutionBundle),
        ("execution-record", ExecutionRecord),
    ]:
        path = Path(__file__).parents[1] / "schemas" / "integrity" / (name + ".schema.json")
        assert json.loads(path.read_text()) == model.model_json_schema()


def test_published_valid_and_truncated_fixtures():
    root = Path(__file__).parents[1] / "examples" / "evidence" / "fixtures"
    for filename, status in [("valid.json", "verified"), ("truncated.json", "failed")]:
        bundle = ExecutionBundle.model_validate_json((root / filename).read_text())
        assert (
            verify_execution(
                bundle, trusted_keys={"test": KEY}, expected_run_id="run-evidence"
            ).status
            == status
        )


def test_unknown_native_schema_cannot_silently_lose_fields():
    run, _, _ = capture()
    run.schema_version = "2.0"
    with pytest.raises(ValueError, match="schema version"):
        export_execution(run, [])


def test_packaged_aios_contracts_match_pinned_source(tmp_path):
    import hashlib

    from agenticlens.validation.aios import _resolve_spec

    resolved = _resolve_spec(artifact_type="run", spec_version="0.4", explicit_root=None)
    assert "schemas/aios/specification/v0.4" in resolved.root.as_posix()
    provenance = json.loads((resolved.root / "SOURCE.json").read_text())
    assert len(provenance["commit"]) == 40
    for name, expected in provenance["files"].items():
        assert hashlib.sha256((resolved.root / name).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("failure", ["missing", "unreadable", "invalid-catalog"])
def test_verifier_setup_errors_are_unknown_and_redacted(monkeypatch, failure):
    from agenticlens.integrity import execution
    from agenticlens.validation.aios import SpecUnavailableError

    run, _, bundle = capture()
    errors = {
        "missing": SpecUnavailableError("sensitive-local-path"),
        "unreadable": OSError("sensitive-local-path"),
        "invalid-catalog": json.JSONDecodeError("sensitive-value", "bad", 0),
    }

    def unavailable(*args, **kwargs):
        raise errors[failure]

    monkeypatch.setattr(execution, "validate_aios_artifact", unavailable)
    summary = execution_summary(bundle, trusted_keys={"test": KEY}, expected_run_id=run.run_id)
    assert summary["verification"]["status"] == "unknown"
    assert summary["causal_links"] == []
    assert "sensitive" not in json.dumps(summary)
