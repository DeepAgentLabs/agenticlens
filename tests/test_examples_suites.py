"""The v0.6 suite-management example reproduces its committed store and artifacts,
and the committed approved suite runs through the CI path (verify, export,
evaluate, gate)."""

import json
import runpy
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from agenticlens.cli.main import app
from agenticlens.suites import SuiteStore

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "suites"
#: Wall-clock fields that legitimately differ between runs.
MEASURED = {"created_at"}


def _load(path: Path) -> Any:
    data = json.loads(path.read_text("utf-8"))
    return {k: v for k, v in data.items() if k not in MEASURED} if isinstance(data, dict) else data


def _outcomes(path: Path) -> Any:
    report = _load(path)
    return report["summary"], [(case["case_id"], case["passed"]) for case in report["cases"]]


def test_suite_management_demo_reproduces_store_and_artifacts(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXAMPLE.parent / "suite_management_demo.py"))
    result = module["main"](tmp_path)
    assert result["cases"] == result["passed"] == 15 and result["gate_passed"] is True

    stored = EXAMPLE / "store" / "support-regression" / "1.0.0.json"
    produced = tmp_path / "store" / "support-regression" / "1.0.0.json"
    assert produced.read_text("utf-8") == stored.read_text("utf-8")

    saved = EXAMPLE / "artifacts"
    for artifact in sorted(saved.iterdir()):
        mine = tmp_path / "artifacts" / artifact.name
        if artifact.name == "evaluation.json":
            # agentic-evals owns the report format; compare outcomes, not every field.
            assert _outcomes(mine) == _outcomes(artifact)
        elif artifact.suffix == ".json":
            assert _load(mine) == _load(artifact), artifact.name
        else:
            assert mine.read_text("utf-8") == artifact.read_text("utf-8"), artifact.name


def test_demo_rerun_is_idempotent(tmp_path: Path) -> None:
    module = runpy.run_path(str(EXAMPLE.parent / "suite_management_demo.py"))
    first = module["main"](tmp_path)
    assert module["main"](tmp_path) == first


def test_committed_store_runs_through_the_ci_path(tmp_path: Path) -> None:
    assert all(result.ok for result in SuiteStore(EXAMPLE / "store").verify())
    runner = CliRunner()
    suite = tmp_path / "suite.json"
    report = tmp_path / "evaluation.json"
    steps = [
        ["suite", "verify", "--store", str(EXAMPLE / "store")],
        [
            "suite",
            "export",
            "support-regression@1.0.0",
            "--store",
            str(EXAMPLE / "store"),
            "--save",
            str(suite),
        ],
        [
            "evaluate",
            str(suite),
            str(EXAMPLE / "artifacts" / "samples.json"),
            "--save",
            str(report),
            "--strict-evidence",
        ],
        ["gate", str(report), "--notify-state", str(tmp_path / "state.json")],
    ]
    for step in steps:
        result = runner.invoke(app, step)
        assert result.exit_code == 0, (step, result.output)
    evaluation = json.loads(report.read_text("utf-8"))
    assert evaluation["summary"]["passed_cases"] == 15
