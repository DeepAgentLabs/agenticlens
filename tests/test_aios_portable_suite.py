"""Execute the full pinned AIOS suite without a sibling checkout or spec test imports."""

import json
from pathlib import Path

import pytest

from agenticlens.validation import resolve_provenance, validate_aios_artifact

ROOT = Path(__file__).parent / "fixtures/aios-v0.8"
SUITE_DIR = ROOT / "specification/v0.6/conformance-suite"
SUITE = json.loads((SUITE_DIR / "suite.json").read_text())


@pytest.mark.parametrize("case", SUITE["cases"], ids=lambda c: c["id"])
def test_portable_outcome(case):
    path = SUITE_DIR / case["path"]
    if case["expected"] == "unsupported":
        with pytest.raises(ValueError, match="AIOS-0.5-V03|Unsupported"):
            validate_aios_artifact(path, spec_root=ROOT)
        return
    report = validate_aios_artifact(path, spec_root=ROOT)
    outcome = (
        "schema-invalid"
        if not report.schema_valid
        else "semantic-invalid"
        if not report.semantic_valid
        else "valid"
    )
    assert outcome == case["expected"]
    assert sorted({i.rule_id for i in report.issues}) == case["rules"]


@pytest.mark.parametrize("case", SUITE["resolution_cases"], ids=lambda c: c["id"])
def test_portable_resolution(case):
    record = json.loads((SUITE_DIR / case["record"]).read_text())
    held = {key: (SUITE_DIR / path).read_bytes() for key, path in case["subjects"].items()}
    assert resolve_provenance(record, held, spec_root=ROOT) == case["expected"]


def test_schema_only_does_not_claim_semantic_alignment():
    report = validate_aios_artifact(
        SUITE_DIR / "cases/run-p12-unlinked-retry.json", mode="validate", spec_root=ROOT
    )
    assert report.schema_valid and not report.aligned and not report.semantic_checked


def test_packaged_families_are_available_without_workspace(tmp_path):
    from agenticlens.validation.aios import available_spec_versions

    assert available_spec_versions() == ["0.4", "0.6", "0.8"]
    assert available_spec_versions(tmp_path) == []


def test_long_valid_lineage_does_not_depend_on_python_recursion_limit():
    from agenticlens.validation.companions import cyclic

    assert not cyclic([(str(i), str(i + 1)) for i in range(3000)])
    assert cyclic([(str(i), str(i + 1)) for i in range(3000)] + [("3000", "0")])


def test_nonfinite_json_and_global_identity_are_rejected(tmp_path):
    document = json.loads((SUITE_DIR / "cases/operational-valid-signal.json").read_text())
    document["confidence"] = float("nan")
    path = tmp_path / "nan.json"
    path.write_text(json.dumps(document))
    report = validate_aios_artifact(path, spec_root=ROOT)
    assert not report.schema_valid and not report.aligned
    document = json.loads((SUITE_DIR / "cases/run-valid-advanced.json").read_text())
    document["requests"][0]["id"] = document["id"]
    path.write_text(json.dumps(document))
    report = validate_aios_artifact(path, spec_root=ROOT)
    assert "AIOS-0.4-P02" in report.summary.failed_rules
