"""Small producer-side checks; no AIOS runtime dependency or network access."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit


def timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("A timezone-aware observation time is required")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def identifier(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A nonempty public identifier is required")
    return value


def reference(value: Mapping[str, Any]) -> dict[str, str]:
    allowed = {"id", "producer", "artifact_id", "format", "object_id", "uri"}
    required = {"id", "producer", "artifact_id", "format"}
    if not required <= value.keys() or not value.keys() <= allowed:
        raise ValueError("Reference fields must follow the 0.8-draft reference shape")
    result = {key: identifier(item) for key, item in value.items()}
    if "uri" in result and not urlsplit(result["uri"]).scheme:
        raise ValueError("Reference URI must be absolute")
    return result
