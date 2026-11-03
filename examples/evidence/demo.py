"""Offline authenticated snapshot and tampering example. Run from repository root."""

import secrets
from copy import deepcopy

from agenticlens.integrity import Coverage, replay, seal, verify


def main() -> None:
    key = secrets.token_bytes(32)
    records = [
        {"event_id": "event-1", "kind": "dispatch", "decision_id": "decision-1"},
        {"event_id": "event-2", "kind": "completion", "dispatch_id": "event-1"},
    ]
    manifest = seal(
        records,
        coverage=Coverage(stream_id="demo", description="entire saved journal", complete=True),
        key_id="demo-ephemeral",
        key=key,
    )
    options = {"demo-ephemeral": key}
    assert (
        verify(records, manifest, trusted_keys=options, expected_stream_id="demo").status
        == "verified"
    )
    assert replay(records, manifest, trusted_keys=options, expected_stream_id="demo") == records
    tampered = deepcopy(records)
    tampered[0]["kind"] = "denied"
    assert (
        verify(tampered, manifest, trusted_keys=options, expected_stream_id="demo").status
        == "failed"
    )
    assert (
        verify(records[:-1], manifest, trusted_keys=options, expected_stream_id="demo").status
        == "failed"
    )
    print("Verified capture-order replay; tampering and truncation rejected.")


if __name__ == "__main__":
    main()
