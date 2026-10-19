"""Append-only local routing records. No prompt, response or exception text."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def artifact_sha256(model: BaseModel) -> str:
    """Hash canonical model JSON, independent of file whitespace."""
    encoded = json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


class RoutingAuditLog:
    """Single-process JSONL sink; write failures propagate before further execution.

    fsync each record. This is an operational journal, not a tamper-proof or
    multi-process governance log. Do not share a path across concurrent writers.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, event: str, decision_id: str, record: BaseModel) -> None:
        payload: dict[str, Any] = {
            "event": event,
            "decision_id": decision_id,
            "record": record.model_dump(mode="json"),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
