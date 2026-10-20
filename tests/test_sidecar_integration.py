"""Versioned native supervision readback, atomicity and exact trace identity."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from agenticlens.diagnosis import diagnose_run
from agenticlens.integrations.sidecar import STATUSES, attach_decisions
from agenticlens.models.trace import Run, RunStatus, Span, SpanType


def fixture() -> dict:
    return json.loads((Path(__file__).parent / "fixtures/sidecar-correlation-v1.json").read_text())


def run() -> Run:
    return Run(
        run_id="run-fixture",
        trace_id="trace-fixture",
        application_name="test",
        spans=[Span(span_id="span-fixture", name="read", span_type=SpanType.TOOL_CALL)],
    )


@pytest.mark.parametrize("status", sorted(STATUSES))
def test_outcomes_are_not_span_failures(status: str) -> None:
    recording = run()
    evidence = fixture()
    evidence["decision"]["status"] = status
    attach_decisions(recording, [evidence, evidence])
    assert len(recording.spans[0].attributes["sidecar.decisions"]) == 1
    assert recording.spans[0].status == RunStatus.RUNNING
    assert any(
        e.kind == "supervision_decision" and status in e.description
        for e in diagnose_run(recording).timeline.events
    )


@pytest.mark.parametrize(
    "key,value", [("run_id", "wrong"), ("trace_id", "wrong"), ("span_id", "wrong")]
)
def test_correlation_mismatch_is_atomic(key: str, value: str) -> None:
    recording = run()
    good = fixture()
    bad = deepcopy(good)
    bad["correlation"][key] = value
    with pytest.raises(ValueError):
        attach_decisions(recording, [good, bad])
    assert recording.spans[0].attributes == {}


def test_conflicting_duplicate_and_version_rejected() -> None:
    recording = run()
    good = fixture()
    attach_decisions(recording, [good])
    bad = deepcopy(good)
    bad["decision"]["status"] = "BLOCK"
    with pytest.raises(ValueError, match="Conflicting"):
        attach_decisions(recording, [bad])
    bad["contract_version"] = "unknown"
    with pytest.raises(ValueError, match="Unsupported"):
        attach_decisions(recording, [bad])


def test_native_journal_integrity() -> None:
    import hashlib

    from agenticlens.integrations.sidecar import verify_journal

    event = {"task_id": "task", "sequence": 1, "previous_hash": "", "payload": {"status": "BLOCK"}}
    event["digest"] = hashlib.sha256(
        json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    verify_journal([event], task_id="task")
    event["payload"]["status"] = "ALLOW"
    with pytest.raises(ValueError, match="audit"):
        verify_journal([event], task_id="task")


@pytest.mark.parametrize("reason", [None, 42, {"private": "value"}])
def test_invalid_reason_batch_is_rejected_before_mutation(reason: object) -> None:
    recording = run()
    good = fixture()
    bad = deepcopy(good)
    bad["decision"]["decision_id"] = "different-decision"
    bad["decision"]["reason"] = reason
    with pytest.raises(ValueError, match="reason"):
        attach_decisions(recording, [good, bad])
    assert recording.spans[0].attributes == {}


def test_missing_reason_batch_is_rejected_before_mutation() -> None:
    recording = run()
    good = fixture()
    bad = deepcopy(good)
    bad["decision"]["decision_id"] = "different-decision"
    del bad["decision"]["reason"]
    with pytest.raises(ValueError, match="reason"):
        attach_decisions(recording, [good, bad])
    assert recording.spans[0].attributes == {}


def test_v09_authority_evidence_is_native_and_redacted_summary_is_not():
    from agenticlens.integrations.sidecar import verify_journal

    native = json.loads((Path(__file__).parent / "fixtures/sidecar-v09-authority.json").read_text())
    event = next(e for e in native["events"] if e["kind"] == "decision")
    authority = event["payload"]["context"]["metadata"]["sidecar.authority"]
    assert authority["task_id"] == "case-fixture"
    assert authority["agent_id"] == "refund-agent"
    assert authority["grant_id"] and authority["parent_intent_id"]
    assert native["correlated"][0]["decision"] == event["payload"]["decision"]
    task_id = native["events"][0]["task_id"]
    verify_journal(native["events"], task_id=task_id)
    recording = run()
    attach_decisions(recording, native["correlated"])
    assert recording.spans[0].attributes["sidecar.decisions"][0]["decision"]["status"] == "BLOCK"
    assert recording.spans[0].status == RunStatus.RUNNING
    with pytest.raises(ValueError, match="Unsupported"):
        attach_decisions(run(), [native["redacted"]])
