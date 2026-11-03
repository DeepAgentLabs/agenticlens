"""Authenticated, Lens-local evidence snapshots; no producer truth claims."""

import hashlib
import hmac
import json
from copy import deepcopy
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Coverage(BaseModel):
    """Caller-declared snapshot boundary; not proof of complete execution."""

    model_config = ConfigDict(extra="forbid", strict=True)
    stream_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    complete: bool


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    format: Literal["lens.evidence-manifest/1"] = "lens.evidence-manifest/1"
    key_id: str = Field(min_length=1)
    coverage: Coverage
    record_count: int = Field(ge=0)
    root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authentication: str = Field(pattern=r"^[0-9a-f]{64}$")


class Verification(BaseModel):
    """Consumers must require verified; other statuses never establish coverage."""

    status: Literal["verified", "failed", "unknown", "incomplete"]
    reason: str
    authenticated: bool = False
    coverage: Coverage | None = None
    record_count: int = 0


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def _root(records: list[dict[str, Any]]) -> str:
    previous = hashlib.sha256(b"lens.evidence-chain/1").digest()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError("Evidence records must be JSON objects")
        previous = hashlib.sha256(previous + _canonical([index, record])).digest()
    return previous.hex()


def _mac(manifest: Manifest, key: bytes) -> str:
    if len(key) < 32:
        raise ValueError("Authentication keys must contain at least 32 bytes")
    body = manifest.model_dump(exclude={"authentication"})
    return hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()


def seal(records: list[dict[str, Any]], *, coverage: Coverage, key_id: str, key: bytes) -> Manifest:
    """Authenticate an ordered snapshot with an externally provisioned HMAC key."""
    manifest = Manifest(
        key_id=key_id,
        coverage=coverage.model_copy(deep=True),
        record_count=len(records),
        root_sha256=_root(records),
        authentication="0" * 64,
    )
    manifest.authentication = _mac(manifest, key)
    return manifest


def verify(
    records: list[dict[str, Any]],
    manifest: Manifest,
    *,
    trusted_keys: dict[str, bytes],
    expected_stream_id: str,
) -> Verification:
    """Check authentication before trusting coverage or the snapshot root.

    The expected stream is supplied by the caller, never inferred from evidence.
    Missing/revoked keys are unknown; malformed input is failed.
    """
    key = trusted_keys.get(manifest.key_id)
    if key is None:
        return Verification(status="unknown", reason="No trusted key for manifest")
    try:
        valid = hmac.compare_digest(_mac(manifest, key), manifest.authentication)
    except (ValueError, TypeError):
        valid = False
    if not valid:
        return Verification(status="failed", reason="Manifest authentication failed")
    if manifest.coverage.stream_id != expected_stream_id:
        return Verification(status="failed", reason="Unexpected evidence stream")
    try:
        matches = len(records) == manifest.record_count and hmac.compare_digest(
            _root(records), manifest.root_sha256
        )
    except (ValueError, TypeError, OverflowError):
        matches = False
    if not matches:
        return Verification(status="failed", reason="Evidence count or chain root mismatch")
    return Verification(
        status="verified" if manifest.coverage.complete else "incomplete",
        reason="Authenticated snapshot matches; completeness is producer-declared",
        authenticated=True,
        coverage=manifest.coverage.model_copy(deep=True),
        record_count=len(records),
    )


def replay(
    records: list[dict[str, Any]],
    manifest: Manifest,
    *,
    trusted_keys: dict[str, bytes],
    expected_stream_id: str,
) -> list[dict[str, Any]]:
    """Return verified records in capture order without executing producer code."""
    result = verify(
        records, manifest, trusted_keys=trusted_keys, expected_stream_id=expected_stream_id
    )
    if result.status != "verified":
        raise ValueError(f"Evidence replay refused: {result.status}: {result.reason}")
    return deepcopy(records)


__all__ = ["Coverage", "Manifest", "Verification", "replay", "seal", "verify"]
