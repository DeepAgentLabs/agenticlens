"""Approval checks, immutable versions, integrity verification, and export provenance."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from agentic_evals import TestCase as EvalCase
from agentic_evals import TestSuite as EvalSuite

from agenticlens.suites import (
    PROVENANCE_KEY,
    ApprovalError,
    ImmutableVersionError,
    IntegrityError,
    PIIMasker,
    SuiteStore,
    SuiteStoreError,
    approval_checks,
    content_sha256,
    new_suite,
    parse_ref,
    review_cases,
    update_case,
)

APPROVED_AT = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)


def _suite(version: str = "1.0.0", **case_extra: object) -> EvalSuite:
    return new_suite(
        name="support",
        version=version,
        cases=[
            EvalCase.model_validate(
                {"id": "a", "name": "a", "input": "hi", "expected_output": "x", **case_extra}
            ),
            EvalCase(id="b", name="b", input="bye", expected_output="y"),
        ],
    )


def _approve(store: SuiteStore, suite: EvalSuite, **kwargs: object) -> object:
    return store.approve(suite, approved_by="qa-lead", approved_at=APPROVED_AT, **kwargs)  # type: ignore[arg-type]


def test_approve_writes_verified_immutable_version(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    record = store.approve(_suite(), approved_by="qa-lead", approved_at=APPROVED_AT, notes="v1")
    path = tmp_path / "support" / "1.0.0.json"
    assert path.exists()
    assert record.content_sha256 == content_sha256(_suite().model_dump(mode="json"))
    assert record.case_count == 2
    assert record.approval.approved_by == "qa-lead" and record.approval.notes == "v1"
    assert [c.name for c in record.approval.checks] == ["review", "pii", "conflicting_duplicates"]
    assert store.get("support", "1.0.0") == record
    # Re-approving identical content is idempotent; different content is refused.
    assert _approve(store, _suite()) == record
    with pytest.raises(ImmutableVersionError, match="already approved"):
        _approve(store, update_case(_suite(), "a", expected_output="changed"))


def test_approve_records_default_timestamp(tmp_path: Path) -> None:
    record = SuiteStore(tmp_path).approve(_suite(), approved_by="qa")
    assert record.approval.approved_at.tzinfo is not None


def test_approval_refuses_unreviewed_rejected_pii_and_conflicts(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    pending = _suite(metadata={"review_status": "needs_review"})
    with pytest.raises(ApprovalError, match="need review: a") as excinfo:
        _approve(store, pending)
    assert [check.passed for check in excinfo.value.checks] == [False, True, True]
    assert (
        _approve(store, pending, allow_unreviewed=True)
        .approval.checks[0]
        .detail.endswith("(allow_unreviewed)")
    )

    rejected = review_cases(_suite("2"), status="rejected", reviewer="qa", case_ids=["a"])
    with pytest.raises(ApprovalError, match="rejected case"):
        _approve(store, rejected, allow_unreviewed=True)

    leaky = _suite("3", input="email me at a@b.io")
    with pytest.raises(ApprovalError, match=r"pii: 1 unmasked value\(s\) found \(email=1\)"):
        _approve(store, leaky)
    assert "allow_pii" in _approve(store, leaky, allow_pii=True).approval.checks[1].detail

    conflict = update_case(_suite("4"), "b", input="hi")
    with pytest.raises(ApprovalError, match="same input, different expectations: a, b"):
        _approve(store, conflict)


def test_approval_checks_use_custom_masker() -> None:
    suite = _suite(input={"employee_id": "E-1"})
    assert all(check.passed for check in approval_checks(suite))
    strict = PIIMasker(sensitive_keys=("employee_id",))
    assert not approval_checks(suite, masker=strict)[1].passed


def test_parent_version_must_exist(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    _approve(store, _suite())
    record = _approve(store, _suite("1.1.0"), parent_version="1.0.0")
    assert record.parent_version == "1.0.0"
    with pytest.raises(SuiteStoreError, match="not in the store"):
        _approve(store, _suite("1.2.0"), parent_version="0.9.0")
    with pytest.raises(SuiteStoreError, match="must differ"):
        _approve(store, _suite("1.3.0"), parent_version="1.3.0")


@pytest.mark.parametrize("name", ["../escape", "a/b", ".hidden", "with space", ".."])
def test_store_rejects_unsafe_names(tmp_path: Path, name: str) -> None:
    suite = _suite().model_copy(update={"name": name})
    with pytest.raises(SuiteStoreError, match="must use only"):
        _approve(SuiteStore(tmp_path), suite)


def test_store_requires_approver(tmp_path: Path) -> None:
    with pytest.raises(SuiteStoreError, match="approved_by"):
        SuiteStore(tmp_path).approve(_suite(), approved_by=" ")


def test_tampering_is_detected(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    _approve(store, _suite())
    path = tmp_path / "support" / "1.0.0.json"
    data = json.loads(path.read_text("utf-8"))
    data["suite"]["cases"][0]["expected_output"] = "edited"
    path.write_text(json.dumps(data), "utf-8")
    with pytest.raises(IntegrityError, match="changed after approval"):
        store.get("support", "1.0.0")
    (result,) = store.verify()
    assert not result.ok and result.expected_sha256 != result.actual_sha256
    with pytest.raises(IntegrityError):
        store.versions()


def test_moved_or_corrupt_versions_fail_verification(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    _approve(store, _suite())
    source = tmp_path / "support" / "1.0.0.json"
    (tmp_path / "support" / "9.9.9.json").write_text(source.read_text("utf-8"), "utf-8")
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "1.json").write_text("{not json", "utf-8")
    results = {f"{r.name}@{r.version}": r for r in store.verify()}
    assert results["support@1.0.0"].ok
    assert "was moved" in (results["support@9.9.9"].error or "")
    assert "unreadable" in (results["other@1"].error or "")
    missing = store.verify([("support", "2.0.0")])
    assert missing[0].error == "not found"


def test_versions_latest_and_load_suite(tmp_path: Path) -> None:
    store = SuiteStore(tmp_path)
    assert store.versions() == [] and store.verify() == []
    with pytest.raises(SuiteStoreError, match="no approved versions"):
        store.latest("support")
    _approve(store, _suite("1.0.0"))
    later = datetime(2026, 10, 18, tzinfo=timezone.utc)
    store.approve(_suite("1.1.0"), approved_by="qa", approved_at=later)
    assert [r.version for r in store.versions("support")] == ["1.0.0", "1.1.0"]
    assert store.versions("unknown") == []
    assert store.latest("support").version == "1.1.0"
    loaded = store.load_suite("support", "1.0.0")
    provenance = loaded.metadata[PROVENANCE_KEY]
    assert provenance["approved_by"] == "qa-lead"
    assert provenance["content_sha256"] == store.get("support", "1.0.0").content_sha256
    assert loaded.cases == _suite().cases


@pytest.mark.parametrize(
    ("ref", "expected"),
    [("support@1.0.0", ("support", "1.0.0")), ("a@b@c", ("a@b", "c"))],
)
def test_parse_ref(ref: str, expected: tuple[str, str]) -> None:
    assert parse_ref(ref) == expected


@pytest.mark.parametrize("ref", ["support", "@1", "support@"])
def test_parse_ref_rejects_bad_refs(ref: str) -> None:
    with pytest.raises(SuiteStoreError, match="NAME@VERSION"):
        parse_ref(ref)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (("approval", "approved_by"), "mallory"),
        (("approval", "notes"), "edited"),
        (("case_count",), 99),
        (("parent_version",), "0.0.1"),
    ],
)
def test_envelope_edits_are_detected(tmp_path: Path, field: tuple[str, ...], value: object) -> None:
    store = SuiteStore(tmp_path)
    record = _approve(store, _suite())
    assert record.record_sha256  # type: ignore[attr-defined]
    path = tmp_path / "support" / "1.0.0.json"
    data = json.loads(path.read_text("utf-8"))
    target = data
    for key in field[:-1]:
        target = target[key]
    target[field[-1]] = value
    path.write_text(json.dumps(data), "utf-8")
    with pytest.raises(IntegrityError, match="approval record changed"):
        store.get("support", "1.0.0")
    assert store.verify()[0].ok is False


def test_hash_matching_invalid_suite_is_an_integrity_error(tmp_path: Path) -> None:
    from agenticlens.suites import record_sha256

    store = SuiteStore(tmp_path)
    _approve(store, _suite())
    path = tmp_path / "support" / "1.0.0.json"
    data = json.loads(path.read_text("utf-8"))
    data["suite"]["cases"] = []
    data["content_sha256"] = content_sha256(data["suite"])
    data["record_sha256"] = record_sha256(data)
    path.write_text(json.dumps(data), "utf-8")
    with pytest.raises(IntegrityError, match="not a valid TestSuite"):
        store.get("support", "1.0.0")
    (result,) = store.verify()
    assert result.ok is False and "not a valid TestSuite" in (result.error or "")
