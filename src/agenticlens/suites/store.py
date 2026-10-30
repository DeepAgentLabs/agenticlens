"""Approved, immutable suite versions on local disk.

Layout: `<root>/<suite name>/<version>.json`, one `SuiteVersion` per file.

- Approval runs checks first (every case reviewed and none rejected, no
  unmasked PII, no conflicting duplicates) and records them.
- A version is written once, with exclusive create. Approving the same
  name and version again succeeds only when the content is identical.
- Every read recomputes the content hash, so a hand-edited or corrupted
  version is reported instead of silently evaluated.

Suite names and versions must be plain path segments (letters, digits,
`.`, `_`, `-`) so they cannot escape the store directory.
"""

import hashlib
import json
import re
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_evals import TestSuite
from pydantic import ValidationError

from agenticlens.suites.duplicates import find_duplicates
from agenticlens.suites.editing import case_review_status
from agenticlens.suites.models import (
    ApprovalCheck,
    ApprovalRecord,
    SuiteVersion,
    VerificationResult,
)
from agenticlens.suites.pii import PIIMasker, scan_suite

_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PROVENANCE_KEY = "agenticlens_suite_version"


class SuiteStoreError(ValueError):
    """Base error for suite store operations."""


class ApprovalError(SuiteStoreError):
    """The suite failed one or more approval checks."""

    def __init__(self, checks: list[ApprovalCheck]) -> None:
        self.checks = checks
        failed = "; ".join(f"{check.name}: {check.detail}" for check in checks if not check.passed)
        super().__init__(f"approval refused: {failed}")


class ImmutableVersionError(SuiteStoreError):
    """A different suite was already approved under this name and version."""


class IntegrityError(SuiteStoreError):
    """A stored version's content no longer matches its recorded hash."""


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_sha256(suite_data: dict[str, Any]) -> str:
    """SHA-256 of a suite's canonical JSON (sorted keys, no whitespace)."""
    return hashlib.sha256(canonical_json(suite_data).encode("utf-8")).hexdigest()


def record_sha256(envelope: dict[str, Any]) -> str:
    """SHA-256 of a stored envelope's canonical JSON, excluding `record_sha256`."""
    return content_sha256({k: v for k, v in envelope.items() if k != "record_sha256"})


def parse_ref(ref: str) -> tuple[str, str]:
    """Split `name@version`."""
    name, separator, version = ref.rpartition("@")
    if not separator or not name or not version:
        raise SuiteStoreError(f"expected NAME@VERSION, got {ref!r}")
    return name, version


def _check_segment(kind: str, value: str) -> str:
    if not _SEGMENT.fullmatch(value) or value in {".", ".."}:
        raise SuiteStoreError(
            f"suite {kind} {value!r} must use only letters, digits, '.', '_', and '-'"
        )
    return value


