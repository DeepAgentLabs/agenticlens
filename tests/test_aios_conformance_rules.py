"""Rule-cited AIOS conformance summaries, version routing, and CLI options."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.validation import (
    ISSUE_RULES,
    available_spec_versions,
    normalize_spec_version,
    validate_aios_artifact,
)

SPEC = Path(__file__).resolve().parent / "fixtures" / "ai-operations-spec"
EXAMPLES = SPEC / "specification" / "v0.4" / "examples"
CATALOG = SPEC / "specification" / "v0.4" / "conformance-rules.json"


def test_issue_rule_ids_exist_in_the_spec_catalog() -> None:
    catalog = {rule["id"] for rule in json.loads(CATALOG.read_text("utf-8"))["rules"]}
    assert set(ISSUE_RULES.values()) <= catalog


def test_valid_run_reports_per_rule_results() -> None:
    report = validate_aios_artifact(EXAMPLES / "valid" / "run.json", spec_root=SPEC)
    assert report.aligned and report.summary is not None
    assert report.summary.status == "aligned"
    assert report.declared_spec_version == "0.4-draft"
    results = {rule.rule_id: rule.result for rule in report.rules}
    assert results["AIOS-0.4-P01"] == "pass"
    assert results["AIOS-0.4-P02"] == "pass"
    assert results["AIOS-0.4-C01"] == "not_checked"  # process rule
    assert report.summary.rules_failed == 0 and report.summary.rules_not_checked > 0


def test_semantic_issue_cites_its_rule() -> None:
    report = validate_aios_artifact(
        EXAMPLES / "semantic-invalid" / "dangling-reference.json", spec_root=SPEC
    )
    assert not report.aligned and report.summary is not None
    assert report.summary.status == "semantic_invalid"
    assert all(issue.rule_id for issue in report.issues)
    assert "AIOS-0.4-P05" in report.summary.failed_rules


def test_schema_invalid_marks_semantic_rules_not_checked() -> None:
    report = validate_aios_artifact(
        EXAMPLES / "invalid" / "workflow-missing-name.json", spec_root=SPEC
    )
    assert report.summary is not None and report.summary.status == "schema_invalid"
    results = {rule.rule_id: rule.result for rule in report.rules}
    assert results["AIOS-0.4-P01"] == "fail"


def test_validate_mode_status() -> None:
    report = validate_aios_artifact(
        EXAMPLES / "valid" / "run.json", spec_root=SPEC, mode="validate"
    )
    assert report.summary is not None and report.summary.status == "schema_valid"


def test_spec_version_normalization_and_routing(tmp_path: Path) -> None:
    assert normalize_spec_version("0.4-draft") == "0.4"
    assert normalize_spec_version("v0.4") == "0.4"
    with pytest.raises(ValueError, match="Malformed"):
        normalize_spec_version("latest")
    with pytest.raises(ValueError, match="Unsupported AIOS version"):
        validate_aios_artifact(
            EXAMPLES / "valid" / "workflow.json", spec_root=SPEC, spec_version="0.5"
        )
    newer = tmp_path / "run.json"
    payload = json.loads((EXAMPLES / "valid" / "run.json").read_text("utf-8"))
    payload["spec_version"] = "0.6-draft"
    newer.write_text(json.dumps(payload), "utf-8")
    with pytest.raises(ValueError, match="AIOS-0.5-V03"):
        validate_aios_artifact(newer, spec_root=SPEC)
    assert available_spec_versions(SPEC) == ["0.4"]
    assert available_spec_versions(tmp_path) in ([], ["0.4"])  # sibling checkout may exist


def test_conformance_cli_json_and_list_versions() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["conformance", str(EXAMPLES / "valid" / "run.json"), "--spec-root", str(SPEC), "--json"],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["summary"]["status"] == "aligned"
    listed = runner.invoke(app, ["conformance", "--list-versions", "--spec-root", str(SPEC)])
    assert listed.exit_code == 0 and "v0.4-draft: schemas found" in listed.output
    assert runner.invoke(app, ["conformance"]).exit_code == 1
    table = runner.invoke(
        app,
        [
            "conformance",
            str(EXAMPLES / "semantic-invalid" / "dangling-reference.json"),
            "--spec-root",
            str(SPEC),
        ],
    )
    assert table.exit_code == 2 and "[AIOS-0.4-P05]" in table.output
