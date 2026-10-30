"""Read sidecar.correlation/1 projections without executing Sidecar."""

from copy import deepcopy
from datetime import datetime
from typing import Any

from agenticlens.models.trace import Run

STATUSES = {"ALLOW", "WARN", "BLOCK", "CHALLENGE", "REPLAN", "PAUSE", "ESCALATE"}


def attach_decisions(run: Run, records: list[dict[str, Any]]) -> None:
    """Validate the whole batch, then attach idempotently to its exact span.

    A supervision BLOCK is a producer outcome, not a failed span/run. This
    projection carries no execution/completion or independently verified hash.
    """
    by_id = {span.span_id: span for span in run.spans}
    pending = []
    seen: dict[str, dict[str, Any]] = {}
    for span in run.spans:
        for existing in span.attributes.get("sidecar.decisions", []):
            seen[existing["decision"]["decision_id"]] = existing
    for raw in records:
        record = deepcopy(raw)
        if record.get("contract_version") != "sidecar.correlation/1":
            raise ValueError("Unsupported Sidecar correlation contract")
        correlation = record["correlation"]
        if correlation["run_id"] != run.run_id or correlation["trace_id"] != run.trace_id:
            raise ValueError("Sidecar run/trace correlation mismatch")
        span_id = correlation["span_id"]
        if span_id not in by_id:
            raise ValueError("Unknown Sidecar target span")
        decision = record["decision"]
        if decision["status"] not in STATUSES or not decision.get("decision_id"):
            raise ValueError("Invalid Sidecar decision")
        if not isinstance(decision.get("reason"), str):
            raise ValueError("Sidecar decision reason must be a string")
        if not isinstance(decision["decision_id"], str):
            raise ValueError("Sidecar decision identity must be a string")
        for key in ("task_id", "source_event_id", "policy_version", "tool_name", "boundary"):
            if not isinstance(record.get(key), str) or not record[key]:
                raise ValueError(f"Missing Sidecar {key}")
        timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Sidecar timestamp must be timezone-aware")
        identity = decision["decision_id"]
        if identity in seen:
            if seen[identity] != record:
                raise ValueError("Conflicting Sidecar decision identity")
            continue
        seen[identity] = record
        pending.append((by_id[span_id], record))
    for span, record in pending:
        span.attributes.setdefault("sidecar.decisions", []).append(record)


def verify_journal(events: list[dict[str, Any]], *, task_id: str) -> None:
    """Verify complete native Sidecar JSONL readback before evidence correlation.

    Hash chains detect tampering/reordering, not a rewritten chain by its owner.
    Retain an independently trusted anchor for that threat model.
    """
    import hashlib
    import json

    previous = ""
    for sequence, raw in enumerate(events, 1):
        event = deepcopy(raw)
        digest = event.pop("digest")
        calculated = hashlib.sha256(
            json.dumps(
                event,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode()
        ).hexdigest()
        if (
            event["task_id"] != task_id
            or event["sequence"] != sequence
            or event["previous_hash"] != previous
            or digest != calculated
        ):
            raise ValueError("Invalid Sidecar audit chain or task identity")
        previous = digest