def approval_checks(
    suite: TestSuite,
    *,
    allow_unreviewed: bool = False,
    allow_pii: bool = False,
    masker: PIIMasker | None = None,
) -> list[ApprovalCheck]:
    """The checks `approve` runs, without writing anything."""
    statuses = [case_review_status(case) for case in suite.cases]
    rejected = [
        case.id for case, status in zip(suite.cases, statuses, strict=True) if status == "rejected"
    ]
    pending = [
        case.id
        for case, status in zip(suite.cases, statuses, strict=True)
        if status == "needs_review"
    ]
    accepted = statuses.count("accepted")
    if rejected:
        review = ApprovalCheck(
            name="review",
            passed=False,
            detail=f"{len(rejected)} rejected case(s) must be removed: {', '.join(rejected)}",
        )
    elif pending and not allow_unreviewed:
        review = ApprovalCheck(
            name="review",
            passed=False,
            detail=f"{len(pending)} case(s) need review: {', '.join(pending)}",
        )
    else:
        detail = f"{accepted}/{len(statuses)} case(s) accepted"
        if pending:
            detail += f"; {len(pending)} approved without review (allow_unreviewed)"
        review = ApprovalCheck(name="review", passed=True, detail=detail)

    pii = scan_suite(suite, masker)
    if pii.total and not allow_pii:
        kinds = ", ".join(f"{name}={count}" for name, count in pii.counts.items())
        pii_check = ApprovalCheck(
            name="pii", passed=False, detail=f"{pii.total} unmasked value(s) found ({kinds})"
        )
    else:
        detail = "no unmasked PII detected"
        if pii.total:
            detail = f"{pii.total} unmasked value(s) approved as-is (allow_pii)"
        pii_check = ApprovalCheck(name="pii", passed=True, detail=detail)

    duplicates = find_duplicates(suite)
    conflicts = [group for group in duplicates.groups if group.conflicting]
    if conflicts:
        ids = "; ".join(", ".join(group.case_ids) for group in conflicts)
        duplicate_check = ApprovalCheck(
            name="conflicting_duplicates",
            passed=False,
            detail=f"same input, different expectations: {ids}",
        )
    else:
        duplicate_check = ApprovalCheck(
            name="conflicting_duplicates",
            passed=True,
            detail=f"none ({len(duplicates.groups)} non-conflicting duplicate group(s))",
        )
    return [review, pii_check, duplicate_check]


