"""Authenticated coverage rejects tampering, truncation and untrusted manifests."""

from copy import deepcopy

import pytest

from agenticlens.integrity import Coverage, Manifest, replay, seal, verify

KEY = b"test-only-key-with-at-least-32-bytes"
RECORDS = [{"event_id": "a", "kind": "dispatch"}, {"event_id": "b", "kind": "completion"}]


def checkpoint(complete=True):
    return seal(
        RECORDS,
        coverage=Coverage(stream_id="run-1", description="entire saved journal", complete=complete),
        key_id="2026-11",
        key=KEY,
    )


def check(records, manifest, keys=None):
    return verify(
        records,
        manifest,
        trusted_keys={"2026-11": KEY} if keys is None else keys,
        expected_stream_id="run-1",
    )


def test_roundtrip_and_replay_preserve_source():
    manifest = Manifest.model_validate_json(checkpoint().model_dump_json())
    assert check(RECORDS, manifest).status == "verified"
    output = replay(RECORDS, manifest, trusted_keys={"2026-11": KEY}, expected_stream_id="run-1")
    output[0]["kind"] = "changed"
    assert RECORDS[0]["kind"] == "dispatch"


@pytest.mark.parametrize(
    "attack", ["modify", "reorder", "duplicate", "missing", "truncate", "append"]
)
def test_evidence_tampering(attack):
    records = deepcopy(RECORDS)
    if attack == "modify":
        records[0]["kind"] = "denied"
    elif attack == "reorder":
        records.reverse()
    elif attack == "duplicate":
        records[1] = records[0]
    elif attack == "missing":
        records.pop(0)
    elif attack == "truncate":
        records.pop()
    else:
        records.append({"kind": "extra"})
    assert check(records, checkpoint()).status == "failed"


def test_rewritten_local_chain_and_manifest_cannot_authenticate():
    forged = checkpoint().model_copy(update={"root_sha256": "0" * 64, "record_count": 0})
    assert check([], forged).status == "failed"
    assert check(RECORDS, checkpoint(), {"2026-11": b"x" * 32}).status == "failed"
    assert check(RECORDS, checkpoint(), {}).status == "unknown"


def test_incomplete_and_wrong_stream_fail_closed():
    assert check(RECORDS, checkpoint(False)).status == "incomplete"
    assert (
        verify(
            RECORDS, checkpoint(), trusted_keys={"2026-11": KEY}, expected_stream_id="other"
        ).status
        == "failed"
    )
    with pytest.raises(ValueError, match="incomplete"):
        replay(
            RECORDS, checkpoint(False), trusted_keys={"2026-11": KEY}, expected_stream_id="run-1"
        )


def test_non_json_and_short_keys_rejected():
    with pytest.raises(ValueError):
        seal(RECORDS, coverage=checkpoint().coverage, key_id="short", key=b"short")
    assert check([{"value": float("nan")}], checkpoint()).status == "failed"


def test_cli_verification_and_invalid_input(tmp_path):
    import json

    from typer.testing import CliRunner

    from agenticlens.cli.main import app

    records = tmp_path / "records.json"
    manifest = tmp_path / "manifest.json"
    keys = tmp_path / "keys.json"
    records.write_text(json.dumps(RECORDS))
    manifest.write_text(checkpoint().model_dump_json())
    keys.write_text(json.dumps({"2026-11": KEY.hex()}))
    args = [
        "evidence",
        "verify",
        str(records),
        str(manifest),
        "--stream-id",
        "run-1",
        "--key-file",
        str(keys),
    ]
    runner = CliRunner()
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "verified"
    records.write_text("[]")
    assert runner.invoke(app, args).exit_code == 1
    records.write_text("invalid json")
    assert json.loads(runner.invoke(app, args).output)["status"] == "failed"


@pytest.mark.parametrize("field,value", [("key_id", "other"), ("record_count", 0)])
def test_manifest_metadata_is_authenticated(field, value):
    changed = checkpoint().model_copy(update={field: value})
    assert check(RECORDS, changed).status != "verified"


def test_coverage_cannot_be_upgraded_without_key():
    manifest = checkpoint(False)
    manifest.coverage.complete = True
    assert check(RECORDS, manifest).status == "failed"
    with pytest.raises(ValueError, match="unknown"):
        replay(RECORDS, checkpoint(), trusted_keys={}, expected_stream_id="run-1")


def test_empty_snapshot_is_explicitly_counted():
    manifest = seal([], coverage=checkpoint().coverage, key_id="2026-11", key=KEY)
    result = check([], manifest)
    assert result.status == "verified"
    assert result.record_count == 0
