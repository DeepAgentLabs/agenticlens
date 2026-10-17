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