class SuiteStore:
    """A directory of approved suite versions."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def path_for(self, name: str, version: str) -> Path:
        return (
            self.root / _check_segment("name", name) / f"{_check_segment('version', version)}.json"
        )

    def approve(
        self,
        suite: TestSuite,
        *,
        approved_by: str,
        notes: str = "",
        approved_at: datetime | None = None,
        parent_version: str | None = None,
        allow_unreviewed: bool = False,
        allow_pii: bool = False,
        masker: PIIMasker | None = None,
    ) -> SuiteVersion:
        """Run approval checks and store `suite` as an immutable version.

        Raises `ApprovalError` when a check fails and `ImmutableVersionError`
        when a different suite already holds this name and version.
        """
        if not approved_by.strip():
            raise SuiteStoreError("approved_by must not be empty")
        path = self.path_for(suite.name, suite.version)
        if parent_version is not None:
            _check_segment("version", parent_version)
            if parent_version == suite.version:
                raise SuiteStoreError("parent_version must differ from the approved version")
            self.get(suite.name, parent_version)
        checks = approval_checks(
            suite, allow_unreviewed=allow_unreviewed, allow_pii=allow_pii, masker=masker
        )
        if not all(check.passed for check in checks):
            raise ApprovalError(checks)

        suite_data = suite.model_dump(mode="json")
        digest = content_sha256(suite_data)
        if path.exists():
            existing = self.get(suite.name, suite.version)
            if existing.content_sha256 == digest:
                return existing
            raise ImmutableVersionError(
                f"{suite.name}@{suite.version} is already approved with different content "
                f"(sha256 {existing.content_sha256[:12]}); approve it under a new version"
            )
        record = SuiteVersion(
            name=suite.name,
            version=suite.version,
            content_sha256=digest,
            case_count=len(suite.cases),
            parent_version=parent_version,
            approval=ApprovalRecord(
                approved_by=approved_by,
                approved_at=approved_at or datetime.now(timezone.utc),
                notes=notes,
                checks=checks,
            ),
            suite=suite_data,
        )
        record.record_sha256 = record_sha256(record.model_dump(mode="json"))
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(record.model_dump_json(indent=2) + "\n")
        except FileExistsError as exc:
            raise ImmutableVersionError(
                f"{suite.name}@{suite.version} was approved concurrently"
            ) from exc
        return record

    def _read(self, path: Path) -> SuiteVersion:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            record = SuiteVersion.model_validate(raw)
        except (OSError, ValueError) as exc:
            raise IntegrityError(f"{path}: unreadable suite version: {exc}") from exc
        actual = content_sha256(record.suite)
        if actual != record.content_sha256:
            raise IntegrityError(
                f"{record.name}@{record.version} content changed after approval "
                f"(expected sha256 {record.content_sha256[:12]}, found {actual[:12]})"
            )
        envelope = record_sha256(raw)
        if envelope != record.record_sha256:
            raise IntegrityError(
                f"{record.name}@{record.version} approval record changed after approval "
                f"(expected sha256 {record.record_sha256[:12] or 'missing'}, "
                f"found {envelope[:12]})"
            )
        expected_path = self.path_for(record.name, record.version)
        if path.resolve() != expected_path.resolve():
            raise IntegrityError(f"{path} holds {record.name}@{record.version}; it was moved")
        try:
            suite = TestSuite.model_validate(record.suite)
        except ValidationError as exc:
            raise IntegrityError(f"{path}: stored suite is not a valid TestSuite: {exc}") from exc
        if (suite.name, suite.version) != (record.name, record.version):
            raise IntegrityError(f"{path}: envelope and suite name/version disagree")
        if len(suite.cases) != record.case_count:
            raise IntegrityError(f"{path}: case_count disagrees with the stored suite")
        return record

    def get(self, name: str, version: str) -> SuiteVersion:
        """A stored version, verified. Raises `SuiteStoreError` when missing or altered."""
        path = self.path_for(name, version)
        if not path.exists():
            raise SuiteStoreError(f"{name}@{version} is not in the store at {self.root}")
        return self._read(path)

    def load_suite(self, name: str, version: str) -> TestSuite:
        """The approved `TestSuite`, with approval provenance added to its metadata."""
        record = self.get(name, version)
        suite = TestSuite.model_validate(record.suite)
        provenance = {
            "name": record.name,
            "version": record.version,
            "content_sha256": record.content_sha256,
            "approved_by": record.approval.approved_by,
            "approved_at": record.approval.approved_at.isoformat(),
        }
        return suite.model_copy(update={"metadata": {**suite.metadata, PROVENANCE_KEY: provenance}})

    def _paths(self, name: str | None = None) -> Iterator[Path]:
        if not self.root.exists():
            return iter(())
        if name is not None:
            directory = self.root / _check_segment("name", name)
            return iter(sorted(directory.glob("*.json")) if directory.is_dir() else [])
        return iter(sorted(self.root.glob("*/*.json")))

    def versions(self, name: str | None = None) -> list[SuiteVersion]:
        """Every verified version, oldest approval first. Raises on an altered version."""
        records = [self._read(path) for path in self._paths(name)]
        return sorted(records, key=lambda record: (record.name, record.approval.approved_at))

    def latest(self, name: str) -> SuiteVersion:
        records = self.versions(name)
        if not records:
            raise SuiteStoreError(f"no approved versions of {name!r} in {self.root}")
        return records[-1]

    def verify(self, refs: list[tuple[str, str]] | None = None) -> list[VerificationResult]:
        """Check stored versions (all when `refs` is None) without raising."""
        if refs is None:
            paths = list(self._paths())
        else:
            paths = []
            for name, version in refs:
                paths.append(self.path_for(name, version))
        results: list[VerificationResult] = []
        for path in paths:
            name, version = path.parent.name, path.stem
            if not path.exists():
                results.append(
                    VerificationResult(
                        name=name, version=version, path=str(path), ok=False, error="not found"
                    )
                )
                continue
            try:
                record = self._read(path)
            except IntegrityError as exc:
                actual: str | None = None
                expected: str | None = None
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    expected = raw.get("content_sha256")
                    actual = content_sha256(raw["suite"])
                except (OSError, ValueError, KeyError, TypeError):
                    pass
                results.append(
                    VerificationResult(
                        name=name,
                        version=version,
                        path=str(path),
                        ok=False,
                        expected_sha256=expected,
                        actual_sha256=actual,
                        error=str(exc),
                    )
                )
                continue
            results.append(
                VerificationResult(
                    name=record.name,
                    version=record.version,
                    path=str(path),
                    ok=True,
                    expected_sha256=record.content_sha256,
                    actual_sha256=record.content_sha256,
                )
            )
        return results
